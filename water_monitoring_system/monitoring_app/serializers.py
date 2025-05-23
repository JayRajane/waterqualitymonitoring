# monitoring_app/serializers.py
from rest_framework import serializers
from .models import WaterQualityData, CustomUser, Reading, Machine

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']

class WaterQualityDataSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = WaterQualityData
        fields = ['id', 'user', 'username', 'timestamp', 'ph', 'cod', 'bod', 'tss', 'date']
        read_only_fields = ['date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', {})
        if not context.get('show_ph', True):
            self.fields.pop('ph', None)
        if not context.get('show_cod', True):
            self.fields.pop('cod', None)
        if not context.get('show_bod', True):
            self.fields.pop('bod', None)
        if not context.get('show_tss', True):
            self.fields.pop('tss', None)

class ReadingSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    machine_name = serializers.ReadOnlyField(source='machine.name')
    
    class Meta:
        model = Reading
        fields = ['id', 'user', 'username', 'machine', 'machine_name', 'parameter', 'value', 'recorded_at']
        read_only_fields = ['recorded_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', {})
        user = context.get('user')
        if user:
            for i in range(1, 11):
                if not getattr(user, f'show_flow{i}'):
                    if 'parameter' in self.fields and f'flow{i}' in self.fields['parameter'].choices:
                        self.fields['parameter'].choices.pop(f'flow{i}', None)
                    if 'parameter' in self.fields and f'flow{i}_total' in self.fields['parameter'].choices:
                        self.fields['parameter'].choices.pop(f'flow{i}_total', None)
                    if 'parameter' in self.fields and f'flow{i}_daily' in self.fields['parameter'].choices:
                        self.fields['parameter'].choices.pop(f'flow{i}_daily', None)
                    if 'parameter' in self.fields and f'flow{i}_monthly' in self.fields['parameter'].choices:
                        self.fields['parameter'].choices.pop(f'flow{i}_monthly', None)