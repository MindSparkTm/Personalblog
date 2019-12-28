from django.contrib import admin
from .models import *
# Register your models here.
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name','iso_3_abbreviation')
class USSDCarrierAdmin(admin.ModelAdmin):
    list_display = ('code','name','country')
class USSDSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id','phone_number','service_code')
class USSDPageAdmin(admin.ModelAdmin):
    list_display = ('title','carrier')
class USSDPageMoveAdmin(admin.ModelAdmin):
    list_display = ('page','next_page','required_user_input')
class USSDPageContentAdmin(admin.ModelAdmin):
    list_display = ('page','creator')
admin.site.register(Country,CountryAdmin)
admin.site.register(USSDCarrier,USSDCarrierAdmin)
admin.site.register(USSDSession,USSDSessionAdmin)
admin.site.register(USSDPage,USSDPageAdmin)
admin.site.register(USSDPageMove,USSDPageMoveAdmin)
admin.site.register(USSDPageContent,USSDPageContentAdmin)
admin.site.register(Currency)