from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from .models import SyncRecord

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器，用于用户资料的增删改查"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'bio', 'last_sync']
        read_only_fields = ['id', 'last_sync']


class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    
    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    phone = serializers.CharField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'phone', 'avatar', 'bio']

    def validate(self, attrs):
        # 验证两次密码是否一致
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次密码不匹配"})
        
        # 验证至少提供了邮箱或手机号之一
        if not attrs.get('email') and not attrs.get('phone'):
            raise serializers.ValidationError({"email_phone": "邮箱和手机号至少提供一个"})
            
        return attrs

    def create(self, validated_data):
        # 移除password2字段，它不是User模型的一部分
        validated_data.pop('password2', None)
        
        # 创建用户
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            phone=validated_data.get('phone'),
            password=validated_data['password']
        )
        
        # 设置其他字段
        if 'avatar' in validated_data:
            user.avatar = validated_data['avatar']
        if 'bio' in validated_data:
            user.bio = validated_data['bio']
            
        user.save()
        return user


class SyncRecordSerializer(serializers.ModelSerializer):
    """同步记录序列化器"""
    
    class Meta:
        model = SyncRecord
        fields = ['id', 'user', 'device_id', 'last_sync_time', 'sync_status']
        read_only_fields = ['id', 'user']