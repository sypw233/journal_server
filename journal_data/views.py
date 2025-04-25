from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import JournalEntry
from .serializers import EntrySerializer

class EntryListCreateView(generics.ListCreateAPIView):
    """
    日记条目列表创建视图
    支持列出和创建用户日记条目
    """
    serializer_class = EntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class EntryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    日记条目详情视图
    支持检索、更新和删除单个日记条目
    """
    serializer_class = EntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)

class SyncDataView(APIView):
    """
    数据同步视图
    处理客户端与服务端之间的日记数据同步
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            last_sync_time = request.query_params.get('last_sync_time')
            user = request.user
            
            if last_sync_time:
                entries = JournalEntry.objects.filter(
                    user=user,
                    date__gt=last_sync_time
                ).order_by('-date')
            else:
                entries = JournalEntry.objects.filter(user=user).order_by('-date')
            
            serializer = EntrySerializer(entries, many=True)
            user.last_data_sync_time = timezone.now()
            user.save()
            
            return Response({
                'entries': serializer.data,
                'last_sync_time': user.last_data_sync_time
            })
            
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"数据同步错误: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({
                'error': '服务器内部错误',
                'details': str(e),
                'code': 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            user = request.user
            entries_data = request.data.get('entries', [])
            
            for entry_data in entries_data:
                entry_data['user'] = user.id
                serializer = EntrySerializer(data=entry_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response({
                        'error': '无效的条目数据',
                        'details': serializer.errors,
                        'code': 400
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            user.last_data_sync_time = timezone.now()
            user.save()
            
            return Response({
                'message': '数据同步成功',
                'last_sync_time': user.last_data_sync_time
            })
            
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"数据同步错误: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({
                'error': '服务器内部错误',
                'details': str(e),
                'code': 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
