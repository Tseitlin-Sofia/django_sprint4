from django import forms

from .models import Comment, Post


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        label='Дата публикации',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = Post
        exclude = ['author', ]
