from django.contrib import admin
from .models import User, Salle, User_Salle
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
    # Customizing the admin interface for User
    list_display = ('id_user', 'email', 'name', 'is_admin')
    list_filter = ('is_admin',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'phone')}),
        ('Permissions', {'fields': ('is_admin', 'is_active', 'admin_creator')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'phone', 'is_admin', 'admin_creator'),
        }),
    )
    
    search_fields = ('email', 'name')
    ordering = ('email',)
    filter_horizontal = ()


class SalleAdmin(admin.ModelAdmin):
    # Display the id_salle field along with other important fields
    list_display = ('id_salle', 'name', 'phone', 'date_creation', 'admin_creator')
    search_fields = ('name', 'phone')  # Enable search by name and phone
    list_filter = ('date_creation',)  # Enable filtering by creation date


# Register the models with the admin site
admin.site.register(User, UserAdmin)  # Register User with the custom admin
admin.site.register(Salle, SalleAdmin)
admin.site.register(User_Salle) 