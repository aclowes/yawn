from rest_framework import serializers

from yawn.worker.models import Worker, Message, Queue


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'


class QueueSerializer(serializers.ModelSerializer):
    message_count = serializers.IntegerField(read_only=True, source='message__count')
    purge = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = Queue
        fields = '__all__'

    def update(self, instance, validated_data):
        if validated_data['purge'] is True:
            instance.message_set.all().delete()
            instance.message__count = 0
        return instance


class MessageSerializer(serializers.ModelSerializer):
    queue = serializers.CharField(source='queue.name')

    class Meta:
        model = Message
        fields = ('id', 'queue', 'queue_id')
