from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from .forms import UserForm
from urllib.parse import urlparse, parse_qs
from searchsystem.models import Account, Place, Review, UserAdd, Category, CategoryPlace
from django.core.exceptions import ObjectDoesNotExist
from paypal.standard.forms import PayPalPaymentsForm
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


import urllib.request
import json
import datetime
import calendar


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def home(request):
    context = RequestContext(request)
    return render_to_response('home/home.html', {}, context)


def register(request):
    context = RequestContext(request)
    errorstring = ''
    result = ''
    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            result = 'Now you can login with your credentials'
        else:
            errorstring = user_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()

    t_vars = {'user_form': user_form, 'result': result, 'errorstring': errorstring}
    return render_to_response('registration/registration.html', t_vars, context)


def user_login(request):
    context = RequestContext(request)
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            errorstring = ("Invalid login details: {0}, {1}".format(username, password))
            return render_to_response('registration/login.html', {'errorstring': errorstring}, context)

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('registration/login.html', {}, context)


def ajax_actions(request):
    context = RequestContext(request)
    # Parse some data
    action_request = urlparse(request.META['QUERY_STRING'])
    action_result = parse_qs(action_request.path)
    # Prepare vars to use
    id_item = action_result['id']
    method = action_result['method']
    return render_to_response('ajax.html', {'method': method, 'id': id_item}, context)


def place(request, g_id):
    context = RequestContext(request)
    account = Account.objects.get(email=request.user)
    try:
        place_data = Place.objects.get(id_google=g_id)
        title = place_data.title
        adress = place_data.adress
        place_object = Place.objects.get(id_google=g_id)
        user_view = UserAdd(user_id=account, place_id=place_object)
        user_view.save()
        t_vars = {'title': title, 'adress': adress, 'current_acc': request.user}
        return render_to_response('place/index.html', t_vars, context)
    except ObjectDoesNotExist:
        place_data_json_link = "https://maps.googleapis.com/maps/api/place/details/json?reference="+g_id+"&sensor=true&key="+settings.GOOGLE_API_KEY
        place_data_json = urllib.request.urlopen(place_data_json_link).read().decode('utf-8')
        place_data_python = json.loads(place_data_json)
        place_data = place_data_python['result']
        place_object = Place.objects.create(adress=place_data['formatted_address'], id_google=g_id, title=place_data['name'])
        for data in place_data['types']:
            category = Category.objects.get_or_create(title=data)
            category_place = CategoryPlace(category=category[0], place=place_object)
            category_place.save()

        user_view = UserAdd(user_id=account, place_id=place_object)
        user_view.save()
        t_vars = {'adress': place_data['formatted_address'], 'title': place_data['name'], 'current_acc': request.user}
        return render_to_response('place/index.html', t_vars, context)


@csrf_exempt
def cabinet(request):
    context = RequestContext(request)
    activate_date = datetime.date.today()
    result_places = list()
    account = Account.objects.get(email=request.user)

    if 'custom' in request.POST:
        account.is_premium = True
        if request.POST['custom'] == 'update_premium_month':
            account.premium_expires = add_months(activate_date, 1)
        else:
            account.premium_expires = add_months(activate_date, 12)
        account.save(update_fields=['is_premium', 'premium_expires'])

    if 'nationality' in request.POST:
        account.nationality = request.POST['nationality']
        account.save(update_fields=['nationality'])

    fields = account._meta.local_fields
    field_names = [[field.name, field.verbose_name, getattr(account, field.name)] for field in fields if(field.name not in('is_premium', 'updated_at', 'password', 'id', 'premium_expires'))]
    premium_data = [getattr(account, 'is_premium'), getattr(account, 'premium_expires')]
    if getattr(account, 'is_premium') is True:
        result = UserAdd.objects.filter(user_id=request.user)
        result_places = [[r.place_id.title, r.place_id.id_google] for r in result]
    nationality = getattr(account, 'nationality')
    return render_to_response('cabinet/index.html', {'data': field_names, 'premium_data': premium_data, 'searches': result_places,'nationality': nationality}, context)


def pay_view(request):
    # What you want the button to do.
    paypal_dict_month = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": "1.99",
        "item_name": "Monthly pay",
        "notify_url": "/paypal" + reverse('paypal-ipn'),
        "custom": "update_premium_month",
        "return_url": request.build_absolute_uri(reverse('searchsystem.views.cabinet')),
        "cancel_return": request.build_absolute_uri(reverse('searchsystem.views.cancel_pay')),
    }
    paypal_dict_annum = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": "10.99",
        "item_name": "Year pay",
        "notify_url": "/paypal" + reverse('paypal-ipn'),
        "custom": "update_premium_year",
        "return_url": request.build_absolute_uri(reverse('searchsystem.views.cabinet')),
        "cancel_return": request.build_absolute_uri(reverse('searchsystem.views.cancel_pay')),
    }
    # Create the instance.
    form_month = PayPalPaymentsForm(initial=paypal_dict_month)
    form_annum = PayPalPaymentsForm(initial=paypal_dict_annum)
    context = {"form_month": form_month, "form_annum": form_annum}
    return render_to_response("payment/index.html", context)


def return_pay(request):
    context = RequestContext(request)
    return render_to_response("payment/success.html", {'result': request}, context)


def cancel_pay(request):
    pass

@login_required
def most_searched(request):
    context = RequestContext(request)
    result = {}
    views = UserAdd.objects.filter(user_id=request.user)
    objects = [Place.objects.filter(title=v.place_id) for v in views]
    categories_places = [CategoryPlace.objects.filter(place=o) for o in objects]
    categories_objects = [j for i in categories_places for j in i]
    categories = [Category.objects.filter(title=t.category).values_list('title') for t in categories_objects]

    for c in categories:
        title = c[0][0]
        if title in result.keys():
            result[title]+=1
        else:
            result[title]= 1
    sorted_c = sorted(result.items(), key=lambda x: x[1],reverse=True)
    account = Account.objects.get(email=request.user)
    is_premium = account.is_premium

    return render_to_response("premium/index.html",{'searchcategories': sorted_c, 'is_premium':is_premium},context)

def search(request,id):
    context = RequestContext(request)
    place_data_json_link = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?types="+id+"&key="+settings.GOOGLE_API_KEY
    place_data_json = urllib.request.urlopen(place_data_json_link).read().decode('utf-8')
    place_data_python = json.loads(place_data_json)

    return render_to_response("premium/search.html",{},context)