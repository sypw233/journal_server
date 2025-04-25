from rest_framework import serializers
from journal_data.models import JournalEntry

class EntrySerializer(serializers.ModelSerializer):
    """
    日志条目序列化器
    
    Attributes:
        model: 关联的JournalEntry模型
        fields: 包含所有模型字段
        read_only_fields: 防止用户修改的字段
    """
    class Meta:
        model = JournalEntry
        fields = ['id', 'user', 'is_mark', 'date', 'text', 'location_name', 'latitude', 'longitude', 'images_json']
        read_only_fields = ['id', 'user']