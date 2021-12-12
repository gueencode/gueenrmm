import datetime as dt
import re
import uuid

import pytz
from django.shortcuts import get_object_or_404
from django.utils import timezone as djangotime
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

from agents.models import Agent
from core.models import CoreSettings
from gueenrmm.utils import notify_error
from gueenrmm.permissions import _has_perm_on_client, _has_perm_on_site

from .models import Client, ClientCustomField, Deployment, Site, SiteCustomField
from .permissions import (
    ClientsPerms,
    DeploymentPerms,
    SitesPerms,
)
from .serializers import (
    ClientCustomFieldSerializer,
    ClientSerializer,
    DeploymentSerializer,
    SiteCustomFieldSerializer,
    SiteSerializer,
)


class GetAddClients(APIView):
    permission_classes = [IsAuthenticated, ClientsPerms]

    def get(self, request):
        clients = Client.objects.select_related(
            "workstation_policy", "server_policy", "alert_template"
        ).filter_by_role(request.user)
        return Response(
            ClientSerializer(clients, context={"user": request.user}, many=True).data
        )

    def post(self, request):
        # create client
        client_serializer = ClientSerializer(data=request.data["client"])
        client_serializer.is_valid(raise_exception=True)
        client = client_serializer.save()

        # create site
        site_serializer = SiteSerializer(
            data={"client": client.id, "name": request.data["site"]["name"]}
        )

        # make sure site serializer doesn't return errors and save
        if site_serializer.is_valid():
            site_serializer.save()
        else:
            # delete client since site serializer was invalid
            client.delete()
            site_serializer.is_valid(raise_exception=True)

        if "initialsetup" in request.data.keys():
            core = CoreSettings.objects.first()
            core.default_time_zone = request.data["timezone"]
            core.save(update_fields=["default_time_zone"])

        # save custom fields
        if "custom_fields" in request.data.keys():
            for field in request.data["custom_fields"]:

                custom_field = field
                custom_field["client"] = client.id

                serializer = ClientCustomFieldSerializer(data=custom_field)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        # add user to allowed clients in role if restricted user created the client
        if request.user.role and request.user.role.can_view_clients.exists():
            request.user.role.can_view_clients.add(client)

        return Response(f"{client.name} was added")


class GetUpdateDeleteClient(APIView):
    permission_classes = [IsAuthenticated, ClientsPerms]

    def get(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        return Response(ClientSerializer(client, context={"user": request.user}).data)

    def put(self, request, pk):
        client = get_object_or_404(Client, pk=pk)

        serializer = ClientSerializer(
            data=request.data["client"], instance=client, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # update custom fields
        if "custom_fields" in request.data.keys():
            for field in request.data["custom_fields"]:

                custom_field = field
                custom_field["client"] = pk

                if ClientCustomField.objects.filter(field=field["field"], client=pk):
                    value = ClientCustomField.objects.get(
                        field=field["field"], client=pk
                    )
                    serializer = ClientCustomFieldSerializer(
                        instance=value, data=custom_field
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    serializer = ClientCustomFieldSerializer(data=custom_field)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

        return Response("{client} was updated")

    def delete(self, request, pk):
        from automation.tasks import generate_agent_checks_task

        client = get_object_or_404(Client, pk=pk)

        # only run tasks if it affects clients
        if client.agent_count > 0 and "move_to_site" in request.query_params.keys():
            agents = Agent.objects.filter(site__client=client)
            site = get_object_or_404(Site, pk=request.query_params["move_to_site"])
            agents.update(site=site)
            generate_agent_checks_task.delay(all=True, create_tasks=True)

        elif client.agent_count > 0:
            return notify_error(
                "Agents exist under this client. There needs to be a site specified to move existing agents to"
            )

        client.delete()
        return Response(f"{client.name} was deleted")


class GetAddSites(APIView):
    permission_classes = [IsAuthenticated, SitesPerms]

    def get(self, request):
        sites = Site.objects.filter_by_role(request.user)
        return Response(SiteSerializer(sites, many=True).data)

    def post(self, request):

        if not _has_perm_on_client(request.user, request.data["site"]["client"]):
            raise PermissionDenied()

        serializer = SiteSerializer(data=request.data["site"])
        serializer.is_valid(raise_exception=True)
        site = serializer.save()

        # save custom fields
        if "custom_fields" in request.data.keys():

            for field in request.data["custom_fields"]:

                custom_field = field
                custom_field["site"] = site.id

                serializer = SiteCustomFieldSerializer(data=custom_field)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        # add user to allowed sites in role if restricted user created the client
        if request.user.role and request.user.role.can_view_sites.exists():
            request.user.role.can_view_sites.add(site)

        return Response(f"Site {site.name} was added!")


class GetUpdateDeleteSite(APIView):
    permission_classes = [IsAuthenticated, SitesPerms]

    def get(self, request, pk):
        site = get_object_or_404(Site, pk=pk)
        return Response(SiteSerializer(site).data)

    def put(self, request, pk):
        site = get_object_or_404(Site, pk=pk)

        if "client" in request.data["site"].keys() and (
            site.client.id != request.data["site"]["client"]
            and site.client.sites.count() == 1
        ):
            return notify_error("A client must have at least one site")

        serializer = SiteSerializer(
            instance=site, data=request.data["site"], partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # update custom field
        if "custom_fields" in request.data.keys():

            for field in request.data["custom_fields"]:

                custom_field = field
                custom_field["site"] = pk

                if SiteCustomField.objects.filter(field=field["field"], site=pk):
                    value = SiteCustomField.objects.get(field=field["field"], site=pk)
                    serializer = SiteCustomFieldSerializer(
                        instance=value, data=custom_field, partial=True
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    serializer = SiteCustomFieldSerializer(data=custom_field)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

        return Response("Site was edited")

    def delete(self, request, pk):
        from automation.tasks import generate_agent_checks_task

        site = get_object_or_404(Site, pk=pk)
        if site.client.sites.count() == 1:
            return notify_error("A client must have at least 1 site.")

        # only run tasks if it affects clients
        if site.agent_count > 0 and "move_to_site" in request.query_params.keys():
            agents = Agent.objects.filter(site=site)
            new_site = get_object_or_404(Site, pk=request.query_params["move_to_site"])
            agents.update(site=new_site)
            generate_agent_checks_task.delay(all=True, create_tasks=True)

        elif site.agent_count > 0:
            return notify_error(
                "There needs to be a site specified to move the agents to"
            )

        site.delete()
        return Response(f"{site.name} was deleted")


class AgentDeployment(APIView):
    permission_classes = [IsAuthenticated, DeploymentPerms]

    def get(self, request):
        deps = Deployment.objects.filter_by_role(request.user)
        return Response(DeploymentSerializer(deps, many=True).data)

    def post(self, request):
        from knox.models import AuthToken
        from accounts.models import User

        site = get_object_or_404(Site, pk=request.data["site"])

        if not _has_perm_on_site(request.user, site.pk):
            raise PermissionDenied()

        installer_user = User.objects.filter(is_installer_user=True).first()

        expires = dt.datetime.strptime(
            request.data["expires"], "%Y-%m-%d %H:%M"
        ).astimezone(pytz.timezone("UTC"))
        now = djangotime.now()
        delta = expires - now
        obj, token = AuthToken.objects.create(user=installer_user, expiry=delta)

        flags = {
            "power": request.data["power"],
            "ping": request.data["ping"],
            "rdp": request.data["rdp"],
        }

        Deployment(
            site=site,
            expiry=expires,
            mon_type=request.data["agenttype"],
            arch=request.data["arch"],
            auth_token=obj,
            token_key=token,
            install_flags=flags,
        ).save()
        return Response("The deployment was added successfully")

    def delete(self, request, pk):
        d = get_object_or_404(Deployment, pk=pk)

        if not _has_perm_on_site(request.user, d.site.pk):
            raise PermissionDenied()

        try:
            d.auth_token.delete()
        except:
            pass

        d.delete()
        return Response("The deployment was deleted")


class GenerateAgent(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, uid):
        from gueenrmm.utils import generate_winagent_exe

        try:
            _ = uuid.UUID(uid, version=4)
        except ValueError:
            return notify_error("invalid")

        d = get_object_or_404(Deployment, uid=uid)

        client = d.client.name.replace(" ", "").lower()
        site = d.site.name.replace(" ", "").lower()
        client = re.sub(r"([^a-zA-Z0-9]+)", "", client)
        site = re.sub(r"([^a-zA-Z0-9]+)", "", site)
        ext = ".exe" if d.arch == "64" else "-x86.exe"
        file_name = f"rmm-{client}-{site}-{d.mon_type}{ext}"

        return generate_winagent_exe(
            client=d.client.pk,
            site=d.site.pk,
            agent_type=d.mon_type,
            rdp=d.install_flags["rdp"],
            ping=d.install_flags["ping"],
            power=d.install_flags["power"],
            arch=d.arch,
            token=d.token_key,
            api=f"https://{request.get_host()}",
            file_name=file_name,
        )
