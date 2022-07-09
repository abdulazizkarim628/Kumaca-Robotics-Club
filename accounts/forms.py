from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from blog.models import Category, Post
from django.contrib.auth import password_validation
from accounts.models import Author
from ckeditor.widgets import CKEditorWidget
from django_countries.widgets import CountrySelectWidget
class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=100,
                               help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                               required=True, widget=forms.TextInput(attrs={'class': 'form-control'}
                                                                     ))
    first_name = forms.CharField(max_length=50, help_text='Optional', required=True, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Firstname'
               }
    ))
    last_name = forms.CharField(max_length=50, help_text='Optional', required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Lastname'}
    ))
    email = forms.EmailField(help_text='Required', required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Email address'}))
    password1 = forms.CharField(required=True, max_length=255, label='Password',
    help_text=password_validation.password_validators_help_text_html(),
                                widget=forms.PasswordInput(
                                    attrs={'class': 'form-control', 'placeholder': 'Password'}
                                ))
    password2 = forms.CharField(required=True, max_length=255, label='Confirm password',
    help_text='Enter the password as before, for verification',
                                widget=forms.PasswordInput(
                                    attrs={'class': 'form-control', 'placeholder': 'Confirm password'},
                                ))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                               required=True, widget=forms.TextInput(attrs={'class': "form-control"}
                                                                     ))
    first_name = forms.CharField(max_length=50, help_text='Optional', required=True, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Firstname'
               }
    ))
    last_name = forms.CharField(max_length=50, help_text='Optional', required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Lastname'}
    ))
    email = forms.EmailField(help_text='email@example.com', required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'email@example.com'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


# author update 
class AuthorUpdateForm(forms.ModelForm):
    
    birthday = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'class': 'form-control', 'type': 'date'}
    ))

    phone_number = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'tel'
    }))

    workplace = forms.CharField(required=False, max_length=200, widget=forms.TextInput(
        attrs={'class': 'form-control'}
    ))

    whatsapp_link = forms.URLField(required=False, max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'type': 'tel','placeholder': 'Whatsapp chat link'
        }
    ))

    twitter_page = forms.URLField(required=False, widget=forms.URLInput(
        attrs={'class': 'form-control','type':'url', 'placeholder': 'link to your twitter page'}
    ))
    personal_website = forms.URLField(required=False, widget=forms.URLInput(
        attrs={'class': 'form-control','type':'url', 'placeholder': 'personal website'}
    ))

    facebook_page = forms.URLField(required=False, widget=forms.URLInput(
        attrs={'class': 'form-control', 'type': 'url', 'placeholder': 'link to your facebook page'}

    ))
    instagram_page = forms.URLField(required=False, widget=forms.URLInput(
        attrs={'class': 'form-control', 'type': 'url', 'placeholder': 'link to your instagram page'}
    ))

    
    class Meta:
        model = Author
        fields = ('birthday', 'bio', 'profile_picture', 'address', 'gender', 'country', 'workplace', 'personal_website', 'phone_number',
                    'whatsapp_link', 'twitter_page', 'facebook_page', 'instagram_page'
        )
        widgets = {'bio': forms.Textarea(attrs={
                'class': "form-control",
                "rows": "5",
                'maxlength': '255',
                'required': 'false'
            }),

             'profile_picture': forms.FileInput(attrs={
                "class": "form-control clearablefileinput",
                "type": "file",
                "id": "profile_picture",
            }),
            
            'country': CountrySelectWidget()

            }

class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditorWidget())

    class Meta:
        model = Post
        fields = ("title", "overview", "content", "tags", "category", 'image')
        widgets = {
            'image': forms.FileInput(attrs={
                "class": "form-control clearablefileinput",
                "type": "file",
                "id": "profile_picture",
            }),
        }

