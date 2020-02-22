from django.contrib import admin
from .models import ClientRequestDetail
# Register your models here.

@admin.register(ClientRequestDetail)
class ClientRequestDetailAdmin(admin.ModelAdmin):
    list_display = ('ip','content_type','browser_detail','query_string')
    readonly_fields = ('date_added',)
    search_fields = ('browser_detail',)