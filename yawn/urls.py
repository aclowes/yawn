from django.conf.urls import include, url
from rest_framework import routers

from yawn.task.views import TaskViewSet, ExecutionViewSet
from yawn.worker.views import QueueViewSet, WorkerViewSet
from yawn.workflow.views import WorkflowViewSet, WorkflowNameViewSet, RunViewSet
from yawn.user.views import UserViewSet

router = routers.DefaultRouter()
router.include_format_suffixes = False
router.register(r'names', WorkflowNameViewSet)
router.register(r'workflows', WorkflowViewSet)
router.register(r'runs', RunViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'queues', QueueViewSet)
router.register(r'workers', WorkerViewSet)
router.register(r'executions', ExecutionViewSet)
router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls'))
]
