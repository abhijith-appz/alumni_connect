"""
messaging/models.py
Direct messaging between students and alumni.
"""

from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """
    A two-person thread. Created lazily on first message.
    participants is always exactly 2 users.
    """
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations'
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conversations'
        ordering = ['-updated_at']

    def __str__(self):
        names = ', '.join(p.get_full_name() for p in self.participants.all())
        return f"Conversation: {names}"

    def other_participant(self, user):
        return self.participants.exclude(pk=user.pk).first()

    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def last_message(self):
        return self.messages.order_by('-created_at').first()

    @classmethod
    def get_or_create_between(cls, user1, user2):
        """Return existing conversation or create a new one."""
        existing = cls.objects.filter(
            participants=user1
        ).filter(
            participants=user2
        ).first()
        if existing:
            return existing, False
        conv = cls.objects.create()
        conv.participants.add(user1, user2)
        return conv, True


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content      = models.TextField()
    attachment   = models.FileField(upload_to='message_attachments/', blank=True, null=True)
    is_read      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class ContactMessage(models.Model):
    """Messages submitted via the public Contact page."""
    name       = models.CharField(max_length=120)
    email      = models.EmailField()
    subject    = models.CharField(max_length=200)
    message    = models.TextField()
    user_type  = models.CharField(max_length=20, blank=True)
    is_read    = models.BooleanField(default=False)
    reply      = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contact_messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.subject}] from {self.name}"
