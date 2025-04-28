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
        fields = ['id', 'user', 'username', 'timestamp', 'ph', 'flow1', 'flow2', 'flow3', 
                  'total_flow1', 'total_flow2', 'total_flow3', 'cod', 'bod', 'tss', 
                  'daily_flow1', 'daily_flow2', 'daily_flow3', 
                  'monthly_flow1', 'monthly_flow2', 'monthly_flow3', 'date']
        read_only_fields = ['daily_flow1', 'daily_flow2', 'daily_flow3', 
                           'monthly_flow1', 'monthly_flow2', 'monthly_flow3', 
                           'total_flow1', 'total_flow2', 'total_flow3', 'date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', {})
        if not context.get('show_ph', True):
            self.fields.pop('ph')
        if not context.get('show_flow1', True):
            self.fields.pop('flow1')
            self.fields.pop('daily_flow1')
            self.fields.pop('monthly_flow1')
            self.fields.pop('total_flow1')
        if not context.get('show_flow2', True):
            self.fields.pop('flow2')
            self.fields.pop('daily_flow2')
            self.fields.pop('monthly_flow2')
            self.fields.pop('total_flow2')
        if not context.get('show_flow3', True):
            self.fields.pop('flow3')
            self.fields.pop('daily_flow3')
            self.fields.pop('monthly_flow3')
            self.fields.pop('total_flow3')
        if not context.get('show_cod', True):
            self.fields.pop('cod')
        if not context.get('show_bod', True):
            self.fields.pop('bod')
        if not context.get('show_tss', True):
            self.fields.pop('tss')