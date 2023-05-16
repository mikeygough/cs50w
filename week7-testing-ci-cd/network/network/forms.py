from django import forms
from .models import Post

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["body"]

        # style
        widgets = {
            "body": forms.Textarea(attrs={"rows": 5}),
        }
        labels = {
            "body": "",
        }