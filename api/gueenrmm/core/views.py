import os
import re

from django.conf import settings
from django.shortcuts import get_object_or_404
from logs.models import AuditLog
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from gueenrmm.utils import notify_error
from gueenrmm.permissions import (
    _has_perm_on_client,
    _has_perm_on_agent,
    _has_perm_on_site,
)

from .models import CodeSignToken, CoreSettings, CustomField, GlobalKVStore, URLAction
from .permissions import (
    CodeSignPerms,
    CoreSettingsPerms,
    ServerMaintPerms,
    URLActionPerms,
    CustomFieldPerms,
)
from .serializers import (
    CodeSignTokenSerializer,
    CoreSettingsSerializer,
    CustomFieldSerializer,
    KeyStoreSerializer,
    URLActionSerializer,
)


class UploadMeshAgent(APIView):
    permission_classes = [IsAuthenticated, CoreSettingsPerms]
    parser_class = (FileUploadParser,)

    def put(self, request, format=None):
        if "meshagent" not in request.data and "arch" not in request.data:
            raise ParseError("Empty content")

        arch = request.data["arch"]
        f = request.data["meshagent"]
        mesh_exe = os.path.join(
            settings.EXE_DIR, "meshagent.exe" if arch == "64" else "meshagent-x86.exe"
        )
        with open(mesh_exe, "wb+") as j:
            for chunk in f.chunks():
                j.write(chunk)

        return Response(
            "Mesh Agent uploaded successfully", status=status.HTTP_201_CREATED
        )


class GetEditCoreSettings(APIView):
    permission_classes = [IsAuthenticated, CoreSettingsPerms]

    def get(self, request):
        settings = CoreSettings.objects.first()
        return Response(CoreSettingsSerializer(settings).data)

    def put(self, request):
        coresettings = CoreSettings.objects.first()
        serializer = CoreSettingsSerializer(instance=coresettings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")


@api_view()
def version(request):
    return Response(settings.APP_VER)


@api_view()
def dashboard_info(request):
    from gueenrmm.utils import get_latest_grmm_ver

    return Response(
        {
            "grmm_version": settings.grmm_VERSION,
            "latest_grmm_ver": get_latest_grmm_ver(),
            "dark_mode": request.user.dark_mode,
            "show_community_scripts": request.user.show_community_scripts,
            "dbl_click_action": request.user.agent_dblclick_action,
            "default_agent_tbl_tab": request.user.default_agent_tbl_tab,
            "url_action": request.user.url_action.id
            if request.user.url_action
            else None,
            "client_tree_sort": request.user.client_tree_sort,
            "client_tree_splitter": request.user.client_tree_splitter,
            "loading_bar_color": request.user.loading_bar_color,
            "clear_search_when_switching": request.user.clear_search_when_switching,
            "hosted": getattr(settings, "HOSTED", False),
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, CoreSettingsPerms])
def email_test(request):
    core = CoreSettings.objects.first()
    r = core.send_mail(
        subject="Test from Gueen RMM", body="This is a test message", test=True
    )

    if not isinstance(r, bool) and isinstance(r, str):
        return notify_error(r)

    return Response("Email Test OK!")


@api_view(["POST"])
@permission_classes([IsAuthenticated, ServerMaintPerms])
def server_maintenance(request):
    from gueenrmm.utils import reload_nats

    if "action" not in request.data:
        return notify_error("The data is incorrect")

    if request.data["action"] == "reload_nats":
        reload_nats()
        return Response("Nats configuration was reloaded successfully.")

    if request.data["action"] == "rm_orphaned_tasks":
        from agents.models import Agent
        from autotasks.tasks import remove_orphaned_win_tasks

        agents = Agent.objects.only("pk", "last_seen", "overdue_time", "offline_time")
        online = [i for i in agents if i.status == "online"]
        for agent in online:
            remove_orphaned_win_tasks.delay(agent.pk)

        return Response(
            "The task has been initiated. Check the Debug Log in the UI for progress."
        )

    if request.data["action"] == "prune_db":
        from logs.models import AuditLog, PendingAction

        if "prune_tables" not in request.data:
            return notify_error("The data is incorrect.")

        tables = request.data["prune_tables"]
        records_count = 0
        if "audit_logs" in tables:
            auditlogs = AuditLog.objects.filter(action="check_run")
            records_count += auditlogs.count()
            auditlogs.delete()

        if "pending_actions" in tables:
            pendingactions = PendingAction.objects.filter(status="completed")
            records_count += pendingactions.count()
            pendingactions.delete()

        if "alerts" in tables:
            from alerts.models import Alert

            alerts = Alert.objects.all()
            records_count += alerts.count()
            alerts.delete()

        return Response(f"{records_count} records were pruned from the database")

    return notify_error("The data is incorrect")


class GetAddCustomFields(APIView):
    permission_classes = [IsAuthenticated, CustomFieldPerms]

    def get(self, request):
        if "model" in request.query_params.keys():
            fields = CustomField.objects.filter(model=request.query_params["model"])
        else:
            fields = CustomField.objects.all()
        return Response(CustomFieldSerializer(fields, many=True).data)

    def patch(self, request):
        if "model" in request.data.keys():
            fields = CustomField.objects.filter(model=request.data["model"])
            return Response(CustomFieldSerializer(fields, many=True).data)
        else:
            return notify_error("The request was invalid")

    def post(self, request):
        serializer = CustomFieldSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")


class GetUpdateDeleteCustomFields(APIView):
    permission_classes = [IsAuthenticated, CustomFieldPerms]

    def get(self, request, pk):
        custom_field = get_object_or_404(CustomField, pk=pk)

        return Response(CustomFieldSerializer(custom_field).data)

    def put(self, request, pk):
        custom_field = get_object_or_404(CustomField, pk=pk)

        serializer = CustomFieldSerializer(
            instance=custom_field, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")

    def delete(self, request, pk):
        get_object_or_404(CustomField, pk=pk).delete()

        return Response("ok")


class CodeSign(APIView):
    permission_classes = [IsAuthenticated, CodeSignPerms]

    def get(self, request):
        token = CodeSignToken.objects.first()
        return Response(CodeSignTokenSerializer(token).data)

    def patch(self, request):
        import requests

        errors = []
        for url in settings.EXE_GEN_URLS:
            try:
                r = requests.post(
                    f"{url}/api/v1/checktoken",
                    json={"token": request.data["token"]},
                    headers={"Content-type": "application/json"},
                    timeout=15,
                )
            except Exception as e:
                errors.append(str(e))
            else:
                errors = []
                break

        if errors:
            return notify_error(", ".join(errors))

        if r.status_code == 400 or r.status_code == 401:  # type: ignore
            return notify_error(r.json()["ret"])  # type: ignore
        elif r.status_code == 200:  # type: ignore
            t = CodeSignToken.objects.first()
            if t is None:
                CodeSignToken.objects.create(token=request.data["token"])
            else:
                serializer = CodeSignTokenSerializer(instance=t, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            return Response("Token was saved")

        try:
            ret = r.json()["ret"]  # type: ignore
        except:
            ret = "Something went wrong"
        return notify_error(ret)

    def post(self, request):
        from agents.models import Agent
        from agents.tasks import force_code_sign

        err = "A valid token must be saved first"
        try:
            t = CodeSignToken.objects.first().token
        except:
            return notify_error(err)

        if t is None or t == "":
            return notify_error(err)

        agent_ids: list[str] = list(
            Agent.objects.only("pk", "agent_id").values_list("agent_id", flat=True)
        )
        force_code_sign.delay(agent_ids=agent_ids)
        return Response("Agents will be code signed shortly")


class GetAddKeyStore(APIView):
    permission_classes = [IsAuthenticated, CoreSettingsPerms]

    def get(self, request):
        keys = GlobalKVStore.objects.all()
        return Response(KeyStoreSerializer(keys, many=True).data)

    def post(self, request):
        serializer = KeyStoreSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")


class UpdateDeleteKeyStore(APIView):
    permission_classes = [IsAuthenticated, CoreSettingsPerms]

    def put(self, request, pk):
        key = get_object_or_404(GlobalKVStore, pk=pk)

        serializer = KeyStoreSerializer(instance=key, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")

    def delete(self, request, pk):
        get_object_or_404(GlobalKVStore, pk=pk).delete()

        return Response("ok")


class GetAddURLAction(APIView):
    permission_classes = [IsAuthenticated, CoreSettingsPerms]

    def get(self, request):
        actions = URLAction.objects.all()
        return Response(URLActionSerializer(actions, many=True).data)

    def post(self, request):
        serializer = URLActionSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")


class UpdateDeleteURLAction(APIView):
    permission_classes = [IsAuthenticated, CoreSettingsPerms]

    def put(self, request, pk):
        action = get_object_or_404(URLAction, pk=pk)

        serializer = URLActionSerializer(
            instance=action, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")

    def delete(self, request, pk):
        get_object_or_404(URLAction, pk=pk).delete()

        return Response("ok")


class RunURLAction(APIView):
    permission_classes = [IsAuthenticated, URLActionPerms]

    def patch(self, request):
        from requests.utils import requote_uri

        from agents.models import Agent
        from clients.models import Client, Site
        from gueenrmm.utils import replace_db_values

        if "agent_id" in request.data.keys():
            if not _has_perm_on_agent(request.user, request.data["agent_id"]):
                raise PermissionDenied()

            instance = get_object_or_404(Agent, agent_id=request.data["agent_id"])
        elif "site" in request.data.keys():
            if not _has_perm_on_site(request.user, request.data["site"]):
                raise PermissionDenied()

            instance = get_object_or_404(Site, pk=request.data["site"])
        elif "client" in request.data.keys():
            if not _has_perm_on_client(request.user, request.data["client"]):
                raise PermissionDenied()

            instance = get_object_or_404(Client, pk=request.data["client"])
        else:
            return notify_error("received an incorrect request")

        action = get_object_or_404(URLAction, pk=request.data["action"])

        pattern = re.compile("\\{\\{([\\w\\s]+\\.[\\w\\s]+)\\}\\}")

        url_pattern = action.pattern

        for string in re.findall(pattern, action.pattern):
            value = replace_db_values(string=string, instance=instance, quotes=False)

            url_pattern = re.sub("\\{\\{" + string + "\\}\\}", str(value), url_pattern)

        AuditLog.audit_url_action(
            username=request.user.username,
            urlaction=action,
            instance=instance,
            debug_info={"ip": request._client_ip},
        )

        return Response(requote_uri(url_pattern))


class TwilioSMSTest(APIView):
    permission_classes = [IsAuthenticated, CoreSettingsPerms]

    def post(self, request):

        core = CoreSettings.objects.first()
        if not core.sms_is_configured:
            return notify_error(
                "All fields are required, including at least 1 recipient"
            )

        r = core.send_sms("gueenrmm Test SMS", test=True)

        if not isinstance(r, bool) and isinstance(r, str):
            return notify_error(r)

        return Response("SMS Test sent successfully!")
