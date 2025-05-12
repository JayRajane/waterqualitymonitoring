# monitoring_app/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, WaterQualityData, Machine, Reading

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'address', 'contact_number', 'state', 'state_code')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Visibility', {'fields': ('show_ph', 'show_flow1', 'show_flow2', 'show_flow3', 'show_cod', 'show_bod', 'show_tss')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

class ReadingAdmin(admin.ModelAdmin):
    list_display = ('user', 'machine', 'parameter', 'value', 'recorded_at')
    list_filter = ('parameter', 'machine', 'user')
    search_fields = ('user__username', 'machine__name', 'parameter')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(WaterQualityData)
admin.site.register(Machine)
admin.site.register(Reading, ReadingAdmin)