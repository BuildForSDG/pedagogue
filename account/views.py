from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm , ContactForm, UserEditForm, ProfileEditForm

from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib import messages
from django.core.mail import send_mail


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, 
                                    username=cd['username'],
                                    password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return render(request, 'account/dashboard.html')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid Login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

def home(request):
    return render(request, 'account/home.html')


@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html', {'section' : 'dashboard'})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password'])
            # Save the user object
            new_user.save()
            # Create the user Profile
            Profile.objects.create(user=new_user)
            return render(request, 
                            'account/register_done.html',
                                {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form':user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                            data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request,
                    'account/edit.html',
                        {'user_form': user_form,
                            'profile_form': profile_form})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        #send mail
        sender_name = request.user.username
        sender_email = request.user.email

        message = "{0} has requested an interview at {1}".format(sender_name, form['date'])
        send_mail('New Enquiry', message, sender_email, ['osasisorae@gmail.com'])
        return HttpResponse("Thanks for wanting to be part of pedagogue, we get back to you within 24 hours")

    else:
        form = ContactForm()

    context = {
        'form': form
    }
    return render(request, 'account/contact.html', context)