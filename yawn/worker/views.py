from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from yawn.worker.models import Worker, Queue, Message
from yawn.worker.serializers import WorkerSerializer, QueueSerializer


class WorkerViewSet(viewsets.GenericViewSet,
                    viewsets.mixins.ListModelMixin,
                    viewsets.mixins.UpdateModelMixin):
    """
    Worker endpoint, GET(list) and PATCH to terminate
    """
    queryset = Worker.objects.all()

    serializer_class = WorkerSerializer

    permission_classes = (AllowAny,)


class QueueViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.ListModelMixin,
                   viewsets.mixins.RetrieveModelMixin,
                   viewsets.mixins.UpdateModelMixin):
    """
    Queue endpoint GET(list,detail), PATCH to clear all messages
    """
    queryset = Queue.objects.all().annotate(Count('message'))

    serializer_class = QueueSerializer

    permission_classes = (AllowAny,)
