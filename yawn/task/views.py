from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from yawn.task.models import Task, Execution
from yawn.task.serializers import RunSerializer, TaskDetailSerializer, ExecutionListSerializer
from yawn.workflow.models import Run


class RunViewSet(viewsets.GenericViewSet,
                 viewsets.mixins.ListModelMixin,
                 viewsets.mixins.RetrieveModelMixin,
                 viewsets.mixins.UpdateModelMixin):
    """
    Run endpoint, only GET(list,detail) and PATCH(detail)
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


class TaskViewSet(viewsets.GenericViewSet,
                  viewsets.mixins.RetrieveModelMixin,
                  viewsets.mixins.UpdateModelMixin):
    """
    GET a task, and its executions. PATCH to re-run or terminate.
    """
    queryset = Task.objects.all().prefetch_related(
        'execution_set__worker').select_related('template__workflow__name')

    serializer_class = TaskDetailSerializer

    permission_classes = (AllowAny,)


class ExecutionViewSet(viewsets.GenericViewSet,
                       viewsets.mixins.ListModelMixin):
    """
    GET a list of Executions
    """
    queryset = Execution.objects.all().select_related(
        'worker', 'task__template__workflow__name')

    serializer_class = ExecutionListSerializer

    permission_classes = (AllowAny,)
