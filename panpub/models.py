#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import pathlib
import tempfile
from io import BytesIO, StringIO
from sys import getsizeof

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.signals import post_save
from django.db.utils import OperationalError
from django.dispatch import receiver
from django.urls import reverse
from django.utils.functional import lazy
from django.utils.text import slugify

# import magic
import pypandoc

from colorful.fields import RGBColorField
from PIL import Image as PIL_image
from pydub import AudioSegment
from tagulous.models import SingleTagField, TagField

from panpub import references as refs

if hasattr(settings, 'PANPUB_MEDIA'):
    PANPUB_MEDIA = settings.PANPUB_MEDIA
else:
    PANPUB_MEDIA = 'panpub-media'

if hasattr(settings, 'FONTAWESOME_CSS_PATH'):
    FONTAWESOME_CSS_PATH = pathlib.Path(settings.FONTAWESOME_CSS_PATH)
else:
    FONTAWESOME_CSS_PATH = pathlib.Path(settings.STATIC_ROOT,
                                        'css', 'fontawesome.css')


def fontawesome_choices():
  try:
      with FONTAWESOME_CSS_PATH.open() as f:
          falist = [(k.split('.fa-', 1)[-1].split(':before', 1)[0],
                     k.split('.fa-', 1)[-1].split(':before', 1)[0])
                     for k in f if ':before' in k]
          return falist
  except:
      return list()


class SteelKiwiSingleton(models.Model):
    """from https://steelkiwi.com/blog/practical-application-singleton-design-pattern/"""

    class Meta:
        abstract = True

    def set_cache(self):
        cache.set(self.__class__.__name__, self)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SteelKiwiSingleton, self).save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            try:
                obj, created = cls.objects.get_or_create(pk=1)
            except OperationalError:
                return None
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)


class Crafter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fa_icon = models.CharField(max_length=25, blank=True)

    def __init__(self, *args, **kwargs):
        super(Crafter, self).__init__(*args, **kwargs)
        self._meta.get_field('fa_icon').choices = lazy(fontawesome_choices, list)()

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse('crafter_detail', args=[str(self.pk), ])

    def claims(self, claim_type=None):
        claims = Claim.objects.filter(crafter=self)
        if claim_type in ['CRT', 'CUR', 'MED']:
            claims = claims.filter(claim_type=claim_type)
        return claims

    def collectives(self):
        collectives = Collective.objects.filter(members__in=[self, ])
        return collectives


class Collective(models.Model):
    name = models.CharField(max_length=100)
    circles = models.ManyToManyField('self',
                                     blank=True)
    members = models.ManyToManyField(Crafter,
                                     blank=True)
    manifeste = models.ForeignKey('Text',
                                  models.SET_NULL,
                                  blank=True,
                                  null=True,
                                  )

    def get_absolute_url(self):
        return reverse('collective_detail', args=[str(self.pk), ])

    def __str__(self):
        return self.name

    def claims(self):
        claims = Claim.objects.none()
        for crafter in self.members.all():
            claims = claims | Claim.objects.filter(crafter=crafter)
        claims = claims.distinct().order_by('created_at')
        return claims

    def works(self):
        works = Content.objects.filter(id__in=set([k.content.id for k in self.claims()])).order_by('-created_at')
        return works

    def latest_members(self, k=3):
        return self.members.order_by('-id')[:k]

    def latest_works(self, k=3):
        return self.works().filter(ready=True)[:k]

    def latest_exhibits(self, k=5):
        return self.works().filter(ready=True).filter(is_exhibit=True).order_by('updated_at')[:k]


class Platform(SteelKiwiSingleton):
    root_collective = models.ForeignKey(Collective,
                                        models.SET_NULL,
                                        blank=True,
                                        null=True,
                                        )
    main_color = RGBColorField()
    contact_email = models.EmailField()
    use_portal = models.BooleanField(default=False)
    banner = models.ForeignKey('Image',
                               models.SET_NULL,
                               blank=True,
                               null=True,
                               )

    def get_name(self):
        try:
            return self.root_collective.name
        except:
            return 'noname'


class Content(models.Model):
    from panpub.utils import worktypes_choice

    CC_licenses = (
        ('CC BY', 'Attribution (CC BY)'),
        ('CC BY-SA', 'Attribution - ShareAlike (CC BY-SA)'),
        ('CC BY-ND', 'Attribution - NoDerivs (CC BY-ND)'),
        ('CC BY-NC', 'Attribution - NonCommercial (CC BY-NC)'),
        ('CC BY-NC-SA', 'Attribution - NonCommercial - ShareAlike (CC BY-NC-SA)'),
        ('CC BY-NC-ND', 'Attribution - NonCommercial - NoDerivs (CC BY-NC-ND)'),
        ('CC0', 'Public Domain (CC0)'),
        )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    license = models.CharField(max_length=15,
                               choices=CC_licenses,
                               default='CC BY')
    ready = models.BooleanField(default=False)
    is_exhibit = models.BooleanField(default=False)

    claims = models.ManyToManyField(
        Crafter,
        through='Claim',
        through_fields=('content', 'crafter'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TagField(case_sensitive=False,
                    force_lowercase=True,
                    max_count=5)

    worktype = models.CharField(max_length=15,
                                choices=worktypes_choice(),
                                default='content')

    def get_absolute_url(self):
        return reverse('work_details', args=[str(self.pk), ])

    def __str__(self):
        return self.name

    def get_tags(self):
        tags = self.tags.all()
        if self.worktype == 'text' and Text.objects.filter(content_ptr=self).exists():
            tags = tags | Text.objects.get(content_ptr=self).tags.all()
        elif self.worktype == 'image' and Image.objects.filter(content_ptr=self).exists():
            tags = tags | Image.objects.get(content_ptr=self).tags.all()
        elif self.worktype == 'corpus' and Corpus.objects.filter(content_ptr=self).exists():
            tags = tags | Corpus.objects.get(content_ptr=self).tags.all()
        return tags

    def set_worktype(self, worktype):
        self.worktype = worktype
        self.save()

    def filefriendly_name(self):
        return slugify(self.name)

    def publish(self):
        self.ready = True
        self.save()


class Corpus(Content):
    elements = models.ManyToManyField(Content,
                                      related_name='elements',
                                      )

    def save(self, *args, **kwargs):
        super(Corpus, self).save(*args, **kwargs)
        self.content_ptr.set_worktype('corpus')

    def available_pubformats(self):
        return refs.corpus_pubformats

    def export(self, pubformat='tar'):
        if pubformat not in self.available_pubformats():
            raise Exception
        try:
            pass
#            with tempfile.NamedTemporaryFile() as f:
#                outpath = pathlib.Path(tempfile.tempdir,
#                                       f.name).as_posix()
#                pypandoc.convert_file(self.document.path,
#                                      pubformat,
#                                      format='md',
#                                      outputfile=outpath)
#                f.seek(0)
#                datafile = f.read()
        except Exception:
            raise Exception
        else:
            pass
#            filelen = len(datafile)
#            filename = '{}.{}'.format(self.filefriendly_name(),
#                                      pubformat)
#            return datafile, filename, filelen


class Text(Content):
    input_type = models.CharField(max_length=10,
                                  choices=refs.text_upformats,
                                  default='markdown')

    # todo: homemade validator. quickwin: FileExtensionAllowed() ?
    document = models.FileField(
        upload_to='{}/texts/'.format(PANPUB_MEDIA),
        )

    def save(self, *args, **kwargs):
        try:
            data = self.document.read()
            # self.input_type = magic.from_buffer(data, mime=True)
            # obtained application/msdoc and application/vnd.openxmlformats
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
            self.content_ptr.set_worktype('text')

    def available_pubformats(self):
        return refs.text_pubformats

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


class Image(Content):
    input_type = models.CharField(max_length=10,
                                  choices=refs.image_upformats,
                                  default='png')

    document = models.FileField(
        upload_to='{}/images/'.format(PANPUB_MEDIA),
        )

    def save(self, *args, **kwargs):
        try:
            data = self.document.read()

            datainput = BytesIO(data)
            datainput.seek(0)
            image = PIL_image.open(datainput)

            datafile = BytesIO()
            image.save(datafile, format='png')
            dataname = hashlib.sha256(datafile.getvalue()).hexdigest()

            self.document = InMemoryUploadedFile(
                                             datafile,
                                             'FileField',
                                             '{}.png'.format(dataname),
                                             'image/png',
                                             getsizeof(datafile),
                                             'UTF-8',
            )
        except Exception:
            raise Exception
        else:
            super(Image, self).save(*args, **kwargs)
            self.content_ptr.set_worktype('image')

    def available_pubformats(self):
        return refs.image_pubformats

    def export(self, pubformat='png'):
        if pubformat not in self.available_pubformats():
            raise Exception
        try:
            image = PIL_image.open(self.document.path)
            datafile = BytesIO()
            image.save(datafile, format=pubformat)
        except Exception:
            raise Exception
        else:
            filelen = len(datafile.getvalue())
            datafile.seek(0)
            filename = '{}.{}'.format(self.filefriendly_name(),
                                      pubformat)
            return datafile, filename, filelen


class Audio(Content):
    input_type = models.CharField(max_length=10,
                                  choices=refs.audio_upformats,
                                  default='mp3')

    document = models.FileField(
        upload_to='{}/audios/'.format(PANPUB_MEDIA),
        )

    def save(self, *args, **kwargs):
        try:
            with tempfile.NamedTemporaryFile(suffix='.{}'.format(self.input_type)) as f1:
                f1.write(self.document.read())
                f1path = pathlib.Path(tempfile.tempdir, f1.name).as_posix()
                audiodata = AudioSegment.from_file(f1path, format=self.input_type)

                with tempfile.NamedTemporaryFile(suffix='.mp3') as f2:
                    f2path = pathlib.Path(tempfile.tempdir, f2.name).as_posix()
                    audiodata.export(f2path, format='mp3')

                    datafile = BytesIO(f2.read())
                    dataname = hashlib.sha256(datafile.getvalue()).hexdigest()
                    datafile.seek(0)
                    self.document = InMemoryUploadedFile(datafile,
                                                         'FileField',
                                                         '{}.mp3'.format(dataname),
                                                         'audio/mp3',
                                                         getsizeof(datafile),
                                                         'UTF-8',
                                                         )
        except Exception:
            raise Exception
        else:
            super(Audio, self).save(*args, **kwargs)
            self.content_ptr.set_worktype('audio')

    def available_pubformats(self):
        return refs.audio_pubformats

    def export(self, pubformat='mp3'):
        if pubformat not in self.available_pubformats():
            raise Exception
        try:
            audio = AudioSegment.from_file(self.document.path, format='mp3')
            with tempfile.NamedTemporaryFile(suffix='.{}'.format(pubformat)) as f:
                fpath = pathlib.Path(tempfile.tempdir, f.name).as_posix()
                audio.export(fpath, format=pubformat)
                f.seek(0)
                datafile = f.read()
        except Exception:
            raise Exception
        else:
            filelen = len(datafile)
            filename = '{}.{}'.format(self.filefriendly_name(),
                                      pubformat)
            return datafile, filename, filelen


class Video(Content):
    document = models.FileField(upload_to='{}/videos/'.format(PANPUB_MEDIA))


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
        return reverse('dataset_detail', args=[str(self.pk), ])

    def save(self, *args, **kwargs):
        pass

    def available_pubformats(self):
        return self.tablib_formats+'latex'  # TODO

    def export(self, pubformat='csv'):
        pass


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
    created_at = models.DateTimeField(auto_now_add=True)

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
