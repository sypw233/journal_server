from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # 用户注册
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # JWT认证
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 用户资料管理
    path('profile/', views.UserDetailView.as_view(), name='user_profile'),
    
    # 同步记录
    path('sync-records/', views.SyncRecordListCreateView.as_view(), name='sync_records'),
]