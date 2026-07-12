import django_filters as filters

from .models import Asset


class AssetFilter(filters.FilterSet):
    """Backs the Category / Status / Department chip filters on the Assets screen."""
    category = filters.NumberFilter(field_name='category_id')
    department = filters.NumberFilter(field_name='department_id')
    status = filters.ChoiceFilter(choices=Asset.Status.choices)
    q = filters.CharFilter(method='filter_q')

    class Meta:
        model = Asset
        fields = ['category', 'department', 'status']

    def filter_q(self, queryset, name, value):
        # Powers the top search bar: "Search by tag, name, or QR code…"
        from django.db.models import Q
        return queryset.filter(
            Q(tag__icontains=value) | Q(name__icontains=value) | Q(qr_code__icontains=value)
        )
