#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.forms import models as model_forms
from django.forms import Textarea
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from panpub.models import (
        Audio,
        Crafter,
        Collective,
        Content,
        Corpus,
        Image,
        Text,
        )


creator_fields = ['name',
                  'description',
                  'license',
                  'document',
                  'input_type',
                  'tags',
                  ]
corpus_fields = ['name',
                 'description',
                 'elements',
                 'tags',
                 ]
mediator_fields = ['name',
                   'description',
                   'tags',
                   ]


class CrafterCreate(CreateView):
    model = Crafter
    fields = ['user',
              'fa_icon',
              ]


class CrafterDelete(DeleteView):
    model = Crafter


class CrafterDetail(DetailView):
    model = Crafter
    context_object_name = 'crafter'


class CrafterUpdate(UpdateView):
    model = Crafter
    fields = ['user',
              'fa_icon',
              ]


class CrafterList(ListView):
    model = Crafter


class CollectiveCreate(CreateView):
    model = Collective
    fields = ['name',
              'circles',
              'members',
              'manifeste',
              ]


class CollectiveDelete(DeleteView):
    model = Collective


class CollectiveDetail(DetailView):
    model = Collective
    context_object_name = 'collective'


class CollectiveUpdate(UpdateView):
    model = Collective
    fields = ['name',
              'circles',
              'members',
              'manifeste',
              ]


class CollectiveList(ListView):
    model = Collective


class ContentCreate(CreateView):
    model = Content
    fields = creator_fields
    template_name = 'panpub/work_create.html'
    context_object_name = 'work'

    def get_form(self, *args, **kwargs):
        form = super(ContentCreate, self).get_form(*args, **kwargs)
        form.fields['description'].widget = Textarea(attrs={'rows':5, 'cols':20})
        return form


class ContentDelete(DeleteView):
    model = Content
    template_name = 'panpub/work_delete.html'
    context_object_name = 'work'
    success_url = '/'  # TODO

    def get_object(self, queryset=None):
        obj = super(ContentDelete, self).get_object(queryset=queryset)
        if obj.worktype == 'text' and Text.objects.filter(content_ptr=obj).exists():
            obj = Text.objects.get(content_ptr=obj)
        elif obj.worktype == 'image' and Image.objects.filter(content_ptr=obj).exists():
            obj = Image.objects.get(content_ptr=obj)
        elif obj.worktype == 'audio' and Audio.objects.filter(content_ptr=obj).exists():
            obj = Audio.objects.get(content_ptr=obj)
        elif obj.worktype == 'corpus' and Corpus.objects.filter(content_ptr=obj).exists():
            obj = Corpus.objects.get(content_ptr=obj)
        return obj


class ContentUpdate(UpdateView):
    model = Content
    fields = creator_fields
    template_name = 'panpub/work_update.html'
    context_object_name = 'work'

    def get_object(self, queryset=None):
        obj = super(ContentUpdate, self).get_object(queryset=queryset)
        if obj.worktype == 'text' and Text.objects.filter(content_ptr=obj).exists():
            obj = Text.objects.get(content_ptr=obj)
        elif obj.worktype == 'image' and Image.objects.filter(content_ptr=obj).exists():
            obj = Image.objects.get(content_ptr=obj)
        elif obj.worktype == 'audio' and Audio.objects.filter(content_ptr=obj).exists():
            obj = Audio.objects.get(content_ptr=obj)
        elif obj.worktype == 'corpus' and Corpus.objects.filter(content_ptr=obj).exists():
            obj = Corpus.objects.get(content_ptr=obj)
            self.fields = corpus_fields
        return obj

    def get_form_class(self):
        if isinstance(self.object, Text):
            return model_forms.modelform_factory(Text, fields=self.fields)
        elif isinstance(self.object, Image):
            return model_forms.modelform_factory(Image, fields=self.fields)
        elif isinstance(self.object, Audio):
            return model_forms.modelform_factory(Audio, fields=self.fields)
        elif isinstance(self.object, Corpus):
            return model_forms.modelform_factory(Corpus, fields=self.fields)
        else:
            return super(ContentUpdate, self).get_form_class()


class ContentMediate(UpdateView):
    fields = mediator_fields
    template_name = 'panpub/work_update.html'
    context_object_name = 'work'

    def get_object(self, queryset=None):
        obj = super(ContentMediate, self).get_object(queryset=queryset)
        if obj.worktype == 'text' and Text.objects.filter(content_ptr=obj).exists():
            obj = Text.objects.get(content_ptr=obj)
        elif obj.worktype == 'image' and Image.objects.filter(content_ptr=obj).exists():
            obj = Image.objects.get(content_ptr=obj)
        elif obj.worktype == 'audio' and Audio.objects.filter(content_ptr=obj).exists():
            obj = Audio.objects.get(content_ptr=obj)
        elif obj.worktype == 'corpus' and Corpus.objects.filter(content_ptr=obj).exists():
            obj = Corpus.objects.get(content_ptr=obj)
            self.fields = corpus_fields
        return obj

    def get_form_class(self):
        if isinstance(self.object, Text):
            return model_forms.modelform_factory(Text, fields=self.fields)
        elif isinstance(self.object, Image):
            return model_forms.modelform_factory(Image, fields=self.fields)
        elif isinstance(self.object, Audio):
            return model_forms.modelform_factory(Audio, fields=self.fields)
        elif isinstance(self.object, Corpus):
            return model_forms.modelform_factory(Corpus, fields=self.fields)
        else:
            return super(ContentUpdate, self).get_form_class()


class ContentList(ListView):
    model = Content


class TextCreate(ContentCreate):
    model = Text

    def get_context_data(self, **kwargs):
        ctx = super(TextCreate, self).get_context_data(**kwargs)
        ctx['worktype'] = 'text'
        return ctx


class ImageCreate(ContentCreate):
    model = Image

    def get_context_data(self, **kwargs):
        ctx = super(ImageCreate, self).get_context_data(**kwargs)
        ctx['worktype'] = 'image'
        return ctx


class AudioCreate(ContentCreate):
    model = Audio

    def get_context_data(self, **kwargs):
        ctx = super(AudioCreate, self).get_context_data(**kwargs)
        ctx['worktype'] = 'audio'
        return ctx


class CorpusCreate(ContentCreate):
    model = Corpus
    fields = corpus_fields

    def get_context_data(self, **kwargs):
        ctx = super(CorpusCreate, self).get_context_data(**kwargs)
        ctx['worktype'] = 'corpus'
        return ctx
