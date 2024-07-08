from rest_framework import serializers

from chat.models import Chat
from users.models import User


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class ChatSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ('id', 'participants',)
