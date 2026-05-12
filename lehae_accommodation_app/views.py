from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .utils import generate_otp, mask_email

from .models import Profile

# Create your views here.

def Intro_loading(request):
    return render(request, 'IntroPage.html')

def Home(request):
    return render(request, 'HomePage.html')

def Register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        
        phone = request.POST.get('phone')
        id_number = request.POST.get('id_number')
        id_type = request.POST.get('id_type')
        
        if password != confirm:
            return render(request, 'RegisterPage.html', {'error': 'Passwords do not match'})
        
         # EMAIL CHECK
        if User.objects.filter(email=email).exists():
            return render(request, 'RegisterPage.html', {'error': 'Email already registered'})

        # ✅ CORRECT CHECK (Profile, not User)
        if Profile.objects.filter(id_number=id_number).exists():
            return render(request, 'RegisterPage.html', {'error': 'ID number already registered'})
        
        user = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name
            )
        
        user.set_password(password)
        user.save()
        
        Profile.objects.create(
            user=user,
            phone=phone,
            id_number=id_number,
            id_type=id_type,
        )
        
        return render(request, 'LoginPage.html', {'success': 'Registration successful. Please log in.'})
        
    return render(request, 'RegisterPage.html')

def Login(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            otp = generate_otp()

            # store OTP in session
            request.session['otp'] = otp
            request.session['user_id'] = user.id

            # send email
            send_mail(
                subject="YourLehae OTP - Request",
                message=f"Your OTP code is: {otp}",
                from_email="molangenikatleho00@gmail.com",
                recipient_list=[user.email],
                fail_silently=False,
            )

            return redirect('TwoFactorAuth')

        return render(request, 'LoginPage.html', {'error': 'Invalid Credentials'})

    return render(request, 'LoginPage.html')

def TwoFactorAuth(request):

    user_id = request.session.get('user_id')

    # safety check (if session expired or user tries direct access)
    if not user_id:
        return redirect('Login')

    user = User.objects.get(id=user_id)
    masked_email = mask_email(user.email)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')

        if entered_otp == session_otp:
            login(request, user)

            # cleanup session
            request.session.pop('otp', None)
            request.session.pop('user_id', None)

            return redirect('LehaeMainPage')

        return render(request, 'TwoFactorAuthPage.html', {
            'error': 'Invalid OTP',
            'masked_email': masked_email
        })

    return render(request, 'TwoFactorAuthPage.html', {
        'masked_email': masked_email
    })

def LehaeMainPage(request):
    return render(request, 'LehaeMainPage.html')

def ManageAccommodation(request):
    return render(request, 'ManageAccommodation.html')

def FindAccommodation(request):
    return render(request, 'FindAccommodation.html')

def StudentProfile(request):
    return render(request, 'StudentProfile.html')