from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import SyncRecord, SyncLog
from .serializers import SyncRecordSerializer, SyncLogSerializer
from journal_data.models import JournalEntry
from journal_data.serializers import EntrySerializer

class SyncInitView(APIView):
    """
    初始化同步端点
    返回用户的基础数据
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 获取用户所有日记条目
            entries = JournalEntry.objects.filter(user=request.user).order_by('-date')
            entry_serializer = EntrySerializer(entries, many=True)
            
            # 创建或更新同步记录
            sync_record, created = SyncRecord.objects.get_or_create(
                user=request.user,
                defaults={
                    'sync_status': 2,  # 同步完成
                    'last_sync_time': timezone.now()
                }
            )
            
            if not created:
                sync_record.sync_status = 2
                sync_record.last_sync_time = timezone.now()
                sync_record.save()
            
            return Response({
                'entries': entry_serializer.data,
                'last_sync_time': sync_record.last_sync_time
            })
            
        except Exception as e:
            return Response({
                'error': '同步初始化失败',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SyncPushView(APIView):
    """
    客户端推送变更端点
    处理客户端上传的变更数据
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # 获取或创建同步记录
            sync_record, created = SyncRecord.objects.get_or_create(
                user=request.user,
                defaults={
                    'sync_status': 1,  # 同步中
                    'last_sync_time': timezone.now()
                }
            )
            
            if not created:
                sync_record.sync_status = 1
                sync_record.save()
            
            # TODO: 实现具体的数据同步逻辑
            
            sync_record.sync_status = 2  # 同步完成
            sync_record.last_sync_time = timezone.now()
            sync_record.save()
            
            return Response({
                'message': '数据同步成功',
                'last_sync_time': sync_record.last_sync_time
            })
            
        except Exception as e:
            return Response({
                'error': '数据同步失败',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SyncPullView(APIView):
    """
    客户端拉取变更端点
    返回客户端需要的变更数据
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            last_sync_time = request.query_params.get('last_sync_time')
            
            # 获取同步记录
            sync_record = SyncRecord.objects.get(user=request.user)
            
            # 获取变更数据
            if last_sync_time:
                entries = JournalEntry.objects.filter(
                    user=request.user,
                    date__gt=last_sync_time
                ).order_by('-date')
            else:
                entries = JournalEntry.objects.filter(
                    user=request.user
                ).order_by('-date')
                
            entry_serializer = EntrySerializer(entries, many=True)
            
            # 更新同步记录
            sync_record.sync_status = 2  # 同步完成
            sync_record.last_sync_time = timezone.now()
            sync_record.save()
            
            return Response({
                'entries': entry_serializer.data,
                'last_sync_time': sync_record.last_sync_time
            })
            
        except Exception as e:
            return Response({
                'error': '获取变更数据失败',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SyncResolveConflictView(APIView):
    """
    解决数据冲突端点
    处理客户端和服务器之间的数据冲突
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # 获取同步记录
            sync_record = SyncRecord.objects.get(user=request.user)
            
            # TODO: 实现具体的冲突解决逻辑
            
            # 更新同步记录
            sync_record.conflict_count += 1
            sync_record.save()
            
            return Response({
                'message': '冲突解决成功',
                'conflict_count': sync_record.conflict_count
            })
            
        except Exception as e:
            return Response({
                'error': '冲突解决失败',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)