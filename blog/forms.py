from .models import Post
from django import forms
from tinymce.widgets import TinyMCE
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class PostForm(BaseForm):
    description = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = Post
        fields = ('title','description','image',)

class UserForm(BaseForm):

    password=forms.CharField(widget=forms.PasswordInput())
    confirm_password=forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model=User
        fields=('username','email','password','confirm_password')
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'password': _('Password'),
            'confirm_password': _('Confirm Password'),

        }

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )
        return cleaned_data