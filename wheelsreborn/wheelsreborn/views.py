from email.message import EmailMessage
import re
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import generate_token
from django.contrib.auth.decorators import login_required
from .models import Booking, Profile, Images
from .forms import BookingForm
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from .forms import CustomSetPasswordForm
import pickle
import numpy as np
from roboflow import Roboflow
import os

@login_required(login_url='/')
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.delete()
    return redirect('mybookings')

@login_required(login_url='/')
def my_bookings(request):
    # Assuming the user is logged in
    user_bookings = Booking.objects.filter(user=request.user)

    return render(request, 'my_bookings.html', {'user_bookings': user_bookings})

@login_required(login_url='/')
def booking(request):
    form = BookingForm()

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            return redirect('mybookings')

    return render(request, 'booking.html', {'form': form})

def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]

        # Check if passwords match
        if pass1 != pass2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        # Check if username is already taken
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken")
            return redirect("signup")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email is already taken")
            return redirect("signup")
        elif not re.match("^[a-zA-Z0-9]+$", username):
            messages.error(request, "Username should be alphanumeric")
            return redirect("signup")

        else:
            myuser = User.objects.create_user(username, email, pass1)
            myuser.first_name = fname
            myuser.last_name = lname
            myuser.is_active = True
            myuser.save()
            messages.success(request, "Account Created")

            subject = "Welcome to WheelsReborn!"
            message = "Hello " +  myuser.first_name + "!! \n" + "Welcome to WheelsReborn!! \n Thank you for visiting our website \n We have also sent you a confirmation email, please confirm your email address in order to activate your account. \n\n Thanking You\n Yash Kumar Shukla - CEO & Founder"
            from_email = settings.EMAIL_HOST_USER
            to_list = [myuser.email]
            send_mail(subject, message, from_email, to_list, fail_silently = True)

            #confirmation email
            current_site = get_current_site(request)
            email_subject = "Confirm your email @ WheelsReborn"
            message2 = render_to_string('email_confirmation.html',{
                "name": myuser.first_name,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(myuser.pk)),
                "token": generate_token.make_token(myuser),
            })

            email = EmailMultiAlternatives(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [myuser.email],
            )
            email.fail_silently = True
            email.send()
            messages.success(request, "We have sent a mail to your registered email id. Please verify.")
            return redirect("signin")

    return render(request, "signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            login(request, user)
            return redirect('userhome')
        else:
            messages.error(request,'Username OR Password is incorrect')
            return redirect('signin')
    return render(request, "login.html")

def signout(request):
    logout(request)
    messages.info(request,"Logged Out Successfully")
    return redirect("signin")

@login_required(login_url='/')
def user_home(request):
    return render(request,"user-home.html")

@login_required(login_url='/')
def predict(request):
    return render(request,"predict.html")

@login_required(login_url='/')
def profile(request):
    user = request.user
    context = {'user': user}
    return render(request,"profile.html")

@login_required(login_url='/')
def update_publicinfo(request):
    if request.method == 'POST':
        user = request.user
        context = {'user': user}
        try:
            profile = user.profile
        except ObjectDoesNotExist:
            profile = Profile(user=user)
            profile.save()
            
        profile.bio = request.POST.get('bio')
        profile.profile_image = request.FILES.get('profile_image')
        profile.save()
        return redirect(reverse('profile'))

    return render(request, 'profile.html')

@login_required(login_url='/')
def update_privateinfo(request):
    if request.method == 'POST':
        user = request.user
        context = {'user': user}
        try:
            profile = user.profile
        except ObjectDoesNotExist:
            profile = Profile(user=user)
            profile.save()

        profile = user.profile
        profile.phone = request.POST.get('phone')
        profile.address1 = request.POST.get('address1')
        profile.address2 = request.POST.get('address2')
        profile.city = request.POST.get('city')
        profile.state = request.POST.get('state')
        profile.zip= request.POST.get('zip')
        profile.save()

        return redirect(reverse('profile'))

    return render(request, 'profile.html')

def aboutus(request):
    return render(request,"aboutus.html")

def projectinfo(request):
    return render(request,"projectinfo.html")

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        return redirect("signin")
    
@login_required(login_url='/')  
def change_password(request):
    if request.method == 'POST':
        form = CustomSetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.info(request,"Password do not match. Please try again")
            return redirect('profile')
    else:
        form = CustomSetPasswordForm(request.user)
    return render(request, 'profile.html', {'form': form})

@login_required(login_url='/')
def predict_price(request):
    if request.method == 'POST':
        user = request.user
        try:
           images = user.images
        except ObjectDoesNotExist:
            images = Images(user=user)
            images.save()
        
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        variant = request.POST.get('variant')
        year = request.POST.get('year')
        bt = request.POST.get('bodytype')
        ft = request.POST.get('ft')
        state = request.POST.get('state')
        km = request.POST.get('km')
        owner = request.POST.get('ownertype')
        color = request.POST.get('colour')
        crash_sensor = request.POST.get('crashsensor')
        OutsideTemperatureDisplay = request.POST.get('tempdisplay')
        Air_Quality_Control = request.POST.get('aqc')
        Integrated_Antenna = request.POST.get('integratedantenna')
        Rear_Window_Defogger = request.POST.get('rearwindowdefogger')
        Multifunction_Steering_Wheel = request.POST.get('multifunctionsteeringwheel')
        Driver_Air_Bag = request.POST.get('driverairbag')
        Height_Adjustable_Driver_Seat = request.POST.get('heightadjustabledriverseat')
        Alloy_Wheels = request.POST.get('alloywheels')
        Chrome_Grille = request.POST.get('chromegrille')
        Anti_TheftAlarm =request.POST.get('antitheftalarm')
        AntiLockBrakingSystem = request.POST.get('albs')
        ManuallyAdjustableExteriorRearViewMirror = request.POST.get('extrearmirror')
        RearCamera =request.POST.get('rearcamera')
        RemoteFuelLidOpener =request.POST.get('rflo')
        PowerAntenna =request.POST.get('powerantenna')
        AntiTheftDevice =request.POST.get('atd')
        TrunkLight =request.POST.get('trunklight')
        LeatherSteeringWheel =request.POST.get('lsw')
        RearWindowWiper =request.POST.get('rww')
        RearSeatCentreArmRest =request.POST.get('rscar')
        WheelCovers =request.POST.get('wheelcovers')
        Radio =request.POST.get('radio')
        FogLightsFront =request.POST.get('foglights')
        CdPlayer =request.POST.get('cdplayer')
        VanityMirror =request.POST.get('vanitymirror')
        DayNightRearViewMirror =request.POST.get('dnrvm')
        RearACVents =request.POST.get('rearacvents')
        HeightAdjustableFrontSeatBelts =request.POST.get('hafsb')
        PassengerAirBag =request.POST.get('pab')
        CupHoldersRear =request.POST.get('rch')
        OutsideRearViewMirrorTurnIndicators =request.POST.get('orvmti')
        EngineCheckWarning =request.POST.get('ecw')
        PretensionersAndForceLimiterSeatbelts =request.POST.get('pafls')
        RearWindowWasher =request.POST.get('rearwindowwasher')
        RearSpoiler =request.POST.get('rearspoiler')
        ElectricFoldingRearViewMirror =request.POST.get('efrvm')
        DoorAjarWarning =request.POST.get('daw')
        TintedGlass =request.POST.get('tg')
        Rear_Reading_Lamp =request.POST.get('rrl')
        Keyless_Entry =request.POST.get('ke')
        Ebd =request.POST.get('ebd')
        Remote_Trunk_Opener =request.POST.get('rto')
        Power_Adjustable_Exterior_Rear_View_Mirror =request.POST.get('paervm')

        images.car_image1 = request.FILES.get('image1')
        images.car_image2 = request.FILES.get('image2')
        images.car_image3 = request.FILES.get('image3')
        images.car_image4 = request.FILES.get('image4')
        images.save()

        rf = Roboflow(api_key="jVkv6dqMu0wCCyeaGf85")
        project = rf.workspace().project("detection-m16cd")
        model = project.version(1).model

        rf = Roboflow(api_key="jVkv6dqMu0wCCyeaGf85")
        project = rf.workspace().project("detection-m16cd")
        model = project.version(1).model

        path1 = images.car_image1.path
        path2 = images.car_image2.path
        path3 = images.car_image3.path
        path4 = images.car_image4.path

        car_image5 = model.predict(path1, confidence=40, overlap=30).save("media/prediction1.jpg")
        car_image6 = model.predict(path2, confidence=40, overlap=30).save("media/prediction2.jpg")
        car_image7 = model.predict(path3, confidence=40, overlap=30).save("media/prediction3.jpg")
        car_image8 = model.predict(path4, confidence=40, overlap=30).save("media/prediction4.jpg")

        prediction_image1_path = os.path.join(settings.MEDIA_URL, "prediction1.jpg")
        prediction_image2_path = os.path.join(settings.MEDIA_URL, "prediction2.jpg")
        prediction_image3_path = os.path.join(settings.MEDIA_URL, "prediction3.jpg")
        prediction_image4_path = os.path.join(settings.MEDIA_URL, "prediction4.jpg")

        mapping_name = 'mappings.pkl'
        with open(mapping_name, 'rb') as file:
            mapping = pickle.load(file)

        mapped_brand = mapping['brand'].get(brand, 0)
        mapped_model = mapping['model'].get(model, 0)
        mapped_variant = mapping['variant'].get(variant, 0)
       
        input_data = np.array([year,km,owner,crash_sensor,OutsideTemperatureDisplay,Air_Quality_Control,
                               Integrated_Antenna,Rear_Window_Defogger,Multifunction_Steering_Wheel,
                               Driver_Air_Bag,Height_Adjustable_Driver_Seat,Alloy_Wheels,Chrome_Grille,
                               Anti_TheftAlarm,AntiLockBrakingSystem,ManuallyAdjustableExteriorRearViewMirror,
                               RearCamera,RemoteFuelLidOpener,PowerAntenna,AntiTheftDevice,TrunkLight,LeatherSteeringWheel,
                               RearWindowWiper,RearSeatCentreArmRest,WheelCovers,Radio,FogLightsFront,CdPlayer,VanityMirror,
                               DayNightRearViewMirror,RearACVents,HeightAdjustableFrontSeatBelts,PassengerAirBag,CupHoldersRear,
                               OutsideRearViewMirrorTurnIndicators,EngineCheckWarning,PretensionersAndForceLimiterSeatbelts,RearWindowWasher,
                               RearSpoiler,ElectricFoldingRearViewMirror,DoorAjarWarning,TintedGlass,Rear_Reading_Lamp,Keyless_Entry,Ebd,
                               Remote_Trunk_Opener,Power_Adjustable_Exterior_Rear_View_Mirror,bt,ft,color,mapped_brand,mapped_model,mapped_variant,state]).reshape(1, -1)
        
        data_numeric = np.array(input_data).astype(int)

        with open('model.pkl', 'rb') as file:
            loaded_model = pickle.load(file)

        predicted_price = loaded_model.predict(data_numeric)[0]
        output = round(predicted_price, 2)

        return render(
            request,
            'predict.html',
            {
                'predicted_price': output,
                'prediction_image1_path': prediction_image1_path,
                'prediction_image2_path': prediction_image2_path,
                'prediction_image3_path': prediction_image3_path,
                'prediction_image4_path': prediction_image4_path
            }
        )

    return render(request, 'predict.html')