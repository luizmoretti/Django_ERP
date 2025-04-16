"""
Filters for Profile views.
This module contains filter classes for Profile querysets.
"""
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from ..models import Profile

class ProfileFilter(filters.FilterSet):
    """Filter class for Profile model"""
    
    search = filters.CharFilter(method='filter_search')
    created_at_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_active = filters.BooleanFilter(field_name='is_active')
    
    class Meta:
        model = Profile
        fields = ['search', 'created_at_after', 'created_at_before', 'is_active']
    
    def filter_search(self, queryset, name, value):
        """
        Search filter that looks in user's first_name, last_name and email
        
        Args:
            queryset: Base queryset
            name: Field name (not used)
            value: Search value
            
        Returns:
            Filtered queryset
        """
        return queryset.filter(
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value) |
            Q(user__email__icontains=value)
        )

class CustomPagination(PageNumberPagination):
    """Custom pagination class for Profile views"""
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100