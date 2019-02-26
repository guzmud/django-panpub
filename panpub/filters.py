import django_filters

from taggit.models import Tag

from panpub.models import Content


class MultiValueCharFilter(django_filters.BaseCSVFilter, django_filters.CharFilter):
    def filter(self, qs, value):
        values = value or []
        for value in values:
            qs = super(MultiValueCharFilter, self).filter(qs, value)
        return qs


class TaggedWorkFilter(django_filters.FilterSet):
    tags__name = MultiValueCharFilter(lookup_expr='contains')

    class Meta:
        model = Content
        fields = ['tags__name',]
