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
    
    # Add fields for parameter selection
    show_ph = models.BooleanField(default=True)
    show_flow = models.BooleanField(default=True)
    show_cod = models.BooleanField(default=True)
    show_bod = models.BooleanField(default=True)
    show_tss = models.BooleanField(default=True)
    show_daily_flow = models.BooleanField(default=True)
    show_total_flow = models.BooleanField(default=True)
    show_monthly_flow = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        # If flow is selected, automatically select daily_flow, total_flow, and monthly_flow
        if self.show_flow:
            self.show_daily_flow = True
            self.show_total_flow = True
            self.show_monthly_flow = True
            
        if not self.pk:  # Only on creation
            self.set_password(f"{self.username}@123")
            if self.role == self.ADMIN:
                self.is_staff = True
                self.is_superuser = True
        super().save(*args, **kwargs)
        
        # Send email with credentials to new users
        if not self.pk:  # Only on creation
            self.send_credentials_email()
    
    def send_credentials_email(self):
        subject = 'Your Water Quality Monitoring System Credentials'
        context = {
            'username': self.username,
            'password': f"{self.username}@123",
            'login_url': settings.LOGIN_URL
        }
        html_message = render_to_string('monitoring_app/email/credentials_email.html', context)
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

class WaterQualityData(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    ph = models.FloatField(null=True, blank=True)
    flow = models.FloatField(null=True, blank=True)
    total_flow = models.FloatField(null=True, blank=True)
    cod = models.FloatField(null=True, blank=True)
    bod = models.FloatField(null=True, blank=True)
    tss = models.FloatField(null=True, blank=True)
    daily_flow = models.FloatField(null=True, blank=True)
    monthly_flow = models.FloatField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Data for {self.user.username} at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        # Ensure date is set before proceeding
        if self.date is None:
            self.date = timezone.now().date()  # Set to current date if None

        print(f"Saving data for user {self.user.username} on {self.date}")  # Debug

        # Calculate daily_flow and monthly_flow
        if self.flow is not None:
            # Daily flow calculation
            start_of_day = timezone.datetime.combine(self.date, timezone.datetime.min.time())
            end_of_day = timezone.datetime.combine(self.date, timezone.datetime.max.time())
            # Monthly flow calculation
            start_of_month = timezone.datetime(self.date.year, self.date.month, 1)
            end_of_month = timezone.datetime(self.date.year, self.date.month + 1, 1) - timezone.timedelta(seconds=1)
            
            # Use timezone-aware datetime if USE_TZ = True
            if settings.USE_TZ:
                start_of_day = timezone.make_aware(start_of_day)
                end_of_day = timezone.make_aware(end_of_day)
                start_of_month = timezone.make_aware(start_of_month)
                end_of_month = timezone.make_aware(end_of_month)

            print(f"Calculating flows between {start_of_day} and {end_of_day} (daily), {start_of_month} and {end_of_month} (monthly)")  # Debug

            # Get all records for this user on this day/month, excluding this instance if it's an update
            existing_daily_records = WaterQualityData.objects.filter(
                user=self.user,
                timestamp__range=(start_of_day, end_of_day)
            ).exclude(id=self.id if self.id else None)

            existing_monthly_records = WaterQualityData.objects.filter(
                user=self.user,
                timestamp__range=(start_of_month, end_of_month)
            ).exclude(id=self.id if self.id else None)

            # Sum existing flows and add the current flow
            daily_flow_sum = existing_daily_records.aggregate(models.Sum('flow'))['flow__sum'] or 0
            self.daily_flow = daily_flow_sum + self.flow

            monthly_flow_sum = existing_monthly_records.aggregate(models.Sum('flow'))['flow__sum'] or 0
            self.monthly_flow = monthly_flow_sum + self.flow

            print(f"Daily flow: {self.daily_flow} (existing sum: {daily_flow_sum}, current flow: {self.flow})")  # Debug
            print(f"Monthly flow: {self.monthly_flow} (existing sum: {monthly_flow_sum}, current flow: {self.flow})")  # Debug
        else:
            # If no flow is provided, set flows to None
            self.daily_flow = None
            self.monthly_flow = None

        super().save(*args, **kwargs)