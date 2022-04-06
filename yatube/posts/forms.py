from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

        def cleat_text(self):
            data = self.cleaned_data['text']
            if data == '':
                raise forms.ValidationError('Обязательное для заполнения поле')
            return data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)