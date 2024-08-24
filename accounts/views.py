from django.shortcuts import render, redirect
from .models import HotelUser, HotelVendor, Hotel, Ameneties, HotelImages
from django.db.models import Q
from django.contrib import messages
from .utils import generateRandomToken, sendEmailToken, sendOTPtoEmail
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
import random
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.decorators import login_required

# Create your views here.

def login_page(request):    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        hotel_user = HotelUser.objects.filter(
            email = email)


        if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/account/login/')

        if not hotel_user[0].is_verified:
            messages.warning(request, "Account not verified")
            return redirect('/account/login/')

        hotel_user = authenticate(username = hotel_user[0].username , password=password)

        if hotel_user:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('/account/login/')

        messages.warning(request, "Invalid credentials")
        return redirect('/account/login/')
    return render(request, 'login.html')


def register(request):
    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        hotel_user = HotelUser.objects.filter(
            Q(email = email) | Q(phone_number  = phone_number)
        )

        if hotel_user.exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('/account/register/')

        hotel_user = HotelUser.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()

        sendEmailToken(email , hotel_user.email_token)

        messages.success(request, "An email Sent to your Email")
        return redirect('/account/register/')


    return render(request, 'register.html')


def verify_email_token(request, token):
    try:
        hotel_user = HotelUser.objects.get(email_token=token)
        hotel_user.is_verified = True
        hotel_user.save()
        messages.success(request, "Email verified")
        return redirect('/account/login/')
    except HotelUser.DoesNotExist:
        return HttpResponse("Invalid Token")

def send_otp(request, email):
    hotel_user = HotelUser.objects.filter( email = email )
    if not hotel_user.exists():
        messages.warning(request, "No Account Found.")
        return redirect('/account/login/')

    otp =   random.randint(1000, 9999)
    hotel_user.update(otp = otp)

    sendOTPtoEmail(email, otp)

    return redirect(f'/account/verify-otp/{email}/')

def verify_otp(request, email):
    if request.method == "POST":
        otp = request.POST.get('otp')
        hotel_user = HotelUser.objects.get(email = email)

        if otp == hotel_user.otp:
            messages.success(request, "Login Success")
            login(request, hotel_user)
            return redirect('/account/login/')

        messages.warning(request, "Wrong OTP")
        return redirect(f'/account/verify-otp/{email}/')

    return render(request, 'verify_otp.html')

def login_vendor(request):    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        hotel_user = HotelVendor.objects.filter(
            email = email)


        if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/account/login-vendor/')

        if not hotel_user[0].is_verified:
            messages.warning(request, "Account not verified")
            return redirect('/account/login-vendor/')

        hotel_user = authenticate(username = hotel_user[0].username , password=password)

        if hotel_user:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('/account/dashboard/')

        messages.warning(request, "Invalid credentials")
        return redirect('/account/login-vendor/')
    return render(request, 'vendor/login_vendor.html')

def register_vendor(request):
    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        business_name = request.POST.get('business_name')

        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        hotel_user = HotelUser.objects.filter(
            Q(email = email) | Q(phone_number  = phone_number)
        )

        if hotel_user.exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('/account/register-vendor/')

        hotel_user = HotelVendor.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            business_name = business_name,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()

        sendEmailToken(email , hotel_user.email_token)

        messages.success(request, "An email Sent to your Email")
        return redirect('/account/register-vendor/')


    return render(request, 'vendor/register_vendor.html')

@login_required(login_url = 'login_vendor')
def dashboard(request):
    hotels = Hotel.objects.filter(hotel_owner=request.user)
    context = {'hotels': hotels}
    return render(request, 'vendor/vendor_dashboard.html', context)

@login_required(login_url = 'login_vendor')
def add_hotel(request):
    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        ameneties= request.POST.getlist('ameneties')
        hotel_price= request.POST.get('hotel_price')
        hotel_offer_price= request.POST.get('hotel_offer_price')
        hotel_location= request.POST.get('hotel_location')
        hotel_slug = generateSlug(hotel_name)
        ameneties = request.POST.getlist('amenities')
        for amenti in ameneties:
            amenti = Ameneties.objects.getlist(id = amenti)
            hotel_obj = ameneties.add(amenti)
            hotel_obj.save()

        hotel_vendor = HotelVendor.objects.get(id = request.user.id)

        hotel_obj = Hotel.objects.create(
            hotel_name = hotel_name,
            hotel_description = hotel_description,
            hotel_price = hotel_price,
            hotel_offer_price = hotel_offer_price,
            hotel_location = hotel_location,
            hotel_slug = hotel_slug,
            hotel_owner = hotel_vendor
        )

        messages.success(request, "Hotel Created")
        return redirect('/account/add_hotel/')

    ameneties = Ameneties.objects.all()

    return render(request, 'vendor/add_vendor.html', context = {'ameneties' : ameneties})

@login_required(login_url = 'login_vendor')
def upload_images(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    if request.method == "POST":
        image = request.FILES['image']
        print(image)
        HotelImages.objects.create(
            hotel = hotel_obj,
            image = image
        )
        return HttpResponsePermanentRedirect(request.path_info)

    return render(request, 'vendor/upload_images.html', context = {'images' : hotel_obj.hotel_images.all()})

@login_required(login_url = 'login_vendor')
def delete_image(request, id):
    print(id)
    print("####")
    hotel_image = HotelImages.objects.get(id = id)
    hotel_image.delete()
    messages.success(request, "Hotel Image Deleted")
    return redirect('/account/dashboard')
