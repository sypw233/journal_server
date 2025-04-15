from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json

from .models import JournalEntry, Category

# Journal Entry API views
@csrf_exempt
def journal_entry_list(request):
    if request.method == 'GET':
        entries = JournalEntry.objects.all()
        data = [{
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'created_at': entry.created_at.isoformat(),
            'updated_at': entry.updated_at.isoformat(),
            'user': entry.user.username
        } for entry in entries]
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        # 简化版本，实际应用中应添加更多验证
        user = User.objects.get(id=1)  # 默认使用ID为1的用户，实际应用中应使用认证
        entry = JournalEntry.objects.create(
            title=data.get('title'),
            content=data.get('content'),
            user=user
        )
        return JsonResponse({
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'created_at': entry.created_at.isoformat(),
            'updated_at': entry.updated_at.isoformat(),
            'user': entry.user.username
        }, status=201)

@csrf_exempt
def journal_entry_detail(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk)
    
    if request.method == 'GET':
        data = {
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'created_at': entry.created_at.isoformat(),
            'updated_at': entry.updated_at.isoformat(),
            'user': entry.user.username
        }
        return JsonResponse(data)
    
    elif request.method == 'PUT':
        data = json.loads(request.body)
        entry.title = data.get('title', entry.title)
        entry.content = data.get('content', entry.content)
        entry.save()
        return JsonResponse({
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'created_at': entry.created_at.isoformat(),
            'updated_at': entry.updated_at.isoformat(),
            'user': entry.user.username
        })
    
    elif request.method == 'DELETE':
        entry.delete()
        return JsonResponse({'message': 'Journal entry deleted successfully'}, status=204)

# Category API views
@csrf_exempt
def category_list(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        data = [{
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'user': category.user.username
        } for category in categories]
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        # 简化版本，实际应用中应添加更多验证
        user = User.objects.get(id=1)  # 默认使用ID为1的用户，实际应用中应使用认证
        category = Category.objects.create(
            name=data.get('name'),
            description=data.get('description'),
            user=user
        )
        return JsonResponse({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'user': category.user.username
        }, status=201)

@csrf_exempt
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'GET':
        data = {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'user': category.user.username
        }
        return JsonResponse(data)
    
    elif request.method == 'PUT':
        data = json.loads(request.body)
        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)
        category.save()
        return JsonResponse({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'user': category.user.username
        })
    
    elif request.method == 'DELETE':
        category.delete()
        return JsonResponse({'message': 'Category deleted successfully'}, status=204)
