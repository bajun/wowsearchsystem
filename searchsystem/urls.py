from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
admin.autodiscover()
urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'searchsystem.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
	#url(r'^$', 'searchsystem.views.home', name='home'),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^register/$', 'searchsystem.views.register', name='registration'),
	url(r'^login/$', 'searchsystem.views.user_login', name='login'),
	url(r'^ajax_actions/$', 'searchsystem.views.ajax_actions'),
	url(r'^view/(\S+)/$', 'searchsystem.views.place'),
	url(r'^cabinet/$', 'searchsystem.views.cabinet'),
	url(r'^logout/$', 'searchsystem.views.logout'),
)
urlpatterns += staticfiles_urlpatterns()