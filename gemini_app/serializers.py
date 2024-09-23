from rest_framework import serializers
from .models import User,Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['user','text','is_bot','timestamp']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['telegram_id','username','first_name','last_name']