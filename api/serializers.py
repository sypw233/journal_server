from rest_framework import serializers
from .models import JournalEntry, Category, Tag, JournalTag


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'created_at', 'updated_at', 'is_deleted', 'is_synced', 'sync_version', 'last_sync_time']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_synced', 'last_sync_time']


class JournalTagSerializer(serializers.ModelSerializer):
    """日记标签关联序列化器"""
    
    class Meta:
        model = JournalTag
        fields = ['id', 'journal', 'tag', 'created_at']
        read_only_fields = ['id', 'created_at']


class JournalSerializer(serializers.ModelSerializer):
    """日记序列化器"""
    tags = TagSerializer(many=True, read_only=True, source='journal_tags.tag')
    
    class Meta:
        model = JournalEntry
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'user', 'is_deleted', 'is_synced', 'sync_version', 'last_sync_time', 'tags']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user', 'is_synced', 'last_sync_time']


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'user', 'created_at', 'updated_at', 'is_deleted', 'is_synced', 'sync_version', 'last_sync_time']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'is_synced', 'last_sync_time']