#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import pathlib
import tempfile
from io import StringIO
from sys import getsizeof

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify

import pypandoc


if hasattr(settings, 'PANPUB_MEDIA'):
    PANPUB_MEDIA = settings.PANPUB_MEDIA
else:
    PANPUB_MEDIA = 'panpub-media'


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
        return reverse('Corpus_detail', args=[str(self.pk), ])

    def __str__(self):
        return self.name

    def filefriendly_name(self):
        return slugify(self.name)

    def only():
        contents = Content.objects.values_list('pk', flat=True)
        return Corpus.objects.exclude(pk__in=contents)

    def get_contents(self):
        return Content.objects.filter(corpuses=self)

    def add_content(self, pk):
        if Content.objects.filter(pk=pk).exists():
            content = Content.objects.get(pk=pk)
            content.corpuses.add(self)

    def sup_content(self, pk):
        if Content.objects.filter(pk=pk).exists():
            content = Content.objects.get(pk=pk)
            content.corpuses.delete(self)
            self.delete(content)

    def publish(self):
        self.ready = True

    def claims(self):
        contents = self.get_contents()
        claims = Claim.objects.filter(content__in=contents)
        return claims

    def claimers(self):
        claims = self.claims()
        claimers = claims.values('crafter__pk').distinct()
        crafters = Crafter.objects.filter(pk__in=claimers)
        return crafters


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
        upload_to='{}/texts/'.format(PANPUB_MEDIA),
        )

    def get_absolute_url(self):
        return reverse('Text_detail', args=[str(self.pk), ])

    def save(self, *args, **kwargs):
        try:
            data = self.document.read()
            data = pypandoc.convert_text(data, to='md', format=self.input_type)
            datafile = StringIO(data)
            dataname = hashlib.sha256(data.encode()).hexdigest()
            self.document = InMemoryUploadedFile(
                                             datafile,
                                             'FileField',
                                             '{}.md'.format(dataname),
                                             'text/markdown',
                                             getsizeof(datafile),
                                             'UTF-8',
            )
        except Exception:
            raise Exception
        else:
            super(Text, self).save(*args, **kwargs)

    def available_pubformats(self):
        # pdf requires xetex
        return ('gfm',
                'html',
                'markdown',
                'docx',
                'epub',
                'odt',
                )

    def export(self, pubformat='markdown'):
        if pubformat not in self.available_pubformats():
            raise Exception
        try:
            with tempfile.NamedTemporaryFile() as f:
                outpath = pathlib.Path(tempfile.tempdir,
                                       f.name).as_posix()
                pypandoc.convert_file(self.document.path,
                                      pubformat,
                                      format='md',
                                      outputfile=outpath)
                f.seek(0)
                datafile = f.read()
        except Exception:
            raise Exception
        else:
            filelen = len(datafile)
            filename = '{}.{}'.format(self.filefriendly_name(),
                                      pubformat)
            return datafile, filename, filelen


class Dataset(Content):

    tablib_formats = ('csv',
                      'json',
                      'xls',
                      'yaml',
                      'tsv',
                      'html',
                      'xlsx',
                      'ods',
                      'dbf',
                      'df',
                      )

    document = models.FileField(
        upload_to='{}/datasets/'.format(PANPUB_MEDIA),
        )

    def get_absolute_url(self):
        return reverse('Dataset_detail', args=[str(self.pk), ])

    def save(self, *args, **kwargs):
        pass

    def available_pubformats(self):
        return self.tablib_formats+'latex'  # TODO

    def export(self, pubformat='csv'):
        pass


class Picture(Content):

    pillow_formats = ('bmp',
                      'eps',
                      'gif',
                      'icns',
                      'ico',
                      'im',
                      'jpeg',
                      'jpeg2000',
                      'msp',
                      'pcx',
                      'png',
                      'ppm',
                      'sgi',
                      'spider',
                      'tga',
                      'tiff',
                      'webp',
                      'xbm',
                      )

    pillow_r_formats = ('blp',
                        'cur',
                        'dcx',
                        'dds',
                        'fli',
                        'flc',
                        'fpx',
                        'ftex',
                        'gbr',
                        'gd',
                        'imt',
                        'iptc/naa',
                        'mcidas',
                        'mic',
                        'mpo',
                        'pcd',
                        'pixar',
                        'psd',
                        'wal',
                        'xpm',
                        ) + pillow_formats

    pillow_w_formats = ('palm',
                        'pdf',
                        'xvthumbnail',
                        ) + pillow_formats

    document = models.FileField(
        upload_to='{}/pictures/'.format(PANPUB_MEDIA),
        )

    def get_absolute_url(self):
        return reverse('Picture_detail', args=[str(self.pk), ])

    def save(self, *args, **kwargs):
        pass

    def available_pubformats(self):
        return self.pillow_w_formats

    def export(self, pubformat='png'):
        pass


class Record(Content):
    document = models.FileField(upload_to='{}/records/'.format(PANPUB_MEDIA))


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
    instance.crafter.save(**kwargs)
