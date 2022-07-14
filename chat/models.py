from django.db import models
from django.utils import timezone

# Create your models here.

class Message(models.Model):
    user = models.CharField(max_length=20)
    text = models.CharField(max_length=100)
    time = models.DateTimeField(default=timezone.now)
    
    def last_30_messages(self):
       return Message.objects.order_by('time')[:30]