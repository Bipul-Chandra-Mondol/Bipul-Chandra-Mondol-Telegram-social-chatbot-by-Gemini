from django.db import models

# Create your models here.

class User(models.Model):
    telegram_id = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100,blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True,null=True)
    last_name = models.CharField(max_length=100, blank=True,null=True)

    def __str__(self):
        return self.username or self.telegram_id
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    is_bot = models.BooleanField(default=False)  # True if bot send message
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f'{self.user} - {"Bot" if self.is_bot else "User"} - {self.text[:50]}'