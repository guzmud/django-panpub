# -*- coding: utf-8 -*-
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import (
        Corpus,
        Text,
)


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

