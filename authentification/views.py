from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from authentification.forms import RegistrationForm
from authentification.models import CustomUser

# Create your views here.

def index(request):
    return render(request, 'authentification/index.html')

def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create the user
            user = CustomUser.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                role=form.cleaned_data['role'],
            )
            # Log in the user after registration
            login(request, user)

            # Redirect to role-specific profile completion page
            if user.role == 'VOLUNTEER':
                return redirect('authentification:complete_volunteer_profile')  
            elif user.role == 'NPO_MANAGER':
                return redirect('authentification:complete_npo_profile')  

            messages.success(request, "Registration successful!")
            return redirect('authentification:index')  # Fallback redirect
        else:
            for field, errors in form.errors.items():
                messages.error(request, f"{field}: {', '.join(errors)}")
            return redirect('authentification:signup')  # Replace with the name of your registration URL
    else:
        form = RegistrationForm()

    return render(request, 'authentification/signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validate inputs
        if not username or not password:
            messages.error(request, "Both username and password are required!")
            return redirect('authentification:signin')

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            messages.error(request, "User does not exist. Please register first!")
            return redirect('authentification:signin')

        # Authenticate user
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            fname = user.first_name
            messages.success(request, f"Welcome back, {fname}!")
            return redirect('authentification:index')  # Redirect home page URL name
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect('authentification:signin')
    else:
        return render(request, 'authentification/signin.html')

def signout(request):
    logout(request)
    messages.success(request,'Logged out')
    return redirect('authentification:index')

def complete_volunteer_profile(request):
    messages.success(request,'Volunteer profile is under work')
    return redirect('authentification:index')

def complete_npo_profile(request):
    messages.success(request,'NPO profile is under work')
    return redirect('authentification:index')