from rest_framework import serializers
from .models import SyncRecord, SyncLog

class SyncRecordSerializer(serializers.ModelSerializer):
    """
    同步记录序列化器
    用于API请求和响应
    """
    class Meta:
        model = SyncRecord
        fields = ['id', 'user', 'last_sync_time', 'sync_status', 'conflict_count']
        read_only_fields = ['id', 'user']

class SyncLogSerializer(serializers.ModelSerializer):
    """
    同步日志序列化器
    用于API请求和响应
    """
    class Meta:
        model = SyncLog
        fields = ['id', 'record', 'operation_type', 'entity_type', 'entity_id', 'operation_time']
        read_only_fields = ['id']