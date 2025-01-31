from django.contrib import admin
from django import forms
from authentification.forms import VolunteerProfileForm
from .models import CustomUser, VolunteerProfile, NPOManagerProfile



# Inline admin for VolunteerProfile
class VolunteerProfileInline(admin.StackedInline):
    model = VolunteerProfile
    form = VolunteerProfileForm
    can_delete = False
    verbose_name_plural = "Volunteer Profile"
    extra = 0  # No additional empty forms


# Inline admin for NPOManagerProfile
class NPOManagerProfileInline(admin.StackedInline):
    model = NPOManagerProfile
    can_delete = False
    verbose_name_plural = "NPO Manager Profile"
    extra = 0  # No additional empty forms


# Custom admin for CustomUser
class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Role', {'fields': ('role',)}),
    )

    inlines = [VolunteerProfileInline, NPOManagerProfileInline]

    def get_inlines(self, request, obj=None):
        """
        Dynamically display inlines based on the user's role.
        """
        if obj:
            if obj.role == 'VOLUNTEER':
                return [VolunteerProfileInline]
            elif obj.role == 'NPO_MANAGER':
                return [NPOManagerProfileInline]
        return []

    def save_model(self, request, obj, form, change):
        """
        Automatically create the appropriate profile when a new user is created.
        """
        super().save_model(request, obj, form, change)
        if not change:  # On creation, add the profile for the role
            if obj.role == 'VOLUNTEER':
                VolunteerProfile.objects.get_or_create(user=obj)
            elif obj.role == 'NPO_MANAGER':
                NPOManagerProfile.objects.get_or_create(user=obj)


# Register the CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)
