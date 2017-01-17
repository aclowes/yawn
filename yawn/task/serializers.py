from rest_framework import serializers

from yawn.task.models import Task, Execution, Template
from yawn.worker.serializers import MessageSerializer, WorkerSerializer
from yawn.workflow.models import Workflow, Run


class SimpleWorkflowSerializer(serializers.ModelSerializer):
    name = serializers.SlugField(source='name.name', read_only=True)

    class Meta:
        model = Workflow
        fields = ('id', 'name', 'version')


class TaskSerializer(serializers.ModelSerializer):
    name = serializers.SlugField(source='template.name', read_only=True)
    workflow = SimpleWorkflowSerializer(source='template.workflow', read_only=True)

    class Meta:
        model = Task
        exclude = ('run', 'template')


class RunSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, source='task_set', read_only=True)
    workflow = serializers.HyperlinkedRelatedField(view_name='workflow-detail', read_only=True)

    class Meta:
        model = Run
        fields = '__all__'
        read_only_fields = ('submitted_time', 'scheduled_time')


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
            return (obj.stop_timestamp - obj.start_timestamp).minutes


class TaskDetailSerializer(TaskSerializer):
    executions = ExecutionDetailSerializer(many=True, source='execution_set', read_only=True)
    messages = MessageSerializer(many=True, source='message_set', read_only=True)

    max_retries = serializers.IntegerField(source='template.max_retries')
    timeout = serializers.IntegerField(source='template.timeout')
    command = serializers.ListField(source='template.command', child=serializers.CharField())

    # actions
    terminate = serializers.IntegerField(write_only=True)
    enqueue = serializers.BooleanField(write_only=True)

    def update(self, instance, validated_data):
        if validated_data.get('terminate'):
            for execution in instance.execution_set.all():
                if execution.id == validated_data['terminate']:
                    execution.status = Execution.KILLED
                    execution.save()
        if validated_data.get('enqueue'):
            instance.enqueue()
        return instance
