from django.db.models import Max
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from yawn.workflow.serializers import WorkflowSerializer
from yawn.workflow.models import Workflow, WorkflowName


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
    queryset = Workflow.objects.filter(
        id__in=WorkflowName.objects.all().annotate(Max('workflow__version'))
    ).select_related('name')

    serializer_class = WorkflowSerializer

    permission_classes = (AllowAny,)
