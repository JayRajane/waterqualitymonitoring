import os
import django
from datetime import datetime, timedelta
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'water_monitoring_system.settings')
django.setup()

from django.contrib.auth.models import User
from monitoring_app.models import WaterQualityData

def create_users():
    """Create sample users if they don't exist."""
    users = [
        {'username': 'plant1', 'email': 'plant1@example.com', 'password': 'password123'},
        {'username': 'plant2', 'email': 'plant2@example.com', 'password': 'password123'},
    ]
    
    created_users = []
    for user_data in users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            email=user_data['email']
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"Created user: {user.username}")
        else:
            print(f"User already exists: {user.username}")
        created_users.append(user)
    
    return created_users

def create_sample_data(users):
    """Create sample water quality data for users."""
    # Start date for data generation
    start_date = datetime.now() - timedelta(days=30)
    
    for user in users:
        # Check if user has any data
        if WaterQualityData.objects.filter(user=user).exists():
            print(f"User {user.username} already has data")
            continue
        
        # Generate random data for the past 30 days
        total_flow = 0
        for day in range(30):
            current_date = start_date + timedelta(days=day)
            
            # Generate 3-5 readings per day
            num_readings = random.randint(3, 5)
            daily_flow = 0
            
            for _ in range(num_readings):
                # Generate random hour
                hour = random.randint(0, 23)
                minute = random.randint(0, 59)
                timestamp = current_date.replace(hour=hour, minute=minute)
                
                # Generate random values
                ph = round(random.uniform(6.5, 8.5), 2)
                flow = round(random.uniform(30, 100), 2)
                cod = round(random.uniform(100, 300), 2)
                bod = round(random.uniform(20, 80), 2)
                tss = round(random.uniform(50, 150), 2)
                
                # Update total flow
                total_flow += flow
                daily_flow += flow
                
                # Create data entry
                WaterQualityData.objects.create(
                    user=user,
                    timestamp=timestamp,
                    ph=ph,
                    flow=flow,
                    total_flow=total_flow,
                    cod=cod,
                    bod=bod,
                    tss=tss,
                    daily_flow=daily_flow,
                    date=timestamp.date()
                )
            
        print(f"Created sample data for user: {user.username}")

if __name__ == '__main__':
    print("Setting up sample data...")
    users = create_users()
    create_sample_data(users)
    print("Setup complete!")