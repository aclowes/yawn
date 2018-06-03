from rest_framework import viewsets

from yawn.task.models import Task, Execution
from yawn.task.serializers import TaskDetailSerializer, ExecutionListSerializer


class TaskViewSet(viewsets.GenericViewSet,
                  viewsets.mixins.RetrieveModelMixin,
                  viewsets.mixins.UpdateModelMixin):
    """
    GET a task, and its executions. PATCH to re-run or terminate.
    """
    queryset = Task.objects.all().order_by('id').prefetch_related(
        'execution_set__worker').select_related('template__workflow__name')

    serializer_class = TaskDetailSerializer


class ExecutionViewSet(viewsets.GenericViewSet,
                       viewsets.mixins.ListModelMixin):
    """
    GET a list of Executions
    """
    queryset = Execution.objects.all().order_by('-id').select_related(
        'worker', 'task__template__workflow__name')

    serializer_class = ExecutionListSerializer

    def get_queryset(self):
        """
        Optionally filter to the executions for a given worker
        """
        queryset = self.queryset
        worker = self.request.query_params.get('worker')
        if worker is not None:
            # worker page filters and reverses the order
            queryset = queryset.filter(worker_id=worker)
        return queryset
