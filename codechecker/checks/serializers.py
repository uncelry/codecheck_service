from rest_framework import serializers
from .models import CheckLog

class CheckLogSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source='created_at')
    class Meta:
        model = CheckLog
        fields = ('status','date','result','email_sent')
