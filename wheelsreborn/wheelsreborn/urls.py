"""
URL configuration for wheelsanddeals project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.signin, name='signin'),
    path('sign-up/', views.signup, name='signup'),
    path('sign-out/', views.signout, name='signout'),
    path("user-home/", views.user_home, name = 'userhome'),
    path("predict-price/", views.predict, name='predict'),
    path("profile-settings/", views.profile, name='profile'),
    path("about-us/", views.aboutus, name='aboutus'),
    path("project-info/", views.projectinfo, name='projectinfo'),
    path("activate/<uidb64>/<token>", views.activate, name='activate'),
    path("my-bookings/", views.my_bookings, name='mybookings'),
    path("booking-inspection/", views.booking, name='booking'),
    path("delete-booking/<int:booking_id>/", views.delete_booking, name='delete_booking'),
    path('update-privateinfo/', views.update_privateinfo, name='update_privateinfo'),
    path('update-publicinfo/', views.update_publicinfo, name='update_publicinfo'),
    path('changepassword/', views.change_password, name='change_password'),
    path('prediction/', views.predict_price, name='prediction'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)