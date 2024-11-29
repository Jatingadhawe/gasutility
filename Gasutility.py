# Import necessary libraries
import os
from django.conf import settings
from django.db import models
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

# Settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Models
class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

# Forms
class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['request_type', 'description']

# Views
@login_required
def submit_request(request):
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.user = request.user
            service_request.save()
            send_mail('Service Request Submitted', 'Your request has been submitted.', settings.DEFAULT_FROM_EMAIL, [request.user.email])
            return redirect('request_list')
    else:
        form = ServiceRequestForm()
    return render(request, 'submit_request.html', {'form': form})

@login_required
def request_list(request):
    requests = ServiceRequest.objects.filter(user=request.user)
    return render(request, 'request_list.html', {'requests': requests})

@login_required
def request_detail(request, request_id):
    service_request = ServiceRequest.objects.get(id=request_id)
    return render(request, 'request_detail.html', {'request': service_request})

# URL patterns
urlpatterns = [
    path('submit_request/', submit_request, name='submit_request'),
    path('request_list/', request_list, name='request_list'),
    path('request_detail/<int:request_id>/', request_detail, name='request_detail'),
]

# Admin
admin.site.register(ServiceRequest)
admin.site.register(Account)

# Settings for email
settings.configure(
    DEFAULT_FROM_EMAIL='noreply@gasutilities.com',
    EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',
    EMAIL_HOST='smtp.gmail.com',
    EMAIL_PORT=587,
    EMAIL_USE_TLS=True,
    EMAIL_HOST_USER='your_email@gmail.com',
    EMAIL_HOST_PASSWORD='your_password',
)
