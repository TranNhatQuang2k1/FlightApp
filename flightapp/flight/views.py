from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime
from .models import *


def index(request):
    min_date = f"{datetime.now().date().year}-{datetime.now().date().month}-{datetime.now().date().day}"
    max_date = f"{datetime.now().date().year if (datetime.now().date().month+3)<=12 else datetime.now().date().year+1}-{(datetime.now().date().month + 3) if (datetime.now().date().month+3)<=12 else (datetime.now().date().month+3-12)}-{datetime.now().date().day}"
    if request.method == 'POST':
        origin = request.POST.get('Origin')
        destination = request.POST.get('Destination')
        depart_date = request.POST.get('DepartDate')
        seat = request.POST.get('SeatClass')
        trip_type = request.POST.get('TripType')
        if(trip_type == '1'):
            return render(request, 'flight/index.html', {
                'origin': origin,
                'destination': destination,
                'depart_date': depart_date,
                'seat': seat.lower(),
                'trip_type': trip_type
            })
        elif(trip_type == '2'):
            return_date = request.POST.get('ReturnDate')
            return render(request, 'flight/index.html', {
                'min_date': min_date,
                'max_date': max_date,
                'origin': origin,
                'destination': destination,
                'depart_date': depart_date,
                'seat': seat.lower(),
                'trip_type': trip_type,
                'return_date': return_date
            })
    else:
        return render(request, 'flight/index.html', {
            'min_date': min_date,
            'max_date': max_date
        })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))

        else:
            return render(request, "flight/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "flight/login.html")


def register_view(request):
    if request.method == "POST":
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensuring password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "flight/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            user.save()
        except:
            return render(request, "flight/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "flight/register.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@csrf_exempt
def flight(request):
    o_place = request.GET.get('Origin')
    d_place = request.GET.get('Destination')
    trip_type = request.GET.get('TripType')
    departdate = request.GET.get('DepartDate')
    depart_date = datetime.strptime(departdate, "%Y-%m-%d")
    return_date = None
    seat = request.GET.get('SeatClass')

    flightday = Week.objects.get(number=depart_date.weekday())
    destination = Place.objects.get(code=d_place.upper())
    origin = Place.objects.get(code=o_place.upper())
    if seat == 'economy':
        flights = Flight.objects.filter(depart_day=flightday, origin=origin, destination=destination).exclude(
            economy_fare=0).order_by('economy_fare')
        try:
            max_price = flights.last().economy_fare
            min_price = flights.first().economy_fare
        except:
            max_price = 0
            min_price = 0

    elif seat == 'business':
        flights = Flight.objects.filter(depart_day=flightday, origin=origin, destination=destination).exclude(
            business_fare=0).order_by('business_fare')
        try:
            max_price = flights.last().business_fare
            min_price = flights.first().business_fare
        except:
            max_price = 0
            min_price = 0

    elif seat == 'first':
        flights = Flight.objects.filter(depart_day=flightday, origin=origin, destination=destination).exclude(
            first_fare=0).order_by('first_fare')
        try:
            max_price = flights.last().first_fare
            min_price = flights.first().first_fare
        except:
            max_price = 0
            min_price = 0

    # print(calendar.day_name[depart_date.weekday()])

    return render(request, "flight/search.html", {
        'flights': flights,
        'origin': origin,
        'destination': destination,
        'seat': seat.capitalize(),
        'trip_type': trip_type,
        'depart_date': depart_date,
        'return_date': return_date,
        'max_price': math.ceil(max_price/100)*100,
        'min_price': math.floor(min_price/100)*100
    })
