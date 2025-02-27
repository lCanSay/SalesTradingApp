from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import LoginForm, ProfileForm, RegistrationForm

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(f"Attempting to authenticate user: {username}")  # Debug print
            user = authenticate(username=username, password=password)
            if user:
                print(f"User authenticated: {user.username}")  # Debug print
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                print(f"Access Token: {access_token}")  # Debug print
                print(f"Refresh Token: {refresh_token}")  # Debug print

                response = redirect('product-list') 
                response.set_cookie('access_token', access_token, httponly=True)
                response.set_cookie('refresh_token', refresh_token, httponly=True)
                return response
            else:
                print("Authentication failed: Invalid credentials")  # Debug print
                form.add_error(None, 'Invalid username or password')
        else:
            print("Form is invalid")  # Debug print
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = redirect('product-list') 
            response.set_cookie('access_token', access_token, httponly=True)
            response.set_cookie('refresh_token', refresh_token, httponly=True)
            return response
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@csrf_exempt
def refresh_token(request):
    refresh_token = request.COOKIES.get('refresh_token')
    if refresh_token:
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            response = JsonResponse({'access': access_token})
            response.set_cookie('access_token', access_token, httponly=True)
            return response
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Refresh token not found'}, status=400)
    
@csrf_exempt
def user_logout(request):
    response = redirect('login')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response

@csrf_exempt
def profile(request):
    # return render(request, 'users/profile.html', {'user': request.user})
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'users/profile.html', {'form': form})
