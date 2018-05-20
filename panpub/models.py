# -*- coding: utf-8 -*-

from io import StringIO
from sys import getsizeof

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

import hashlib
import pypandoc


class Crafter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    def claims(self, claim_type=None):
        claims = Claim.objects.filter(crafter=self)
        if claim_type in ['CRT', 'CUR', 'MED']:
            claims = claims.filter(claim_type=claim_type)
        return claims


class Corpus(models.Model):
    name = models.CharField(max_length=100)
    datestamp = models.DateField(null=True)
    description = models.TextField(blank=True)
    license = models.CharField(max_length=100)
    ready = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('Corpus_detail', args=[str(self.pk),])

    def __str__(self):
         return self.name

    def only():
        contents = Content.objects.values_list('pk', flat=True)
        return Corpus.objects.exclude(pk__in=contents)

    def get_contents(self):
        return Content.objects.filter(corpuses=self)

    def add_content(self, pk):
        if Content.objects.filter(pk=pk).exists():
            c = Content.objects.get(pk=pk)
            c.corpuses.add(self)

    def sup_content(self, pk):
        if Content.objects.filter(pk=pk).exists():
            c = Content.objects.get(pk=pk)
            c.corpuses.delete(self)
            self.delete(c)

    def publish(self):
        self.ready = True

    def claims(self):
        contents = self.get_contents()
        claims = Claim.objects.filter(content__in=contents)
        return claims

    def claimers(self):
        claims = self.claims()
        claimers = Crafter.objects.filter(pk__in=claims.values('crafter__pk').distinct())
        return claimers


class Content(Corpus):
    claims = models.ManyToManyField(
        Crafter,
        through='Claim',
        through_fields=('content', 'crafter'),
    )
    corpuses = models.ManyToManyField(Corpus, related_name='+')

    def get_absolute_url(self):
        return None

    def __str__(self):
        return self.name


class Text(Content):
    pandoc_formats = (
        ('markdown', 'Markdown'),
        ('gfm', 'Markdown (github-flavour)'),
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
                                  choices=pandoc_formats,
                                  default='markdown')

    # todo: homemade validator. quickwin: FileExtensionAllowed() ?
    document = models.FileField(
        upload_to='panpub-media/texts/',
        )

    def get_absolute_url(self):
        return reverse('Text_detail', args=[str(self.pk),])

    def save(self):
        try:
            data = self.document.read()
            data = pypandoc.convert_text(data, to='md', format=self.input_type)
            datafile = StringIO(data)
            self.document = InMemoryUploadedFile(
                                             datafile,
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
    document = models.FileField(upload_to='panpub-media/pictures/')


class Record(Content):
    document = models.FileField(upload_to='panpub-media/records/')


class OutsideLink(models.Model):
    pass


class Claim(models.Model):
    CREATOR = 'CRT'
    CURATOR = 'CUR'
    MEDIATOR = 'MED'
    CLAIMS = (
        (CREATOR, 'creator'),
        (CURATOR, 'curator'),
        (MEDIATOR, 'mediator'),
    )
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    crafter = models.ForeignKey(Crafter, on_delete=models.CASCADE)
    claim_type = models.CharField(
        max_length=3,
        choices=CLAIMS,
        default=CREATOR
    )

    def __str__(self):
        return "{} has a {} claim on {}".format(self.crafter,
                                                self.claim_type,
                                                self.content)


@receiver(post_save, sender=User)
def create_crafter(sender, instance, created, **kwargs):
    if created:
        Crafter.objects.create(user=instance)


@receiver(post_save, sender=User)
def update_crafter(sender, instance, **kwargs):
    instance.crafter.save()

