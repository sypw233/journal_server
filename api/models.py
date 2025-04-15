from django.db import models
from django.conf import settings
from sync_api.models import SyncableModel

# Create your models here.
class JournalEntry(SyncableModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Journal Entry'
        verbose_name_plural = 'Journal Entries'
        ordering = ['-created_at']

class Category(SyncableModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

class Tag(SyncableModel):
    """标签模型，用于给日记条目添加标签"""
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='#3498db')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

# 日记和标签的多对多关系
class JournalTag(models.Model):
    """日记和标签的关联模型"""
    journal = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='journal_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='tag_journals')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Journal Tag'
        verbose_name_plural = 'Journal Tags'
        unique_together = ('journal', 'tag')
