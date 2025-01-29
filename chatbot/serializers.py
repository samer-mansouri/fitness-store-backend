from rest_framework import serializers
from .models import Chat
from users.serializers import PartialUserSerializer
from users.models import User

class ChatSerializer(serializers.ModelSerializer):
    user = PartialUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')

    class Meta:
        model = Chat
        fields = ['id', 'user', 'message', 'response', 'created_at', 'updated_at', 'user_id']
        read_only_fields = ['user']
    
    def create(self, validated_data):
        user = self.context['request'].user
        chat = Chat.objects.create(user=user, **validated_data)
        return chat