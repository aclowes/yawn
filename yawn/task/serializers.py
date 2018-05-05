from rest_framework import serializers

from yawn.task.models import Task, Execution
from yawn.worker.serializers import MessageSerializer, WorkerSerializer
from yawn.workflow.models import Workflow


class SimpleWorkflowSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name.name', read_only=True)

    class Meta:
        model = Workflow
        fields = ('id', 'name', 'version')


class TaskSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='template.name', read_only=True)
    workflow = SimpleWorkflowSerializer(source='template.workflow', read_only=True)

    class Meta:
        model = Task
        exclude = ('run', 'template')


class ExecutionDetailSerializer(serializers.ModelSerializer):
    worker = WorkerSerializer(read_only=True)

    class Meta:
        model = Execution
        exclude = ('task',)


class ExecutionListSerializer(serializers.ModelSerializer):
    worker = WorkerSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    minutes_running = serializers.SerializerMethodField()

    class Meta:
        model = Execution
        fields = ('id', 'task', 'worker', 'status', 'start_timestamp', 'minutes_running')

    def get_minutes_running(self, obj):
        if obj.stop_timestamp:
            runtime = (obj.stop_timestamp - obj.start_timestamp).total_seconds()
            return '{:.0f}m {:.2f}s'.format(runtime // 60, runtime % 60)


class TaskDetailSerializer(TaskSerializer):
    executions = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, source='message_set', read_only=True)

    max_retries = serializers.IntegerField(source='template.max_retries')
    timeout = serializers.IntegerField(source='template.timeout')
    command = serializers.CharField(source='template.command')

    # actions
    terminate = serializers.IntegerField(write_only=True)
    enqueue = serializers.BooleanField(write_only=True)

    def get_executions(self, instance):
        executions = instance.execution_set.order_by('id')
        return ExecutionDetailSerializer(executions, many=True).data

    def update(self, instance, validated_data):
        if validated_data.get('terminate'):
            instance.execution_set.filter(
                id=validated_data['terminate'], status=Execution.RUNNING
            ).update(status=Execution.KILLED)
        if validated_data.get('enqueue'):
            instance.enqueue()
        return instance
