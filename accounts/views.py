from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer, SyncRecordSerializer
from .models import SyncRecord

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """用户注册视图"""
    
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    """用户详情视图，用于获取和更新用户资料"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义JWT令牌获取视图，支持使用用户名、邮箱或手机号登录"""
    
    def post(self, request, *args, **kwargs):
        # 获取请求数据
        username = request.data.get('username')
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')
        
        # 至少需要提供一种登录方式
        if not any([username, email, phone]):
            return Response(
                {"error": "请提供用户名、邮箱或手机号"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 根据提供的登录方式查找用户
        try:
            if username:
                user = User.objects.get(username=username)
            elif email:
                user = User.objects.get(email=email)
            elif phone:
                user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(
                {"error": "用户不存在"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 验证密码
        if not user.check_password(password):
            return Response(
                {"error": "密码错误"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 生成令牌
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_data(request):
    """获取当前登录用户的数据"""
    
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class SyncRecordListCreateView(generics.ListCreateAPIView):
    """同步记录列表和创建视图"""
    
    serializer_class = SyncRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SyncRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
