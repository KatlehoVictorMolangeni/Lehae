from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .utils import generate_otp, mask_email
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Accreditation, Campus, Amenity
from .models import Profile, Merchant, PropertyImage
from .forms import PropertyForm, MerchantForm

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

    properties = Property.objects.filter(
        is_approved=True,
        is_active=True
    ).distinct()

    # SEARCH (title / address / city)
    search = request.GET.get('search')
    if search:
        properties = properties.filter(
            Q(title__icontains=search) |
            Q(address__icontains=search) |
            Q(city__icontains=search)
        )

    # PROPERTY TYPE
    property_type = request.GET.get('property_type')
    if property_type:
        properties = properties.filter(accommodation_type=property_type)

    # CAMPUS FILTER
    campus = request.GET.get('campus')
    if campus:
        properties = properties.filter(campuses__id=campus)

    # PRICE FILTER
    min_price = request.GET.get('min_price')
    if min_price:
        properties = properties.filter(monthly_rent__gte=min_price)

    max_price = request.GET.get('max_price')
    if max_price:
        properties = properties.filter(monthly_rent__lte=max_price)

    # ACCREDITATION FILTER
    accreditation = request.GET.get('accreditation')
    if accreditation:
        properties = properties.filter(accreditation__id=accreditation)

    # DATE FILTER
    available_from = request.GET.get('available_from')
    if available_from:
        properties = properties.filter(available_from__lte=available_from)

    context = {
        "properties": properties,
        "campuses": Campus.objects.all(),
        "accreditations": Accreditation.objects.all(),
    }

    return render(request, "FindAccommodation.html", context)


def StudentProfile(request):
    return render(request, 'StudentProfile.html')


def MerchantRegister(request):
    if request.method == "POST":
        form = MerchantForm(request.POST, request.FILES)

        if form.is_valid():
            # 1. Create User
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )

            # 2. Create Merchant Profile
            merchant = form.save(commit=False)
            merchant.user = user

            # default status (IMPORTANT for approval system)
            merchant.is_verified = False

            merchant.save()

            messages.success(request, "Merchant account created successfully. Await verification.")
            return redirect('Login')

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = MerchantForm()
    return render(request, 'MerchantRegistration.html', {"form": form})


def MerchantLogin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # 1. Authenticate user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            try:
                merchant = Merchant.objects.get(user=user)

                # 2. Check if merchant is allowed
                if not merchant.is_verified:
                    messages.error(request, "Your account is still pending verification.")
                    return redirect("MerchantLogin")

                # 3. Log user in
                login(request, user)

                return redirect("MerchantDashboard")

            except Merchant.DoesNotExist:
                messages.error(request, "You are not registered as a merchant.")
                return redirect("MerchantLogin")

        else:
            messages.error(request, "Invalid email or password.")
            return redirect("MerchantLogin")
    
    return render(request, 'MerchantLogin.html')


from django.shortcuts import render, redirect
from .models import Merchant, Property

def MerchantDashboard(request):

    # 🔐 AUTH CHECK
    if not request.user.is_authenticated:
        return redirect("MerchantLogin")

    # 🧑 GET MERCHANT
    try:
        merchant = Merchant.objects.get(user=request.user)
    except Merchant.DoesNotExist:
        return redirect("MerchantLogin")

    # 🏠 GET PROPERTIES
    properties = Property.objects.filter(merchant=merchant).order_by("-created_at")

    # 📊 STATS
    total_properties = properties.count()
    pending_approvals = properties.filter(is_approved=False).count()
    active_listings = properties.filter(is_approved=True, is_active=True).count()

    context = {
        "merchant": merchant,
        "properties": properties,
        "total_properties": total_properties,
        "pending_approvals": pending_approvals,
        "active_listings": active_listings,
    }

    return render(request, "MerchantDashboard.html", context)

@login_required
def ListAccommodationView(request):
    # Get the merchant linked to the logged-in user
    try:
        merchant = Merchant.objects.get(user=request.user)
    except Merchant.DoesNotExist:
        return redirect("MerchantLogin")

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)

        if form.is_valid():
            # Save property first
            property_obj = form.save(commit=False)
            property_obj.merchant = merchant
            property_obj.is_approved = False  # Requires admin approval
            property_obj.save()

            # Save ManyToMany fields:
            # accreditation, campuses, amenities
            form.save_m2m()

            # Save multiple gallery images
            for image in request.FILES.getlist('gallery_images'):
                PropertyImage.objects.create(
                    property=property_obj,
                    image=image
                )

            return redirect('MerchantDashboard')

        else:
            # Helpful while debugging
            print(form.errors)

    else:
        form = PropertyForm()

    context = {
        'merchant': merchant,
        'form': form,
        "accreditations": Accreditation.objects.all(),
        "campuses": Campus.objects.all(),
        "amenities": Amenity.objects.all(),
    }

    return render(request, 'ListAccommodation.html', context)


from django.shortcuts import get_object_or_404

def PropertyDetailView(request, pk):
    property_obj = get_object_or_404(Property, pk=pk, is_approved=True, is_active=True)

    return render(request, "PropertyDetail.html", {
        "property": property_obj
    })