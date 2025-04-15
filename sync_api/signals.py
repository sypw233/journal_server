from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.apps import apps


def get_syncable_models():
    """获取所有可同步的模型"""
    syncable_models = []
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            # 检查模型是否有SyncableModel的特征
            if hasattr(model, 'is_synced') and hasattr(model, 'sync_version'):
                syncable_models.append(model)
    return syncable_models


@receiver(post_save)
def update_sync_status(sender, instance, created, **kwargs):
    """当模型实例保存时更新同步状态"""
    # 检查是否是可同步模型
    if hasattr(instance, 'is_synced') and hasattr(instance, 'sync_version'):
        # 如果不是通过同步API创建的，则标记为未同步
        if not getattr(instance, '_syncing', False):
            instance.is_synced = False
            instance.sync_version += 1
            # 使用update_fields避免无限递归
            type(instance).objects.filter(pk=instance.pk).update(
                is_synced=False,
                sync_version=instance.sync_version
            )
            
            # 更新用户的最后同步时间
            if hasattr(instance, 'user') and instance.user:
                instance.user.last_sync = timezone.now()
                instance.user.save(update_fields=['last_sync'])


@receiver(post_delete)
def handle_deleted_syncable(sender, instance, **kwargs):
    """当模型实例删除时处理同步状态"""
    # 检查是否是可同步模型
    if hasattr(instance, 'is_synced') and hasattr(instance, 'sync_version'):
        # 如果模型支持软删除，则使用软删除而不是硬删除
        if hasattr(instance, 'is_deleted') and hasattr(instance, 'soft_delete'):
            # 阻止实际删除，改为软删除
            instance.soft_delete()
            
            # 更新用户的最后同步时间
            if hasattr(instance, 'user') and instance.user:
                instance.user.last_sync = timezone.now()
                instance.user.save(update_fields=['last_sync'])