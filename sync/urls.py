from django.urls import path
from .views import SyncInitView, SyncPushView, SyncPullView, SyncResolveConflictView

urlpatterns = [
    path('init/', SyncInitView.as_view(), name='sync-init'),
    path('push/', SyncPushView.as_view(), name='sync-push'),
    path('pull/', SyncPullView.as_view(), name='sync-pull'),
    path('resolve-conflict/', SyncResolveConflictView.as_view(), name='sync-resolve-conflict'),
]