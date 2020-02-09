from django.contrib import admin
from .models import Invoice, File


# Register your models here.

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('file', 'timestamp','status')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('get_customer_name','number', 'date', 'due_date', 'description', 'quantity', 'unit_amount')

    def get_file(self, obj):
        return obj.file.id
    def get_customer_name(self,obj):
        return obj.customer.name

    get_file.short_description = 'File'
    get_customer_name.short_description = 'Customer Name'
