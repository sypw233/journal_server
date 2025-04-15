from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """自定义用户管理器，支持使用邮箱或手机号作为用户名"""
    
    def create_user(self, username, email=None, phone=None, password=None, **extra_fields):
        if not username:
            raise ValueError(_('用户名必须提供'))
        
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(username, email, phone, password, **extra_fields)


class CustomUser(AbstractUser):
    """自定义用户模型，扩展AbstractUser以支持手机号"""
    
    email = models.EmailField(_('邮箱地址'), unique=True, null=True, blank=True)
    phone = models.CharField(_('手机号'), max_length=15, unique=True, null=True, blank=True)
    avatar = models.ImageField(_('头像'), upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(_('个人简介'), max_length=500, blank=True)
    last_sync = models.DateTimeField(_('最后同步时间'), null=True, blank=True)
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
    
    def __str__(self):
        return self.username


class SyncRecord(models.Model):
    """同步记录模型，用于记录数据同步状态"""
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sync_records')
    device_id = models.CharField(_('设备ID'), max_length=100)
    last_sync_time = models.DateTimeField(_('最后同步时间'))
    sync_status = models.CharField(_('同步状态'), max_length=20, 
                                choices=[
                                    ('success', '成功'),
                                    ('failed', '失败'),
                                    ('partial', '部分成功')
                                ])
    
    class Meta:
        verbose_name = _('同步记录')
        verbose_name_plural = _('同步记录')
        
    def __str__(self):
        return f"{self.user.username} - {self.device_id} - {self.last_sync_time}"
