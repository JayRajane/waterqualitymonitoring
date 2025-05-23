# monitoring_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class CustomUser(AbstractUser):
    ADMIN = 1
    USER = 2
    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (USER, 'User'),
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=USER)
    address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    state_code = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    
    show_ph = models.BooleanField(default=True)
    show_cod = models.BooleanField(default=True)
    show_bod = models.BooleanField(default=True)
    show_tss = models.BooleanField(default=True)
    show_flow1 = models.BooleanField(default=True)
    show_flow2 = models.BooleanField(default=True)
    show_flow3 = models.BooleanField(default=True)
    show_flow4 = models.BooleanField(default=True)
    show_flow5 = models.BooleanField(default=True)
    show_flow6 = models.BooleanField(default=True)
    show_flow7 = models.BooleanField(default=True)
    show_flow8 = models.BooleanField(default=True)
    show_flow9 = models.BooleanField(default=True)
    show_flow10 = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.set_password(f"{self.username}@123")
            if self.role == self.ADMIN:
                self.is_staff = True
                self.is_superuser = True
        super().save(*args, **kwargs)
        if not self.pk:
            self.send_credentials_email()
    
    def send_credentials_email(self):
        subject = 'Your Water Quality Monitoring System Credentials'
        context = {
            'username': self.username,
            'password': f"{self.username}@123",
            'login_url': settings.LOGIN_URL
        }
        html_message = render_to_string('monitoring_app/credentials_email.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            html_message=html_message,
            fail_silently=False,
        )
    
    @property
    def is_admin(self):
        return self.role == self.ADMIN
    
    @property
    def is_regular_user(self):
        return self.role == self.USER

class Machine(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, default=None)
    
    def __str__(self):
        return self.name or "Unnamed Machine"
    
    class Meta:
        managed = True
        db_table = 'machine'

class Reading(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, db_column='user_id')
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, db_column='machine_id')
    parameter = models.CharField(max_length=50)
    value = models.FloatField(blank=True, null=True, default=None)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.machine.name} - {self.parameter} - {self.value}"
    
    class Meta:
        managed = True
        db_table = 'reading'
        indexes = [
            models.Index(fields=['user', 'parameter', 'recorded_at']),
            models.Index(fields=['machine', 'parameter', 'recorded_at']),
        ]

class FlowMeterConfig(models.Model):
    machine = models.OneToOneField(Machine, on_delete=models.CASCADE)
    port = models.CharField(max_length=50, default='/dev/ttyUSB0')
    slave_id = models.PositiveIntegerField(default=1)
    flow_register = models.PositiveIntegerField(default=2)
    total_register = models.PositiveIntegerField(default=3)

class WaterQualityData(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    ph = models.FloatField(null=True, blank=True)
    cod = models.FloatField(null=True, blank=True)
    bod = models.FloatField(null=True, blank=True)
    tss = models.FloatField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Data for {self.user.username} at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        if self.date is None:
            self.date = timezone.now().date()
        super().save(*args, **kwargs)