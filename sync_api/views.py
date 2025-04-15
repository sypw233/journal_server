from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db import transaction
from django.apps import apps
import json
import uuid

from .models import SyncSession, SyncConflict
from .serializers import SyncSessionSerializer, SyncConflictSerializer
from api.models import JournalEntry as Journal, Category, Tag


class SyncSessionViewSet(viewsets.ModelViewSet):
    """同步会话视图集，用于管理同步会话"""
    
    serializer_class = SyncSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SyncSession.objects.filter(user=self.request.user).order_by('-started_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SyncConflictViewSet(viewsets.ModelViewSet):
    """同步冲突视图集，用于管理同步冲突"""
    
    serializer_class = SyncConflictSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SyncConflict.objects.filter(
            session__user=self.request.user
        ).order_by('-created_at')


class SyncDataView(APIView):
    """数据同步视图，处理客户端和服务器之间的数据同步"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """获取服务器上的更新数据"""
        # 获取客户端最后同步时间
        last_sync = request.query_params.get('last_sync')
        if not last_sync:
            return Response({"error": "缺少last_sync参数"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            last_sync_time = timezone.datetime.fromisoformat(last_sync)
        except ValueError:
            return Response({"error": "last_sync格式无效"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取设备ID
        device_id = request.query_params.get('device_id')
        if not device_id:
            return Response({"error": "缺少device_id参数"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建同步会话
        session = SyncSession.objects.create(
            user=request.user,
            device_id=device_id,
            status='started'
        )
        
        # 获取各模型的更新数据
        updates = {
            'journals': self._get_model_updates(Journal, request.user, last_sync_time),
            'categories': self._get_model_updates(Category, request.user, last_sync_time),
            'tags': self._get_model_updates(Tag, request.user, last_sync_time),
        }
        
        # 更新同步会话状态
        total_items = sum(len(items) for items in updates.values())
        session.items_sent = total_items
        session.complete()
        
        return Response({
            'session_id': session.id,
            'updates': updates
        })
    
    def post(self, request):
        """处理客户端提交的更新数据"""
        # 获取设备ID
        device_id = request.data.get('device_id')
        if not device_id:
            return Response({"error": "缺少device_id参数"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建同步会话
        session = SyncSession.objects.create(
            user=request.user,
            device_id=device_id,
            status='started'
        )
        
        # 获取客户端提交的更新数据
        updates = request.data.get('updates', {})
        if not updates:
            return Response({"error": "缺少updates数据"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 处理各模型的更新数据
        results = {}
        conflicts = []
        
        with transaction.atomic():
            # 处理日记更新
            if 'journals' in updates:
                journal_results, journal_conflicts = self._process_model_updates(
                    Journal, updates['journals'], request.user, session
                )
                results['journals'] = journal_results
                conflicts.extend(journal_conflicts)
            
            # 处理分类更新
            if 'categories' in updates:
                category_results, category_conflicts = self._process_model_updates(
                    Category, updates['categories'], request.user, session
                )
                results['categories'] = category_results
                conflicts.extend(category_conflicts)
            
            # 处理标签更新
            if 'tags' in updates:
                tag_results, tag_conflicts = self._process_model_updates(
                    Tag, updates['tags'], request.user, session
                )
                results['tags'] = tag_results
                conflicts.extend(tag_conflicts)
        
        # 更新同步会话状态
        total_items = sum(len(items) for items in results.values())
        session.items_received = total_items
        session.conflicts = len(conflicts)
        session.complete()
        
        # 返回处理结果
        return Response({
            'session_id': session.id,
            'results': results,
            'conflicts': conflicts
        })
    
    def _get_model_updates(self, model, user, last_sync_time):
        """获取指定模型的更新数据"""
        updates = model.objects.filter(
            user=user,
            updated_at__gt=last_sync_time
        )
        
        # 使用模型的序列化器序列化数据
        serializer_class = self._get_serializer_for_model(model)
        serializer = serializer_class(updates, many=True)
        return serializer.data
    
    def _process_model_updates(self, model, updates, user, session):
        """处理指定模型的更新数据"""
        results = []
        conflicts = []
        
        for update in updates:
            try:
                # 尝试查找对象
                obj_id = update.get('id')
                if not obj_id:
                    continue
                
                try:
                    obj = model.objects.get(id=obj_id, user=user)
                    # 对象存在，检查版本
                    if obj.sync_version > update.get('sync_version', 0):
                        # 服务器版本更新，记录冲突
                        conflict = SyncConflict.objects.create(
                            session=session,
                            model_name=model.__name__,
                            object_id=obj_id,
                            client_version=update.get('sync_version', 0),
                            server_version=obj.sync_version
                        )
                        conflicts.append({
                            'id': str(conflict.id),
                            'model': model.__name__,
                            'object_id': obj_id
                        })
                        continue
                    
                    # 更新对象
                    serializer_class = self._get_serializer_for_model(model)
                    serializer = serializer_class(obj, data=update, partial=True)
                    if serializer.is_valid():
                        obj = serializer.save()
                        obj.sync_version += 1
                        obj.mark_synced()
                        results.append({
                            'id': str(obj.id),
                            'status': 'updated'
                        })
                    else:
                        results.append({
                            'id': str(obj_id),
                            'status': 'error',
                            'errors': serializer.errors
                        })
                
                except model.DoesNotExist:
                    # 对象不存在，创建新对象
                    serializer_class = self._get_serializer_for_model(model)
                    serializer = serializer_class(data=update)
                    if serializer.is_valid():
                        obj = serializer.save(user=user)
                        obj.mark_synced()
                        results.append({
                            'id': str(obj.id),
                            'status': 'created'
                        })
                    else:
                        results.append({
                            'id': str(obj_id),
                            'status': 'error',
                            'errors': serializer.errors
                        })
            
            except Exception as e:
                # 处理异常
                results.append({
                    'id': str(update.get('id')),
                    'status': 'error',
                    'message': str(e)
                })
        
        return results, conflicts
    
    def _get_serializer_for_model(self, model):
        """获取模型对应的序列化器"""
        if model == Journal:
            from api.serializers import JournalSerializer
            return JournalSerializer
        elif model == Category:
            from api.serializers import CategorySerializer
            return CategorySerializer
        elif model == Tag:
            from api.serializers import TagSerializer
            return TagSerializer
        else:
            raise ValueError(f"未知模型: {model.__name__}")


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resolve_conflict(request, conflict_id):
    """解决同步冲突"""
    try:
        conflict = SyncConflict.objects.get(id=conflict_id, session__user=request.user)
    except SyncConflict.DoesNotExist:
        return Response({"error": "冲突不存在"}, status=status.HTTP_404_NOT_FOUND)
    
    resolution = request.data.get('resolution')
    if not resolution or resolution not in ['client', 'server', 'merged']:
        return Response({"error": "无效的解决方式"}, status=status.HTTP_400_BAD_REQUEST)
    
    # 获取冲突对象
    model_name = conflict.model_name
    model = apps.get_model('api', model_name)
    
    try:
        obj = model.objects.get(id=conflict.object_id, user=request.user)
    except model.DoesNotExist:
        return Response({"error": "对象不存在"}, status=status.HTTP_404_NOT_FOUND)
    
    # 根据解决方式处理冲突
    if resolution == 'client':
        # 使用客户端数据
        client_data = request.data.get('client_data')
        if not client_data:
            return Response({"error": "缺少client_data"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer_class = self._get_serializer_for_model(model)
        serializer = serializer_class(obj, data=client_data, partial=True)
        if serializer.is_valid():
            obj = serializer.save()
            obj.sync_version = max(conflict.client_version, conflict.server_version) + 1
            obj.mark_synced()
        else:
            return Response({"error": "客户端数据无效", "errors": serializer.errors}, 
                            status=status.HTTP_400_BAD_REQUEST)
    
    elif resolution == 'merged':
        # 使用合并数据
        merged_data = request.data.get('merged_data')
        if not merged_data:
            return Response({"error": "缺少merged_data"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer_class = self._get_serializer_for_model(model)
        serializer = serializer_class(obj, data=merged_data, partial=True)
        if serializer.is_valid():
            obj = serializer.save()
            obj.sync_version = max(conflict.client_version, conflict.server_version) + 1
            obj.mark_synced()
        else:
            return Response({"error": "合并数据无效", "errors": serializer.errors}, 
                            status=status.HTTP_400_BAD_REQUEST)
    
    # 标记冲突为已解决
    conflict.resolve(resolution)
    
    return Response({
        "status": "success",
        "message": "冲突已解决",
        "resolution": resolution
    })


def _get_serializer_for_model(model):
    """获取模型对应的序列化器"""
    if model.__name__ == 'Journal':
        from api.serializers import JournalSerializer
        return JournalSerializer
    elif model.__name__ == 'Category':
        from api.serializers import CategorySerializer
        return CategorySerializer
    elif model.__name__ == 'Tag':
        from api.serializers import TagSerializer
        return TagSerializer
    else:
        raise ValueError(f"未知模型: {model.__name__}")