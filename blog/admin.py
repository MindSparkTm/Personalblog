from django.contrib import admin
from .models import UserProfile,Post
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Register your models here.

# class UserProfileAdmin(admin.ModelAdmin):
#     def get_user(self,obj):
#         return obj.user.username
#     list_display = ('get_user','subscribed','date_last_modified')

class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_subscription')
    list_select_related = ('profile',)

    def get_subscription(self, instance):
        return instance.profile.subscribed

    get_subscription.short_description = 'Subscription'
    def get_location(self, instance):
        return instance.profile.location

    get_location.short_description = 'Location'
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

class PostAdmin(admin.ModelAdmin):
    list_display = ('title','description')

admin.site.register(Post,PostAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
# admin.site.register(UserProfile,UserProfileAdmin)