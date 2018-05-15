from django import template
from panpub.models import Crafter, Content, Text, Claim

register = template.Library()


def claim_filter(claims, claim_type):
    if claim_type in ['CRT', 'CUR', 'MED']:
        claims = claims.filter(claim_type=claim_type)
    return claims


@register.simple_tag
def crafterworks(crafter_pk, claim_type=None):
    if Crafter.objects.filter(pk=crafter_pk).exists():
        crafter = Crafter.objects.get(pk=crafter_pk)
        claims = Claim.objects.filter(crafter=crafter)
        claims = claim_filter(claims, claim_type)
        claims = claims.values_list('content', flat=True)
        works = Content.objects.filter(pk__in=claims)
        return claims


@register.simple_tag
def craftertexts(crafter_pk, claim_type=None):
    if Crafter.objects.filter(pk=crafter_pk).exists():
        crafter = Crafter.objects.get(pk=crafter_pk)
        claims = Claim.objects.filter(crafter=crafter)
        claims = claim_filter(claims, claim_type)
        claims = claims.values_list('content', flat=True)
        texts = Text.objects.filter(content_ptr__in=claims)
        return texts


@register.simple_tag
def craftercorpuses(crafter_pk):
    if Crafter.objects.filter(pk=crafter_pk).exists():
        crafter = Crafter.objects.get(pk=crafter_pk)

