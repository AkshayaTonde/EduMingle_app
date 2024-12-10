from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import QuizQuestion, QuizResponse
from .forms import QuizForm
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import NearestNeighbors
from .models import QuizResponse, QuizQuestion
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from .models import Profile
from django.db import models
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from chat.models import Connectionrequests
from sklearn.neighbors import NearestNeighbors
# Create your views here.


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"{username} has been created!")
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your account has been updated")
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)


@login_required
def take_quiz(request):
    questions = QuizQuestion.objects.all()
    user_has_taken_quiz = QuizResponse.objects.filter(user=request.user).exists()
    
    # Handle clear_previous flag
    if request.GET.get('clear_previous') == 'true':
        QuizResponse.objects.filter(user=request.user).delete()
        messages.info(request, "Your previous quiz responses have been cleared. Please take the quiz again.")
        return redirect('take_quiz')  # Reload the page without the query parameter

    # If user has taken the quiz, pass a flag to the template
    if user_has_taken_quiz and request.method != 'POST':
        return render(request, 'users/quiz.html', {'questions': questions, 'show_alert': True})
    
    # Handle quiz submission
    if request.method == 'POST':
        form = QuizForm(request.POST, questions=questions)
        if form.is_valid():
            # Save the new responses
            for question in questions:
                selected_option = form.cleaned_data[f'question_{question.id}']
                QuizResponse.objects.create(
                    user=request.user,
                    question=question,
                    selected_option=selected_option
                )
            messages.success(request, "Thank you for completing the quiz!")
            return redirect('study_partners_knn')  # Redirect to a results or profile page
    else:
        form = QuizForm(questions=questions)
    
    return render(request, 'users/quiz.html', {'form': form, 'show_alert': False})



def get_encoded_responses():
    users = User.objects.all()
    questions = QuizQuestion.objects.all()
    
    # Prepare a matrix where rows are users and columns are responses to questions
    response_matrix = []
    user_ids = []
    
    for user in users:
        user_response = []
        for question in questions:
            response = QuizResponse.objects.filter(user=user, question=question).first()
            if response:
                # Convert response text (e.g., option_1, option_2) into a number (1, 2, etc.)
                option_number = [question.option_1, question.option_2,question.option_3 , question.option_4].index(response.selected_option) + 1
                user_response.append(option_number)
            else:
                user_response.append(0)  # Assume 0 if no answer
        response_matrix.append(user_response)
        user_ids.append(user.id)
    
    return np.array(response_matrix), user_ids




@login_required
def find_study_partners_knn(request):
    response_matrix, user_ids = get_encoded_responses()
    
    # Handle case where there are not enough users
    if len(user_ids) <= 1:
        return render(request, 'users/study_partners.html', {
            'matches': None,
            'message': "Not enough users available for matching at the moment."
        })

    # Initialize the KNN model
    knn = NearestNeighbors(n_neighbors=min(4, len(user_ids)), metric='euclidean')  # Ensure n_neighbors <= number of users
    knn.fit(response_matrix)

    # Find the nearest neighbors for the current user
    current_user_index = user_ids.index(request.user.id)
    distances, indices = knn.kneighbors([response_matrix[current_user_index]])

    # Collect the top study partners (excluding the user themself)
    matches = []
    for i in range(1, len(indices[0])):  # Skip index 0 because it's the user themself
        match_id = user_ids[indices[0][i]]
        match_profile = Profile.objects.get(user__id=match_id)  # Get the Profile object directly
        match_score = distances[0][i]
        matches.append((match_profile, match_score))
    
    # Handle no matches found
    if not matches:
        return render(request, 'users/study_partners.html', {
            'matches': None,
            'message': "No suitable study partners found at this time. Please try again later."
        })

    # Check connection status
    updated_matches = []
    for profile, score in matches:
        is_connected = Connectionrequests.objects.filter(
            sender=request.user.profile, receiver=profile, is_approved=True
        ).exists() or Connectionrequests.objects.filter(
            sender=profile, receiver=request.user.profile, is_approved=True
        ).exists()

        updated_matches.append((profile, score, is_connected))

    return render(request, 'users/study_partners.html', {'matches': updated_matches})

@login_required
def view_profile(request, profile_id):
    # Fetch the profile using the profile_id
    profile = get_object_or_404(Profile, id=profile_id)
    return render(request, 'users/view_profile.html', {'profile': profile})

@login_required
def my_connections(request):
    # Fetch approved connections where the user is either the sender or the receiver
    approved_connections = Connectionrequests.objects.filter(
        is_approved=True
    ).filter(
        models.Q(sender=request.user.profile) | models.Q(receiver=request.user.profile)
    )

    return render(request, 'users/my_connections.html', {'connections': approved_connections})