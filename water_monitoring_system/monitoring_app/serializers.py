# serializers.py
from rest_framework import serializers
from .models import WaterQualityData, CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  
        fields = ['id', 'username', 'email']

class WaterQualityDataSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = WaterQualityData
        fields = ['id', 'user', 'username', 'timestamp', 'ph', 'flow', 'total_flow', 
                  'cod', 'bod', 'tss', 'daily_flow', 'date']
        read_only_fields = ['daily_flow', 'date']