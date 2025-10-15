from django.contrib import admin
from django.urls import path
from matches import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing, name='landing'),
]
