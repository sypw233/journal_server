from django.db import models
from django.utils import timezone
from users.models import User

class SyncRecord(models.Model):
    """
    同步记录模型
    记录用户最后一次同步状态和冲突数量
    """
    SYNC_STATUS_CHOICES = (
        (0, '未同步'),
        (1, '同步中'),
        (2, '同步完成'),
        (3, '同步失败'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sync_records')
    last_sync_time = models.DateTimeField(default=timezone.now)
    sync_status = models.PositiveSmallIntegerField(choices=SYNC_STATUS_CHOICES, default=0)
    conflict_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = '同步记录'
        verbose_name_plural = '同步记录'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_sync_status_display()}"


class SyncLog(models.Model):
    """
    同步日志模型
    记录每次同步的详细操作
    """
    OPERATION_CHOICES = (
        (0, '创建'),
        (1, '更新'),
        (2, '删除'),
    )
    
    record = models.ForeignKey(SyncRecord, on_delete=models.CASCADE, related_name='logs')
    operation_type = models.PositiveSmallIntegerField(choices=OPERATION_CHOICES)
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=100)
    operation_time = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = '同步日志'
        verbose_name_plural = '同步日志'
    
    def __str__(self):
        return f"{self.get_operation_type_display()} {self.entity_type}:{self.entity_id}"