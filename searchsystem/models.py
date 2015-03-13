from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.utils.translation import ugettext_lazy as _

class AccountManager(BaseUserManager):
	def create_user(self, email, password=None, **kwargs):
		if not email:
			raise ValueError('User must have a valid email address.')
		if not kwargs.get('username'):
			raise ValueError('User must have a valid username.')

		account = self.model(
			email=self.normalize_email(email), username=kwargs.get('username')
		)

		account.set_password(password)
		account.save()

		return account

	def create_superuser(self, email, password, **kwargs):
		account = self.create_user(email, password, **kwargs)

		account.is_admin = True
		account.save()

		return account

class Account(AbstractBaseUser):
	email = models.EmailField(unique=True)
	username = models.CharField("Username",max_length=40, unique=True)

	first_name = models.CharField("First name",max_length=40, blank=True)
	last_name = models.CharField("Last name",max_length=40, blank=True)

	is_premium = models.BooleanField(default=False)
	premium_expires = models.DateTimeField(null=True)

	is_admin = models.BooleanField(default=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	objects = AccountManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username', ]

	def __str__(self):
		return self.email
	
	def get_all(self):
		return self
	
	def get_full_name(self):
		return ' '.join([self.first_name, self.last_name])

	def get_short_name(self):
		return self.first_name
	
	@property
	def is_superuser(self):
		return self.is_admin

	@property
	def is_staff(self):
		return self.is_admin

	def has_perm(self, perm, obj=None):
		return self.is_admin

	def has_module_perms(self, app_label):
		return self.is_admin


class Place(models.Model):
	author = models.ManyToManyField(Account,through="UserAdd")
	adress = models.TextField()
	id_google = models.CharField(max_length = 255)
	title = models.CharField(max_length = 255)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '{0}'.format(self.title)
	
	def __str__(self):
		return self.title
	
class UserAdd(models.Model):
	user_id = models.ForeignKey(Account)
	place_id = models.ForeignKey(Place)
	
class Review(models.Model):
	place = models.ForeignKey(Place)
	content = models.TextField()

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '{0}'.format(self.content)
	
	def __str__(self):
		return '{0}'.format(self.content)
	
# i dunno where to put signals,so they will be here

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received

def set_premium(sender,instance,**kwargs):
	ipn_obj = sender
	f = open('workfile', 'w')
	f.write(str(instance))
	if ipn_obj.payment_status == ST_PP_COMPLETED:
		# Undertake some action depending upon `ipn_obj`.
		if ipn_obj.custom == "update_premium_month":
			account = Account.objects.get(email=instance.user)
			account.objects.update(is_premium=True)
		else:
			pass

valid_ipn_received.connect(set_premium)