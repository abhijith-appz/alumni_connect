from django import forms
from .models import Message, ContactMessage


class MessageForm(forms.ModelForm):
    class Meta:
        model  = Message
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Type a message…',
            }),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model  = ContactMessage
        fields = ['name', 'email', 'user_type', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Write your message here…',
            }),
        }
