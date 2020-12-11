import django_filters
from .models import *
from django_filters import DateFilter

class OrderFilter(django_filters.FilterSet):
    startdate = DateFilter(field_name='created_at', lookup_expr='gte')
    enddate = DateFilter(field_name='created_at', lookup_expr='lte')
    class Meta:
        model = Order
        fields = ['created_at']
        exclude = ['created_at']