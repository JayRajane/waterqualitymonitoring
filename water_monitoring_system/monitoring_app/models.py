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
    
    # Parameter visibility flags
    show_ph = models.BooleanField(default=True)
    show_flow1 = models.BooleanField(default=True)
    show_flow2 = models.BooleanField(default=True)
    show_flow3 = models.BooleanField(default=True)
    show_cod = models.BooleanField(default=True)
    show_bod = models.BooleanField(default=True)
    show_tss = models.BooleanField(default=True)
    show_daily_flow1 = models.BooleanField(default=True)
    show_daily_flow2 = models.BooleanField(default=True)
    show_daily_flow3 = models.BooleanField(default=True)
    show_monthly_flow1 = models.BooleanField(default=True)
    show_monthly_flow2 = models.BooleanField(default=True)
    show_monthly_flow3 = models.BooleanField(default=True)
    show_total_flow1 = models.BooleanField(default=True)
    show_total_flow2 = models.BooleanField(default=True)
    show_total_flow3 = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        # Ensure flow-related flags are consistent
        if self.show_flow1:
            self.show_daily_flow1 = True
            self.show_monthly_flow1 = True
            self.show_total_flow1 = True
        if self.show_flow2:
            self.show_daily_flow2 = True
            self.show_monthly_flow2 = True
            self.show_total_flow2 = True
        if self.show_flow3:
            self.show_daily_flow3 = True
            self.show_monthly_flow3 = True
            self.show_total_flow3 = True
            
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
    flow1 = models.FloatField(null=True, blank=True)
    flow2 = models.FloatField(null=True, blank=True)
    flow3 = models.FloatField(null=True, blank=True)
    total_flow1 = models.FloatField(null=True, blank=True)
    total_flow2 = models.FloatField(null=True, blank=True)
    total_flow3 = models.FloatField(null=True, blank=True)
    cod = models.FloatField(null=True, blank=True)
    bod = models.FloatField(null=True, blank=True)
    tss = models.FloatField(null=True, blank=True)
    daily_flow1 = models.FloatField(null=True, blank=True)
    daily_flow2 = models.FloatField(null=True, blank=True)
    daily_flow3 = models.FloatField(null=True, blank=True)
    monthly_flow1 = models.FloatField(null=True, blank=True)
    monthly_flow2 = models.FloatField(null=True, blank=True)
    monthly_flow3 = models.FloatField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Data for {self.user.username} at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        if self.date is None:
            self.date = timezone.now().date()

        start_of_day = timezone.datetime.combine(self.date, timezone.datetime.min.time())
        end_of_day = timezone.datetime.combine(self.date, timezone.datetime.max.time())
        start_of_month = timezone.datetime(self.date.year, self.date.month, 1)
        end_of_month = timezone.datetime(self.date.year, self.date.month + 1, 1) - timezone.timedelta(seconds=1)
        
        if settings.USE_TZ:
            start_of_day = timezone.make_aware(start_of_day)
            end_of_day = timezone.make_aware(end_of_day)
            start_of_month = timezone.make_aware(start_of_month)
            end_of_month = timezone.make_aware(end_of_month)

        # Calculate flows for Flow1
        if self.flow1 is not None:
            existing_daily_records = WaterQualityData.objects.filter(
                user=self.user,
                timestamp__range=(start_of_day, end_of_day)
            ).exclude(id=self.id if self.id else None)

            existing_monthly_records = WaterQualityData.objects.filter(
                user=self.user,
                timestamp__range=(start_of_month, end_of_month)
            ).exclude(id=self.id if self.id else None)

            daily_flow1_sum = sum(r.flow1 or 0 for r in existing_daily_records)
            self.daily_flow1 = daily_flow1_sum + self.flow1

            monthly_flow1_sum = sum(r.flow1 or 0 for r in existing_monthly_records)
            self.monthly_flow1 = monthly_flow1_sum + self.flow1

            latest_record = WaterQualityData.objects.filter(user=self.user).order_by('-timestamp').first()
            self.total_flow1 = (latest_record.total_flow1 or 0) + self.flow1 if latest_record else self.flow1
        else:
            self.daily_flow1 = None
            self.monthly_flow1 = None
            self.total_flow1 = None

        # Calculate flows for Flow2
        if self.flow2 is not None:
            existing_daily_records = WaterQualityData.objects.filter(
                user=self.user,
                timestamp__range=(start_of_day, end_of_day)
            ).exclude(id=self.id if self.id else None)

            existing_monthly_records = WaterQualityData.objects.filter(
                user=self.user,
                timestamp__range=(start_of_month, end_of_month)
            ).exclude(id=self.id if self.id else None)

            daily_flow2_sum = sum(r.flow2 or 0 for r in existing_daily_records)
            self.daily_flow2 = daily_flow2_sum + self.flow2

            monthly_flow2_sum = sum(r.flow2 or 0 for r in existing_monthly_records)
            self.monthly_flow2 = monthly_flow2_sum + self.flow2

            latest_record = WaterQualityData.objects.filter(user=self.user).order_by('-timestamp').first()
            self.total_flow2 = (latest_record.total_flow2 or 0) + self.flow2 if latest_record else self.flow2
        else:
            self.daily_flow2 = None
            self.monthly_flow2 = None
            self.total_flow2 = None

        # Calculate flows for Flow3
        if self.flow3 is not None:
            existing_daily_records = WaterQualityData.objects.filter(
                user=self.user,
                timestamp__range=(start_of_day, end_of_day)
            ).exclude(id=self.id if self.id else None)

            existing_monthly_records = WaterQualityData.objects.filter(
                user=self.user,
                timestamp__range=(start_of_month, end_of_month)
            ).exclude(id=self.id if self.id else None)

            daily_flow3_sum = sum(r.flow3 or 0 for r in existing_daily_records)
            self.daily_flow3 = daily_flow3_sum + self.flow3

            monthly_flow3_sum = sum(r.flow3 or 0 for r in existing_monthly_records)
            self.monthly_flow3 = monthly_flow3_sum + self.flow3

            latest_record = WaterQualityData.objects.filter(user=self.user).order_by('-timestamp').first()
            self.total_flow3 = (latest_record.total_flow3 or 0) + self.flow3 if latest_record else self.flow3
        else:
            self.daily_flow3 = None
            self.monthly_flow3 = None
            self.total_flow3 = None

        super().save(*args, **kwargs)
    
    def calibrate_total_flow(self, flow_number, new_total):
        """Calibrate the total flow for a specific flow stream and update daily/monthly flows."""
        if flow_number not in [1, 2, 3]:
            raise ValueError("Invalid flow number. Must be 1, 2, or 3.")
        
        field_map = {
            1: ('total_flow1', 'daily_flow1', 'monthly_flow1', 'flow1'),
            2: ('total_flow2', 'daily_flow2', 'monthly_flow2', 'flow2'),
            3: ('total_flow3', 'daily_flow3', 'monthly_flow3', 'flow3'),
        }
        
        total_field, daily_field, monthly_field, flow_field = field_map[flow_number]
        
        # Update total flow
        setattr(self, total_field, new_total)
        
        # Recalculate daily and monthly flows
        start_of_day = timezone.datetime.combine(self.date, timezone.datetime.min.time())
        end_of_day = timezone.datetime.combine(self.date, timezone.datetime.max.time())
        start_of_month = timezone.datetime(self.date.year, self.date.month, 1)
        end_of_month = timezone.datetime(self.date.year, self.date.month + 1, 1) - timezone.timedelta(seconds=1)
        
        if settings.USE_TZ:
            start_of_day = timezone.make_aware(start_of_day)
            end_of_day = timezone.make_aware(end_of_day)
            start_of_month = timezone.make_aware(start_of_month)
            end_of_month = timezone.make_aware(end_of_month)

        existing_daily_records = WaterQualityData.objects.filter(
            user=self.user,
            timestamp__range=(start_of_day, end_of_day)
        ).exclude(id=self.id if self.id else None)

        existing_monthly_records = WaterQualityData.objects.filter(
            user=self.user,
            timestamp__range=(start_of_month, end_of_month)
        ).exclude(id=self.id if self.id else None)

        daily_sum = sum(getattr(r, flow_field) or 0 for r in existing_daily_records)
        monthly_sum = sum(getattr(r, flow_field) or 0 for r in existing_monthly_records)
        
        setattr(self, daily_field, daily_sum + (getattr(self, flow_field) or 0))
        setattr(self, monthly_field, monthly_sum + (getattr(self, flow_field) or 0))
        
        super().save()