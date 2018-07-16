import re
from operator import itemgetter

from django.db import transaction
from django.db.models import NOT_PROVIDED
from rest_framework import serializers

from yawn.task.serializers import TaskSerializer
from yawn.worker.models import Queue
from yawn.workflow.models import Workflow, WorkflowName, Run
from yawn.task.models import Template


class WorkflowNameSerializer(serializers.ModelSerializer):
    current_version = serializers.IntegerField(source='current_version.version')
    current_version_id = serializers.IntegerField()
    task_count = serializers.IntegerField()
    schedule = serializers.CharField(source='current_version.schedule')
    schedule_active = serializers.BooleanField(source='current_version.schedule_active')
    versions = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowName
        fields = '__all__'

    def get_versions(self, obj):
        """Provide a full list of versions, only on detail"""
        if self.context['view'].action == 'retrieve':
            return list(obj.workflow_set.order_by('id').values_list('id', flat=True))


class TemplateSerializer(serializers.ModelSerializer):
    queue = serializers.SlugRelatedField(slug_field='name', queryset=Queue.objects.all())
    upstream = serializers.ListField(
        child=serializers.CharField(), default=[], source='upstream.all')

    class Meta:
        model = Template
        exclude = ('workflow',)


class WorkflowSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name.name')
    name_id = serializers.IntegerField(read_only=True)
    tasks = TemplateSerializer(many=True, allow_empty=False, source='template_set')

    class Meta:
        model = Workflow
        fields = '__all__'
        read_only_fields = ('next_run', 'name_id')

    @transaction.atomic
    def create(self, validated_data):
        workflow_name = validated_data.pop('name')['name']
        name, _ = WorkflowName.objects.get_or_create(name=workflow_name)
        # get the current version and check for changes
        if name.current_version and unchanged(name.current_version, validated_data):
            # TODO return 302 found instead of 201 created
            return name.current_version

        # changed or no existing version: create a new version
        tasks = validated_data.pop('template_set')
        workflow = name.new_version(**validated_data)
        for task_kwargs in tasks:
            # the awkward 'all' is so serialization gets related tasks through the manager method
            upstream = workflow.template_set.filter(name__in=task_kwargs.pop('upstream')['all'])
            task = Template.objects.create(workflow=workflow, **task_kwargs)
            task.upstream.set(upstream)

        return workflow

    def validate_parameters(self, parameters):
        """Validate variable name is a slug and value is a string"""
        if not isinstance(parameters, dict):
            raise serializers.ValidationError('Workflow parameters must be a dictionary')
        key_regex = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
        errors = []
        for key, value in parameters.items():
            if not key_regex.fullmatch(key):
                errors.append('Invalid parameter key: %s' % key)
            if not isinstance(value, str):
                errors.append('Invalid parameter value: %s' % value)
        if errors:
            raise serializers.ValidationError(errors)
        return parameters

    def validate_tasks(self, tasks):
        """Validate tasks only reference already defined upstream tasks"""
        seen_tasks = set()
        errors = []
        for task in tasks:
            name = task['name']
            if name in seen_tasks:
                errors.append('Task names must be unique. Tas %s is defined more than once' % name)
            missing = set(task['upstream']['all']) - seen_tasks
            if missing:
                errors.append(
                    'Task {task} specifies upstream task(s) {upstream} but they do not exist. '
                    'Hint: check the order of your tasks.'.format(
                        task=name, upstream=', '.join(missing))
                )
            seen_tasks.add(name)

        if errors:
            raise serializers.ValidationError(errors)
        return tasks


def unchanged(current_workflow, new_data):
    """
    Detect if the new workflow is unchanged from the current version.

    This is ugly; suggestions would be appreciated...
    """
    ignore = ('id', 'name', 'version', 'schedule_active', 'next_run', 'parameters')
    if not compare_fields(current_workflow, new_data, ignore):
        return False

    new_tasks = sorted(new_data['template_set'], key=itemgetter('name'))
    current_tasks = list(current_workflow.template_set.order_by('name'))
    if len(new_tasks) != len(current_tasks):
        return False

    for current_task, new_task in zip(current_tasks, new_tasks):
        ignore = ('id', 'upstream', 'workflow')
        if not compare_fields(current_task, new_task, ignore):
            return False

        if set(new_task['upstream']['all']) == \
                set(current_task.upstream.values_list('name', flat=True)):
            continue
        else:
            return False

    return True


def compare_fields(instance, new_data, ignore_fields):
    """Compare a model instance to a new dict; return True if they match"""
    for field in instance._meta.fields:
        if field.name in ignore_fields:
            # ignored fields
            continue
        current_value = getattr(instance, field.name)
        if field.name not in new_data:
            # no value provided, check if the current value is the default
            default = field.default if field.default is not NOT_PROVIDED else None
            if current_value == default:
                continue
            else:
                return False
        if current_value != new_data[field.name]:
            return False

    return True


class RunSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, source='task_set', read_only=True)
    workflow_id = serializers.IntegerField()

    class Meta:
        model = Run
        exclude = ('workflow',)
        read_only_fields = ('submitted_time', 'scheduled_time', 'status')

    def create(self, validated_data):
        workflow = Workflow.objects.get(id=validated_data['workflow_id'])
        parameters = validated_data.get('parameters')
        run = workflow.submit_run(parameters)
        run.refresh_from_db()  # load submitted_time...
        return run
