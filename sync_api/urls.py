from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'sessions', views.SyncSessionViewSet, basename='sync-session')
router.register(r'conflicts', views.SyncConflictViewSet, basename='sync-conflict')

urlpatterns = [
    # 视图集路由
    path('', include(router.urls)),
    
    # 数据同步API
    path('data/', views.SyncDataView.as_view(), name='sync-data'),
    
    # 解决冲突
    path('conflicts/<uuid:conflict_id>/resolve/', views.resolve_conflict, name='resolve-conflict'),
]