#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from panpub.filters import TaggedWorkFilter
from panpub.forms import (
        CrafterDeploy,
        CollectiveDeploy,
        CollectiveEdit,
        ContactForm,
        ImageExport,
        PlatformDeploy,
        ProfileEdit,
        TextExport,
        ContentUpload,
        )
from panpub.models import (
        Crafter,
        Collective,
        Content,
        Corpus,
        Image,
        Platform,
        Text,
        )
from panpub import utils


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


def portal(request):
    platform = Platform.load()

    if (platform is None) or (platform.root_collective is None):
        crafter_deploy = CrafterDeploy()
        collective_deploy = CollectiveDeploy()
        platform_deploy = PlatformDeploy()

        if request.method == 'POST':
            crafter_deploy = CrafterDeploy(request.POST)
            collective_deploy = CollectiveDeploy(request.POST)
            platform_deploy = PlatformDeploy(request.POST)
            if crafter_deploy.is_valid() and collective_deploy.is_valid() and platform_deploy.is_valid():
                user = crafter_deploy.save()
                user.refresh_from_db()
                user.crafter.fa_icon = crafter_deploy.cleaned_data.get('fa_icon')
                user.save()
                collective = collective_deploy.save()
                platform = platform_deploy.save()
                platform.root_collective = collective
                platform.save()
                collective.members.add(user.crafter)
                collective.save()
                user = authenticate(username=user.username, password=crafter_deploy.cleaned_data.get('password1'))
                login(request, user)
                return redirect('/')

        return render(request,
                      'panpub/deploy.html',
                      {'crafter_deploy': crafter_deploy,
                       'collective_deploy': collective_deploy,
                       'platform_deploy': platform_deploy,
                       })

    # exhibit panel
    exhibits = Content.objects.filter(ready=True).filter(is_exhibit=True).order_by('updated_at')

    # works panel
    worktypes = utils.worktypes()

    # rewriting ' ' in ',' for the CSV parser in the tag filter
    #grq_tags = request.GET.getlist('tags__name')
    #if grq_tags:
    #    grq_tags = [tag.replace(' ', ',') for tag in grq_tags]
    #    grq = request.GET.copy()
    #    grq = grq.setlist('tags_name', grq_tags)
    #else:
    #    grq = request.GET.copy()
    #works = TaggedWorkFilter(grq, queryset=Content.objects.all())
    works = TaggedWorkFilter(request.GET, queryset=Content.objects.all())

    # crafter panel
    crafters = Crafter.objects.all()

    # collective panel
    collective = platform.root_collective

    return render(request,
                  'panpub/portal.html',
                  {'exhibits': exhibits,
                   'collective': collective,
                   'crafters': crafters,
                   'worktypes': worktypes,
                   'works': works,
                  })


def contact_form(request):
    platform = Platform.load()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            identity = form.cleaned_data['identity']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            status = send_mail(subject="[{}] Message from {}".format(platform.get_name(), identity),
                               message="{}".format(message),
                               from_email="{}".format(email),
                               recipient_list=['{}'.format(platform.contact_email),],
                               fail_silently=False,
                               )
            if status > 0:
                messages.success(request, 'Your message has been successfully sent. Thank you.')
            else:
                messages.error(request, 'Sorry we could not process your message. Please try again later.')
        else:
            messages.error(request, 'Sorry your form is not a valid one. Please re-fill it.')
    return redirect('/')


@login_required
def profile_edit(request):
    try:
       user = request.user
       crafter = Crafter.objects.get(user=user) 
    except:
        return redirect('portal')

    profile_form = ProfileEdit(instance=user)
    if request.method == 'POST':
        profile_form = ProfileEdit(request.POST, instance=user)
        if profile_form.is_valid():
            crafter.fa_icon = profile_form.cleaned_data['fa_icon']
            crafter.save()
            profile_form.save()

    return render(request,
                  'panpub/accounts/profile_edit.html',
                  {'profile_form': profile_form,
                  })


@login_required
def platform_configure(request):
    platform = Platform.load()

    platform_form = PlatformDeploy(instance=platform)
    if request.method == 'POST':
        platform_form = PlatformDeploy(request.POST, instance=platform)
        if platform_form.is_valid():
            platform_form.save()

    return render(request,
                  'panpub/platform_configure.html',
                  {'platform_form': platform_form,
                  })


@login_required
def collective_edit(request):
    platform = Platform.load()

    if platform.root_collective:
        collective = platform.root_collective
        collective_form = CollectiveEdit(instance=collective)
        if request.method == 'POST':
            collective_form = CollectiveEdit(request.POST, instance=collective)
            if collective_form.is_valid():
                collective_form.save()

        return render(request,
                      'panpub/collective_edit.html',
                      {'collective_form': collective_form,
                      })
    return redirect('portal')


def crafter_register(request):
    crafter_form = CrafterDeploy()
    platform = Platform.load()

    if request.method == 'POST':
        crafter_form = CrafterDeploy(request.POST)
        if crafter_form.is_valid():
            user = crafter_form.save()
            user.refresh_from_db()
            user.crafter.fa_icon = crafter_form.cleaned_data.get('fa_icon')
            user.save()
            if platform.root_collective:
                collective = platform.root_collective
                collective.members.add(user.crafter)
                collective.save()
            return redirect('/?anchor=crafters')

    return render(request,
                  'panpub/crafter_register.html',
                  {'crafter_form': crafter_form,
                  })


def work_random(request):
    return redirect(random.choice(Content.objects.all()).get_absolute_url())


def work_details(request, pk):
    work = get_object_or_404(Content, pk=pk)

    similar_works = Content.objects.exclude(pk=work.pk).filter(tags__in=work.tags.all())

    return render(request,
                  'panpub/work_details.html',
                  {'work': work,
                   'similar_works': similar_works,
                  })


def corpus_assemble(request):
    return redirect('/')


def work_upload(request):
    upload_form = ContentUpload()
    if request.method == 'POST':
        upload_form = ContentUpload(request.POST, request.FILES)
        if upload_form.is_valid():
            content = upload_form.save(commit=False)
            if content.worktype in utils.worktypes(include_content=False):
                workclass = utils.worktype_class(content.worktype)
                work = workclass.objects.create(name=content.name,
                                                description=content.description,
                                                license=content.license,
                                                is_exhibit=content.is_exhibit,
                                                worktype=content.worktype,
                                                tags=upload_form.cleaned_data.get('tags', None),
                                                input_type=upload_form.cleaned_data.get('input_type', None),
                                                document=upload_form.cleaned_data.get('document', None),
                                                )
                work.save()
                return redirect('work_details', pk=work.pk)
    return render(request,
                  'panpub/work_upload.html',
                  {'upload_form': upload_form,
                  })


def work_export_form(request, pk):
    if request.method == 'POST':
        work = Content.objects.get(pk=pk)
        if not work.ready:
            raise PermissionDenied  # unless user has claim ?

        if work.worktype == 'text' and Text.objects.filter(content_ptr=work).exists():
            work = Text.objects.get(content_ptr=work)
            form = TextExport(request.POST)
        elif work.worktype == 'image' and Image.objects.filter(content_ptr=work).exists():
            work = Image.objects.get(content_ptr=work)
            form = ImageExport(request.POST)
#        elif work.worktype == 'corpus' and Corpus.objects.filter(content_ptr=work).exists():
#            work = Corpus.objects.get(content_ptr=work)
        else:
            raise Http404  # better error msg

        if form.is_valid():
            export_format = form.cleaned_data['format']
            if export_format not in work.available_pubformats():
                raise Http404("Export format requested unavailable.")  # better error msg

            fdata, fname, flen = work.export(pubformat=export_format)
            content_type = utils.xprformat_to_ctntype(export_format)
            response = utils.prepare_fileresponse(fdata,
                                                  fname,
                                                  flen,
                                                  content_type)
            return response
    return redirect('work_details', pk=pk)


def load_inputtypes(request):
    worktype = request.GET.get('worktype')
    return render(request,
                  'panpub/forms/inputtype_options.html',
                  {'input_types': utils.worktype_inputtype(worktype),
                  })


def panpub_export(request):
    ppdata, ppname, pplen = utils.panpub_export()
    response = utils.prepare_fileresponse(ppdata,
                                          ppname,
                                          pplen,
                                          'application/x-gzip')
    return response
