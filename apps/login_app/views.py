from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import *
import bcrypt

def index(request):
    context = {
        'all_users':User.objects.all()
    }
    return render(request, "login_app/index.html", context)

def register(request):

    #Check if username already exists in database
    if(User.objects.filter(email=request.POST['email'])):
        print("User already exists in db")
        messages.add_message(request, messages.INFO, 'User already exists in db')
        return redirect('/')

    errors = User.objects.registration_validator(request.POST)
        # check if the errors dictionary has anything in it
    if len(errors) > 0:
        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)
        # redirect the user back to the form to fix the errors
        return redirect('/')
    else:
        print("Plaintext_password", request.POST['password'])
        hashed_password = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
        print("hashed_password", hashed_password)

        #Store user object we just created in variable called "current_user"
        current_user = User.objects.create(first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], password=hashed_password)
        
        #Store current user's id in session as a key called "current_user_id"
        request.session['current_user_id'] = current_user.id

    return redirect('/dashboard')

def login(request):

    errors = User.objects.login_validator(request.POST)
        # check if the errors dictionary has anything in it
    if len(errors) > 0:
        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)
        # redirect the user back to the form to fix the errors
        return redirect('/')
    else:
        print("email",request.POST['email'])
        print(request.POST['password'])

        if User.objects.filter(email=request.POST['email']):
            #Get User object
            current_user = User.objects.get(email=request.POST['email'])
            #Get user objects' password
            user_password = current_user.password #User's password (hashed)
            #Get the plaintext password from the login page
            entered_password = request.POST['password'] #User's entered password from login (plaintext)
            print("user's hashed password", user_password)
        is_match = bcrypt.checkpw(entered_password.encode(), user_password.encode())

        if(is_match == True):
            request.session['current_user_id'] = current_user.id
            return redirect('/dashboard')
        else:
            return redirect('/')

    return redirect('/dashboard')

def dashboard(request):
    context = {
        'current_user' : User.objects.get(id=request.session['current_user_id'])
    }
    return render(request, "login_app/dashboard.html", context)
