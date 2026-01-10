from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ChatSettings(BaseModel):
    welcome_message = models.TextField(default="Xizmat ko'rsatish markazimizga xush kelibsiz! Sizga qanday yordam bera olamiz?")
    is_chat_enabled = models.BooleanField(default=True)
    auto_reply_enabled = models.BooleanField(default=False)
    auto_reply_text = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Chat Sozlamasi"
        verbose_name_plural = "Chat Sozlamalari"

    def __str__(self):
        return f"Chat Settings ({'Faol' if self.is_chat_enabled else 'Faol emas'})"

class Conversation(BaseModel):
    STATUS_CHOICES = (
        ('open', 'Ochiq'),
        ('closed', 'Yopilgan'),
        ('pending', 'Kutilmoqda'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user', help_text="Mijoz (Client)")
    responder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chats_as_responder', help_text="Admin yoki Supervayzer")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    last_message_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Suhbat"
        verbose_name_plural = "Suhbatlar"
        ordering = ['-last_message_at']

    def __str__(self):
        return f"Suhbat: {self.user.username} - {self.status}"

class ChatMessage(BaseModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    body = models.TextField()
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"
        ordering = ['created_at']

    def __str__(self):
        return f"Xabar: {self.sender.username} - {self.created_at}"
