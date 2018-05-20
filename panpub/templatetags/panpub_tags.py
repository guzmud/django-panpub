from django import template
from panpub.models import Crafter, Content, Text

register = template.Library()


def content_claimed_by_crafter(crafter_pk, claim_type=None):
    crafter = Crafter.objects.get(pk=crafter_pk)
    claims = crafter.claims(claim_type=claim_type)
    claims = claims.values_list('content', flat=True)
    return claims


@register.simple_tag
def crafterworks(crafter_pk, claim_type=None):
    if Crafter.objects.filter(pk=crafter_pk).exists():
        claims = content_claimed_by_crafter(crafter_pk, claim_type)
        works = Content.objects.filter(pk__in=claims)
        return works


@register.simple_tag
def craftertexts(crafter_pk, claim_type=None):
    if Crafter.objects.filter(pk=crafter_pk).exists():
        claims = content_claimed_by_crafter(crafter_pk, claim_type)
        texts = Text.objects.filter(content_ptr__in=claims)
        return texts


@register.simple_tag
def craftercorpuses(crafter_pk):
    raise NotImplementedError
