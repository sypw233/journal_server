from django.contrib import admin
from .models import SyncRecord, SyncLog

@admin.register(SyncRecord)
class SyncRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_sync_time', 'sync_status', 'conflict_count')
    list_filter = ('sync_status',)
    search_fields = ('user__username',)
    ordering = ('-last_sync_time',)

@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ('record', 'operation_type', 'operation_time', 'entity_type')
    list_filter = ('operation_type',)
    search_fields = ('entity_type', 'entity_id')
    ordering = ('-operation_time',)