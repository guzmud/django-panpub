# -*- coding: utf-8 -*-

from io import StringIO
from sys import getsizeof

from django.core.validators import FileExtensionValidator
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

import hashlib
import pypandoc

from model_utils.models import TimeStampedModel


class Crafter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class Corpus(models.Model):
    name = models.CharField(max_length=100)


class Content(TimeStampedModel):
    name = models.CharField(max_length=100)
    claims = models.ManyToManyField(
        Crafter,
        through='Claim',
        through_fields=('content', 'crafter'),
    )
    description = models.TextField(blank=True)
    corpuses = models.ManyToManyField(Corpus)


class Text(Content):
    pandoc_formats = (
        ('markdown', 'Markdown'),
        ('gfm', 'Markdown (github-style)'),
        ('latex', 'LaTeX'),
        ('docx', 'Word docx'),
        ('odt', 'OpenDocument ODT'),
        ('html', 'HTML'),
        ('mediawiki', 'MediaWiki markup'),
        ('rst', 'reStructuredText'),
        ('json', 'JSON'),
        ('native', 'Haskell (pandoc-native)'),
    )

    input_type = models.CharField(max_length=10,
                                  choices=pandoc_formats) 
    document = models.FileField(upload_to='panpub/texts/',)
#                                validators=[FileExtensionAllowed(allowed_extensions=['doc', 'md', 'rst', 'txt'])])

    def get_absolute_url(self):
        return reverse('Text_detail', args=[str(self.pk),])

    def save(self):
        try:
            data = self.document.read()
            data = pypandoc.convert_text(data, to='md', format=self.input_type)
            datafile = StringIO(data)
            self.document = InMemoryUploadedFile(datafile,
                                             'FileField',
                                             '{}.md'.format(hashlib.sha256(data.encode()).hexdigest()),
                                             'text/markdown',
                                             getsizeof(datafile),
                                             'UTF-8',
            )
        except:
            raise Exception
        else:
            super(Text,self).save()


class Picture(Content):
    document = models.FileField(upload_to='panpub/pictures/')


class Record(Content):
    document = models.FileField(upload_to='panpub/records/')


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


@receiver(post_save, sender=User)
def create_crafter(sender, instance, created, **kwargs):
    if created:
        Crafter.objects.create(user=instance)


@receiver(post_save, sender=User)
def update_crafter(sender, instance, **kwargs):
    instance.crafter.save()

