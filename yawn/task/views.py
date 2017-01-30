from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from yawn.task.models import Task, Execution
from yawn.task.serializers import TaskDetailSerializer, ExecutionListSerializer


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

    def get_queryset(self):
        """
        Optionally filter to the executions for a given worker
        """
        queryset = self.queryset.all()
        worker = self.request.query_params.get('worker', None)
        if worker is not None:
            queryset = queryset.filter(worker_id=worker)
        return queryset.order_by('-id')
