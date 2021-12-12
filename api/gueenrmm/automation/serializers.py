from rest_framework.serializers import (
    ModelSerializer,
    ReadOnlyField,
    SerializerMethodField,
)

from agents.serializers import AgentHostnameSerializer
from autotasks.models import AutomatedTask
from checks.models import Check
from clients.models import Client
from clients.serializers import ClientMinimumSerializer, SiteMinimumSerializer
from winupdate.serializers import WinUpdatePolicySerializer

from .models import Policy


class PolicySerializer(ModelSerializer):
    class Meta:
        model = Policy
        fields = "__all__"


class PolicyTableSerializer(ModelSerializer):
    default_server_policy = ReadOnlyField(source="is_default_server_policy")
    default_workstation_policy = ReadOnlyField(source="is_default_workstation_policy")
    agents_count = SerializerMethodField(read_only=True)
    winupdatepolicy = WinUpdatePolicySerializer(many=True, read_only=True)
    alert_template = ReadOnlyField(source="alert_template.id")

    class Meta:
        model = Policy
        fields = "__all__"

    def get_agents_count(self, policy):
        return policy.related_agents().count()


class PolicyRelatedSerializer(ModelSerializer):
    workstation_clients = SerializerMethodField()
    server_clients = SerializerMethodField()
    workstation_sites = SerializerMethodField()
    server_sites = SerializerMethodField()
    agents = SerializerMethodField()

    def get_agents(self, policy):
        return AgentHostnameSerializer(
            policy.agents.filter_by_role(self.context["user"]).only(
                "agent_id", "hostname"
            ),
            many=True,
        ).data

    def get_workstation_clients(self, policy):
        return ClientMinimumSerializer(
            policy.workstation_clients.filter_by_role(self.context["user"]), many=True
        ).data

    def get_server_clients(self, policy):
        return ClientMinimumSerializer(
            policy.server_clients.filter_by_role(self.context["user"]), many=True
        ).data

    def get_workstation_sites(self, policy):
        return SiteMinimumSerializer(
            policy.workstation_sites.filter_by_role(self.context["user"]), many=True
        ).data

    def get_server_sites(self, policy):
        return SiteMinimumSerializer(
            policy.server_sites.filter_by_role(self.context["user"]), many=True
        ).data

    class Meta:
        model = Policy
        fields = (
            "pk",
            "name",
            "workstation_clients",
            "workstation_sites",
            "server_clients",
            "server_sites",
            "agents",
            "is_default_server_policy",
            "is_default_workstation_policy",
        )


class PolicyOverviewSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = ("pk", "name", "sites", "workstation_policy", "server_policy")
        depth = 2


class PolicyCheckStatusSerializer(ModelSerializer):
    hostname = ReadOnlyField(source="agent.hostname")

    class Meta:
        model = Check
        fields = "__all__"


class PolicyTaskStatusSerializer(ModelSerializer):
    hostname = ReadOnlyField(source="agent.hostname")

    class Meta:
        model = AutomatedTask
        fields = "__all__"


class PolicyAuditSerializer(ModelSerializer):
    class Meta:
        model = Policy
        fields = "__all__"
