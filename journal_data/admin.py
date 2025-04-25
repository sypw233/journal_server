from django.contrib import admin

from .models import JournalEntry

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'date')
    search_fields = ('text', 'user__username')
    list_filter = ('date',)
    date_hierarchy = 'date'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['text'].widget.attrs['style'] = 'width: 800px; height: 200px;'
        return form
