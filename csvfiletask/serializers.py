from rest_framework import serializers
from .models import File, Invoice


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('file', 'timestamp',)


class InvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name')
    class Meta:
        model = Invoice
        fields = ('customer_name','number','unit_amount','quantity','total','due_date','date',)

class InvoiceDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ('date','total',)

class InvoiceMonthSerializer(serializers.ModelSerializer):
    month = serializers.IntegerField()
    class Meta:
        model = Invoice
        fields = ('month','total',)