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
                  'cod', 'bod', 'tss', 'daily_flow', 'monthly_flow', 'date']
        read_only_fields = ['daily_flow', 'monthly_flow', 'date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', {})
        if not context.get('show_ph', True):
            self.fields.pop('ph')
        if not context.get('show_flow', True):
            self.fields.pop('flow')
        if not context.get('show_daily_flow', True):
            self.fields.pop('daily_flow')
        if not context.get('show_monthly_flow', True):
            self.fields.pop('monthly_flow')
        if not context.get('show_total_flow', True):
            self.fields.pop('total_flow')
        if not context.get('show_cod', True):
            self.fields.pop('cod')
        if not context.get('show_bod', True):
            self.fields.pop('bod')
        if not context.get('show_tss', True):
            self.fields.pop('tss')