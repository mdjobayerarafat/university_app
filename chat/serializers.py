# chat/serializers.py
from rest_framework import serializers
from .models import Messages

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ['id', 'description', 'sender_name', 'receiver_name',
                 'parent', 'is_announcement', 'timestamp']