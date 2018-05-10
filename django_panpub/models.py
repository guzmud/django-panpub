# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from model_utils.models import TimeStampedModel


class Crafter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASACADE)


class Content(TimeStampedModel):
    name = models.CharField(max_length=100)
    claims = models.ManyToManyField(
        Crafter,
        through='Claim',
        through_fields=('content', 'crafter'),
    )


class Text(Content):
    pass


class Picture(Content):
    pass


class Audio(Content):
    pass


class OutsideLink(models.Model):
    pass


class Claim(models.Model):
    CREATOR = 'CR'
    CURATOR = 'CU'
    MEDIATOR = 'ME'
    CLAIMS = (
        (CREATOR, 'Creator'),
        (CURATOR, 'Curator'),
        (MEDIATOR, 'Mediator'),
    )
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    crafter = models.ForeignKey(Crafter, on_delete=models.CASCADE)
    claim_type = models.CharField(
        max_length=2,
        choices=CLAIMS,
        default=CREATOR
    )


class Tag(models.Model):
    pass


@receiver(post_save, sender=User)
def create_crafter(sender, instance, created, **kwargs):
    if created:
        Crafter.objects.create(user=instance)


@receiver(post_save, sender=User)
def update_crafter(sender, instance, **kwargs):
    instance.crafter.save()

