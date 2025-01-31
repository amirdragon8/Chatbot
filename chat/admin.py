from django.contrib import admin

# Register your models here.
from .models import Task


class TaskAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('name', 'description', 'start_date', 'end_date', 'created_by', 'created_at')
    list_filter = ('start_date', 'end_date', 'created_by')  # Filters for easy navigation
    search_fields = ('name', 'description')  # Search functionality
    ordering = ('-created_at',)  # Default ordering

    # Fields to mark as read-only
    readonly_fields = ('created_at', 'created_by')

    # Organizing fields into sections
    fieldsets = (
        ('Task Details', {
            'fields': ('name', 'description', 'start_date', 'end_date'),
        }),
        ('Additional Information', {
            'fields': ('created_by', 'created_at'),
        }),
    )

admin.site.register(Task, TaskAdmin)