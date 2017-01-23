from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from yawn.workflow.serializers import WorkflowSerializer, WorkflowNameSerializer, RunSerializer
from yawn.workflow.models import Workflow, WorkflowName, Run


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


class RunViewSet(viewsets.GenericViewSet,
                 viewsets.mixins.ListModelMixin,
                 viewsets.mixins.RetrieveModelMixin,
                 viewsets.mixins.CreateModelMixin,
                 viewsets.mixins.UpdateModelMixin):
    """
    Run endpoint: GET(list,detail), POST(list) and PATCH(detail)
    """

    serializer_class = RunSerializer
    permission_classes = (AllowAny,)
    queryset = Run.objects.prefetch_related('task_set__template')

    def get_queryset(self):
        """
        Optionally filter to the runs for a given workflow
        """
        queryset = self.queryset.all()
        workflow = self.request.query_params.get('workflow', None)
        if workflow is not None:
            queryset = queryset.filter(workflow_id=workflow)
        return queryset
