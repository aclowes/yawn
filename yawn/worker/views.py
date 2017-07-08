from django.db.models import Count
from rest_framework import viewsets

from yawn.worker.models import Worker, Queue
from yawn.worker.serializers import WorkerSerializer, QueueSerializer


class WorkerViewSet(viewsets.GenericViewSet,
                    viewsets.mixins.ListModelMixin,
                    viewsets.mixins.RetrieveModelMixin):
    """
    Worker endpoint, GET(list)
    """
    queryset = Worker.objects.all().order_by('-id')

    serializer_class = WorkerSerializer


class QueueViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.ListModelMixin,
                   viewsets.mixins.RetrieveModelMixin,
                   viewsets.mixins.UpdateModelMixin):
    """
    Queue endpoint GET(list,detail), PATCH to clear all messages
    """
    queryset = Queue.objects.all().annotate(Count('message')).order_by('id')

    serializer_class = QueueSerializer
