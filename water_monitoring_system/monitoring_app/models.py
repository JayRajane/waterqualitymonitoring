from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class WaterQualityData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    ph = models.FloatField()
    flow = models.FloatField()
    total_flow = models.FloatField()
    cod = models.FloatField()
    bod = models.FloatField()
    tss = models.FloatField()
    daily_flow = models.FloatField(default=0)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Data for {self.user.username} at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        # If this is a new record, calculate daily flow
        if not self.pk:
            # Get the start and end of the current day
            today = timezone.now().date()
            start_of_day = timezone.datetime.combine(today, timezone.datetime.min.time())
            end_of_day = timezone.datetime.combine(today, timezone.datetime.max.time())
            
            # Calculate daily flow - sum of all flow entries for the day
            daily_total = WaterQualityData.objects.filter(
                user=self.user,
                timestamp__range=(start_of_day, end_of_day)
            ).aggregate(models.Sum('flow'))['flow__sum'] or 0
            
            # Add the current flow value
            self.daily_flow = daily_total + self.flow
            
            # Update total flow
            latest_record = WaterQualityData.objects.filter(user=self.user).order_by('-timestamp').first()
            if latest_record:
                self.total_flow = latest_record.total_flow + self.flow
            else:
                self.total_flow = self.flow
        
        super().save(*args, **kwargs)