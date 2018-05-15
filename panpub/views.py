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


class CorpusCreateView(CreateView):

    model = Corpus
    fields = ['name', 'datestamp', 'description']


class CorpusDeleteView(DeleteView):

    model = Corpus


class CorpusDetailView(DetailView):

    model = Corpus
    context_object_name = 'corpus'


class CorpusUpdateView(UpdateView):

    model = Corpus


class CorpusListView(ListView):

    model = Corpus
    context_object_name = 'corpuses'
    paginate_by = 10


class TextCreateView(CreateView):

    model = Text
    fields = ['name', 'description', 'document', 'input_type']


class TextDeleteView(DeleteView):

    model = Text


class TextDetailView(DetailView):

    model = Text
    context_object_name = 'text'


class TextUpdateView(UpdateView):

    model = Text


class TextListView(ListView):
    model = Text
    context_object_name = 'texts'
    paginate_by = 10

