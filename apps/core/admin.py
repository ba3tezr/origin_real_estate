"""
Admin configuration for Core app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Permission, Role, UserProfile, AuditLog,
    SystemSetting, Notification
)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_select_related = ('profile',)

    def get_role(self, instance):
        return instance.profile.role if hasattr(instance, 'profile') else '-'
    get_role.short_description = 'Role'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'module', 'action', 'created_at']
    list_filter = ['module', 'action']
    search_fields = ['name', 'codename', 'description']
    ordering = ['module', 'action']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'role_type', 'is_active', 'created_at']
    list_filter = ['role_type', 'is_active']
    search_fields = ['name', 'description']
    filter_horizontal = ['permissions']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'language', 'is_active']
    list_filter = ['role', 'language', 'is_active']
    search_fields = ['user__username', 'user__email', 'phone']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'content_type', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'description']
    readonly_fields = ['user', 'action', 'content_type', 'object_id', 
                      'description', 'ip_address', 'user_agent', 'changes', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'data_type', 'is_public', 'updated_by', 'updated_at']
    list_filter = ['data_type', 'is_public']
    search_fields = ['key', 'description']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
