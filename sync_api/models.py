from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid


class SyncableModel(models.Model):
    """可同步模型的基类，所有需要同步的模型都应该继承这个类"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(class)s_items')
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    is_deleted = models.BooleanField(_('是否删除'), default=False)
    is_synced = models.BooleanField(_('是否已同步'), default=False)
    sync_version = models.IntegerField(_('同步版本'), default=1)
    last_sync_time = models.DateTimeField(_('最后同步时间'), null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def mark_synced(self):
        """标记为已同步"""
        self.is_synced = True
        self.last_sync_time = timezone.now()
        self.save(update_fields=['is_synced', 'last_sync_time'])
    
    def soft_delete(self):
        """软删除"""
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])


class SyncSession(models.Model):
    """同步会话，记录每次同步的信息"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sync_sessions')
    device_id = models.CharField(_('设备ID'), max_length=100)
    started_at = models.DateTimeField(_('开始时间'), auto_now_add=True)
    completed_at = models.DateTimeField(_('完成时间'), null=True, blank=True)
    status = models.CharField(_('状态'), max_length=20, choices=[
        ('started', '开始'),
        ('completed', '完成'),
        ('failed', '失败'),
    ], default='started')
    items_sent = models.IntegerField(_('发送项目数'), default=0)
    items_received = models.IntegerField(_('接收项目数'), default=0)
    conflicts = models.IntegerField(_('冲突数'), default=0)
    error_message = models.TextField(_('错误信息'), blank=True)
    
    class Meta:
        verbose_name = _('同步会话')
        verbose_name_plural = _('同步会话')
        ordering = ['-started_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.started_at}'
    
    def complete(self):
        """标记同步会话为完成"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
    
    def fail(self, error_message):
        """标记同步会话为失败"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])


class SyncConflict(models.Model):
    """同步冲突记录"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(SyncSession, on_delete=models.CASCADE, related_name='conflict_records')
    model_name = models.CharField(_('模型名称'), max_length=100)
    object_id = models.UUIDField(_('对象ID'))
    client_version = models.IntegerField(_('客户端版本'))
    server_version = models.IntegerField(_('服务器版本'))
    resolved = models.BooleanField(_('是否已解决'), default=False)
    resolution = models.CharField(_('解决方式'), max_length=20, choices=[
        ('client', '使用客户端版本'),
        ('server', '使用服务器版本'),
        ('merged', '合并'),
    ], null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    resolved_at = models.DateTimeField(_('解决时间'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('同步冲突')
        verbose_name_plural = _('同步冲突')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.model_name} - {self.object_id}'
    
    def resolve(self, resolution):
        """解决冲突"""
        self.resolved = True
        self.resolution = resolution
        self.resolved_at = timezone.now()
        self.save(update_fields=['resolved', 'resolution', 'resolved_at'])