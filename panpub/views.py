#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from panpub.models import (
        Crafter,
	Corpus,
        Content,
	Text,
        )
from panpub import utils


class CrafterList(ListView):
    model = Crafter
    context_object_name = 'crafters'
    paginate_by = 10


class CrafterDetail(DetailView):
    model = Crafter
    context_object_name = 'crafter'


class CorpusCreate(CreateView):
    model = Corpus
    fields = ['name', 'datestamp', 'description']


class CorpusDelete(DeleteView):
    model = Corpus


class CorpusDetail(DetailView):
    model = Corpus
    context_object_name = 'corpus'


class CorpusUpdate(UpdateView):
    model = Corpus


class CorpusList(ListView):
    model = Corpus
    context_object_name = 'corpuses'
    paginate_by = 10


class ContentList(ListView):
    model = Content
    context_object_name = 'contents'
    paginate_by = 10


class ContentDetail(DetailView):
    model = Content
    context_object_name = 'content'


class TextCreate(CreateView):
    model = Text
    fields = ['name', 'description', 'document', 'input_type']


class TextDelete(DeleteView):
    model = Text


class TextDetail(DetailView):
    model = Text
    context_object_name = 'text'


class TextUpdate(UpdateView):
    model = Text


class TextList(ListView):
    model = Text
    context_object_name = 'texts'
    paginate_by = 10


def text_export(request, text_id, export_format):
    if not Text.objects.filter(pk=text_id).exists():
        raise Http404("Text does not exist.")
    text = Text.objects.get(pk=text_id)

    if not text.ready:
        raise PermissionDenied  # unless user has claim ?

    if export_format not in text.available_pubformats():
        raise Http404("Export format requested unavailable.")

    fdata, fname, flen = text.export(pubformat=export_format)
    content_type = utils.xprformat_to_ctntype(export_format)
    response = utils.prepare_fileresponse(fdata,
					  fname,
					  flen,
					  content_type)
    return response


def panpub_export(request):
    ppdata, ppname, pplen = utils.panpub_export()
    response = utils.prepare_fileresponse(ppdata,
					  ppname,
                                          pplen,
					  'application/x-gzip')
    return response
