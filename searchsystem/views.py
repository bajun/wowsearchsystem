from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from .forms import UserForm
from urllib.parse import urlparse,parse_qs
from searchsystem.models import Account,Place,Review,UserAdd
from django.core.exceptions import ObjectDoesNotExist

import urllib.request
import json

def home(request):
	return render_to_response('home/home.html')

def register(request):
	context = RequestContext(request)
    
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
	result = False
    # If it's a HTTP POST, we're interested in processing form data.
	if request:
		if request.method == 'POST':
			result = True
			user_form = UserForm(data=request.POST)
			if user_form.is_valid() :
			   
				# Save the user's form data to the database.
				user = user_form.save()
		   
				# Now we hash the password with the set_password method.
				# Once hashed, we can update the user object.
				user.set_password(user.password)
				user.save()
		   
			# Invalid form or forms - mistakes or something else?
			# Print problems to the terminal.
			# They'll also be shown to the user.
			else:
				print(user_form.errors)
		
		# Not a HTTP POST, so we render our form using two ModelForm instances.
		# These forms will be blank, ready for user input.
		else:
			result = 'no,not post'
			user_form = UserForm()
	    
	return render_to_response('registration/registration.html',{'user_form':user_form,'result':result},context)

def user_login(request):
	# Like before, obtain the context for the user's request.
	context = RequestContext(request)

	# If the request is a HTTP POST, try to pull out the relevant information.
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
			print ("Invalid login details: {0}, {1}".format(username, password))
			return HttpResponse("Invalid login details supplied.")

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
	id = action_result['id']
	method = action_result['method']
	
	return render_to_response('ajax.html',{'method': method,'id':id},context)

def place(request,id):
	context = RequestContext(request)
	review_request = urlparse(request.META['QUERY_STRING'])
	
	try:
		place_data = Place.objects.get(id_google=id)
		title = place_data.title
		adress = place_data.adress
		return render_to_response('place/index.html',{'title' : title,'adress':adress,'current_acc':request.user},context)
	except ObjectDoesNotExist:
		place_data_json = urllib.request.urlopen("https://maps.googleapis.com/maps/api/place/details/json?reference="+id+"&sensor=true&key="+settings.GOOGLE_API_KEY).read().decode('utf-8')
		place_data_python = json.loads(place_data_json)
		place_data = place_data_python['result']
		account = Account.objects.get(email=request.user)
		place_object = Place.objects.create(adress=place_data['formatted_address'],id_google=id,title=place_data['name'])
		user_view = UserAdd(user_id=account,place_id=place_object)
		user_view.save()
		return render_to_response('place/index.html',{'adress' : place_data['formatted_address'],'title':place_data['name'],'current_acc':request.user},context)

def cabinet(request):
	context = RequestContext(request)
	result_ = list()
	account = Account.objects.get(email=request.user)
	fields = account._meta.local_fields
	field_names = [[field.name,field.verbose_name, getattr(account,field.name)] for field in fields if(field.name not in('is_premium','updated_at','password','id','premium_expires'))]
	premium_data = [getattr(account,'is_premium'),getattr(account,'premium_expires')]
	if(getattr(account,'is_premium') == True):
		result = UserAdd.objects.filter(user_id=request.user)
		result_places = [[r.place_id.adress] for r in result]
		# result = UserAdd.objects.raw('SELECT * FROM searchsystem_useradd where user_id_id=%s',[request.user])
		# for r in result:
			# result_.append(r)
	return render_to_response('cabinet/index.html',{'data':field_names,'premium_data': premium_data,'searches':result_places},context)

def logout(request):
	pass