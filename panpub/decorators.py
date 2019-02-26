#!/usr/bin/env python3
from functools import wraps
from django.core.exceptions import PermissionDenied

from panpub.models import Claim, Content


def _test_claim(content_pk, crafter, claim_type=None):
    test = False
    if Content.objects.filter(pk=content_pk).exists():
        content = Content.objects.get(pk=content_pk)
        matching_claims = Claim.objects.filter(crafter=crafter,
                                               content=content)
        if claim_type in ['CRT', 'CUR', 'MED']:
            matching_claims = matching_claims.filter(claim_type=claim_type)
        if matching_claims.exists():
            test = True
    return test


def has_any_claim(content_pk):
    def decorator(func):
        def inner_decorator(request, *args, **kwargs):
            crafter = request.user.crafter
            if _test_claim(content_pk, crafter):
                return func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wraps(func)(inner_decorator)
    return decorator


def has_creator_claim(content_pk):
    def decorator(func):
        def inner_decorator(request, *args, **kwargs):
            crafter = request.user.crafter
            if _test_claim(content_pk, crafter, claim_type='CRT'):
                return func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wraps(func)(inner_decorator)
    return decorator


def has_curator_claim(content_pk):
    def decorator(func):
        def inner_decorator(request, *args, **kwargs):
            crafter = request.user.crafter
            if _test_claim(content_pk, crafter, claim_type='CUR'):
                return func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wraps(func)(inner_decorator)
    return decorator


def has_mediator_claim(content_pk):
    def decorator(func):
        def inner_decorator(request, *args, **kwargs):
            crafter = request.user.crafter
            if _test_claim(content_pk, crafter, claim_type='MED'):
                return func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wraps(func)(inner_decorator)
    return decorator
