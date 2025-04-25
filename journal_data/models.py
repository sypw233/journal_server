from django.db import models
from users.models import User

class JournalEntry(models.Model):
    """
    日记条目模型
    记录用户的日记内容及相关信息
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="journal_entries")
    is_mark = models.BooleanField(default=False)
    date = models.DateTimeField()
    text = models.TextField(blank=True, null=True)
    location_name = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    images_json = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.date.strftime('%Y-%m-%d')}"

