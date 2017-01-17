from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from yawn.workflow.serializers import WorkflowSerializer, WorkflowNameSerializer
from yawn.workflow.models import Workflow, WorkflowName


class WorkflowNameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    WorkflowName endpoint. Provides the name, current version number,
    current_version_id, and the select_version_id if a version was
    requested in the query string.

    Used to list the workflows and power version switcher.
    """
    queryset = WorkflowName.objects.select_related('current_version').annotate(
        task_count=Count('current_version__template'))

    serializer_class = WorkflowNameSerializer
    permission_classes = (AllowAny,)


class WorkflowViewSet(viewsets.GenericViewSet,
                      viewsets.mixins.ListModelMixin,
                      viewsets.mixins.RetrieveModelMixin,
                      viewsets.mixins.UpdateModelMixin,
                      viewsets.mixins.CreateModelMixin):
    """
    Workflow endpoint.

    The POST action is unusual as it checks for an existing, identical
    workflow and return it if found instead of creating a new object.
    """
    queryset = Workflow.objects.select_related('name')

    serializer_class = WorkflowSerializer
    permission_classes = (AllowAny,)
