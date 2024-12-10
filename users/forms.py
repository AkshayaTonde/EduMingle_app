from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import QuizQuestion, QuizResponse
from .models import Profile


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):
    school_name = forms.CharField(max_length=100)
    preferred_subjects = forms.CharField(max_length=255, required=False)
    study_type = forms.ChoiceField(choices=[('online', 'Online'), ('offline', 'Offline'), ('hybrid', 'Hybrid')], required=False)
    user_bio = forms.CharField(widget=forms.Textarea, required=False)

    
    class Meta:
        model = Profile
        fields = ['image','school_name','preferred_subjects','study_type','user_bio']

class ViewAllProfiles(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)
    school_name = forms.CharField(max_length=100)


class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super(QuizForm, self).__init__(*args, **kwargs)
        
        for question in questions:
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.question_text,
                choices=[
                    (question.option_1, question.option_1),
                    (question.option_2, question.option_2),
                    (question.option_3, question.option_3),
                    (question.option_4, question.option_4),
                ],
                widget=forms.RadioSelect,
                required=True
            )
