from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from yawn.workflow.serializers import WorkflowSerializer
from yawn.workflow.models import Workflow


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

    def get_queryset(self):
        queryset = self.queryset.all()

        # in the list view, only show the latest versions
        if self.request.method == 'GET':
            queryset = queryset.exclude(is_current=None)

        return queryset
