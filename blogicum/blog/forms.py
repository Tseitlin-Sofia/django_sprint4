from .models import Comment, Post, User
from django import forms
from django.core.mail import EmailMultiAlternatives
from django.template import loader


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    post = forms.DateField(
        label='Дата публикации',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = Post
        exclude = ['author',]
