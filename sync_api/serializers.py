from rest_framework import serializers
from .models import SyncSession, SyncConflict


class SyncSessionSerializer(serializers.ModelSerializer):
    """同步会话序列化器"""
    
    class Meta:
        model = SyncSession
        fields = ['id', 'device_id', 'started_at', 'completed_at', 'status', 
                  'items_sent', 'items_received', 'conflicts', 'error_message']
        read_only_fields = ['id', 'started_at', 'completed_at', 'status', 
                           'items_sent', 'items_received', 'conflicts', 'error_message']


class SyncConflictSerializer(serializers.ModelSerializer):
    """同步冲突序列化器"""
    
    class Meta:
        model = SyncConflict
        fields = ['id', 'session', 'model_name', 'object_id', 'client_version', 
                  'server_version', 'resolved', 'resolution', 'created_at', 'resolved_at']
        read_only_fields = ['id', 'session', 'model_name', 'object_id', 'client_version', 
                           'server_version', 'created_at', 'resolved_at']