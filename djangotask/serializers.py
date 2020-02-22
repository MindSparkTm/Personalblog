from .models import ClientRequestDetail
from rest_framework import serializers

class ClientRequestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientRequestDetail
        fields = ('ip', 'browser_detail','content_type','query_string')
