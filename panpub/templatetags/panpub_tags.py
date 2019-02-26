import base64

from django import template
from django.forms import FileInput, Textarea

from panpub.forms import CorpusExport, TextExport, ImageExport
from panpub.genericviews import ContentDelete, ContentUpdate, ContentMediate
from panpub.models import Claim, Crafter, Content, Corpus, Image, Platform, Text
from panpub.utils import worktype_icon


register = template.Library()


def content_claimed_by_crafter(crafter_pk, claim_type=None):
    crafter = Crafter.objects.get(pk=crafter_pk)
    claims = crafter.claims(claim_type=claim_type)
    claims = claims.values_list('content', flat=True)
    return claims


@register.simple_tag
def creatorclaims_number(crafter_pk):
    if Crafter.objects.filter(pk=crafter_pk).exists():
        return len(Crafter.objects.get(pk=crafter_pk).claims('CRT'))
    return 0


@register.simple_tag
def curatorclaims_number(crafter_pk):
    if Crafter.objects.filter(pk=crafter_pk).exists():
        return len(Crafter.objects.get(pk=crafter_pk).claims('CUR'))
    return 0


@register.simple_tag
def mediatorclaims_number(crafter_pk):
    if Crafter.objects.filter(pk=crafter_pk).exists():
        return len(Crafter.objects.get(pk=crafter_pk).claims('MED'))
    return 0


@register.simple_tag
def crafterworks(crafter_pk, claim_type=None):
    if Crafter.objects.filter(pk=crafter_pk).exists():
        claims = content_claimed_by_crafter(crafter_pk, claim_type)
        works = Content.objects.filter(pk__in=claims)
        return works
    return Content.objects.none()


@register.simple_tag
def craftertexts(crafter_pk, claim_type=None):
    if Crafter.objects.filter(pk=crafter_pk).exists():
        claims = content_claimed_by_crafter(crafter_pk, claim_type)
        texts = Text.objects.filter(content_ptr__in=claims)
        return texts
    return Text.objects.none()


@register.simple_tag
def has_creator_claim(user, work):
    try:
        crafter = Crafter.objects.get(user=user)
        return Claim.objects.filter(crafter=crafter,
                                    content=work,
                                    claim_type='CRT',
                                    ).exists()
    except:
        return False


@register.simple_tag
def has_curator_claim(user, work):
    try:
        crafter = Crafter.objects.get(user=user)
        return Claim.objects.filter(crafter=crafter,
                                    content=work,
                                    claim_type='CUR',
                                    ).exists()
    except:
        return False


@register.simple_tag
def has_mediator_claim(user, work):
    try:
        crafter = Crafter.objects.get(user=user)
        return Claim.objects.filter(crafter=crafter,
                                    content=work,
                                    claim_type='MED',
                                    ).exists()
    except:
        return False


@register.simple_tag
def license_tag(license):
    CC_licenses = {k[0]: k[1] for k in Content.CC_licenses }
    if license not in CC_licenses:
        return license

    html = '<i class="fab fa-creative-commons fa-lg"></i>&nbsp;'
    if license=='CC0':
        uri = 'https://creativecommons.org/share-your-work/public-domain/'
        html += '<i class="fab fa-creative-commons-pd fa-lg"></i>&nbsp;'
    else:
        uri = 'https://creativecommons.org/share-your-work/licensing-types-examples/'
        if 'BY' in license:
            html += '<i class="fab fa-creative-commons-by fa-lg"></i>&nbsp;'
        if 'SA' in license:
            html += '<i class="fab fa-creative-commons-sa fa-lg"></i>&nbsp;'
        if 'NC' in license:
            html += '<i class="fab fa-creative-commons-nc-eu fa-lg"></i>&nbsp;'
        if 'ND' in license:
            html += '<i class="fab fa-creative-commons-nd fa-lg"></i>&nbsp;'
    html = "CreativeCommons:&nbsp;<a href='{}' target='_blank'><span data-tooltip tabindex='1' title='{}' style='cursor: pointer;'>{}</span></a>".format(uri, CC_licenses[license], html)
    return html


def main_color(platform):
    color = "#333333"
    if platform and platform.main_color is not None:
        color = platform.main_color
    return color


@register.simple_tag
def base64_image(image):
    return base64.b64encode(image.document.read()).decode()


@register.inclusion_tag('panpub/display/image.html')
def image_display(work):
    if Image.objects.filter(content_ptr=work).exists():
        return {'b64image': base64_image(Image.objects.get(content_ptr=work)), }


@register.inclusion_tag('panpub/display/image_thumbnail.html')
def image_thumbnail(work):
    if Image.objects.filter(content_ptr=work).exists():
        return {'b64image': base64_image(Image.objects.get(content_ptr=work)), }


@register.inclusion_tag('panpub/display/text.html')
def text_display(work):
    if Text.objects.filter(content_ptr=work).exists():
        return {'text': Text.objects.get(content_ptr=work).document.read(), }


@register.inclusion_tag('panpub/display/text_thumbnail.html')
def text_thumbnail(work):
    if Text.objects.filter(content_ptr=work).exists():
        return {'text': b' '.join(Text.objects.get(content_ptr=work).document.read()[:50].split(b' ')[:-1]).decode('utf-8')}


@register.inclusion_tag('panpub/display/corpus.html')
def corpus_display(work):
    if Corpus.objects.filter(content_ptr=work).exists():
        return {'corpus': Corpus.objects.get(content_ptr=work), }


@register.inclusion_tag('panpub/display/corpus_thumbnail.html')
def corpus_thumbnail(work):
    if Corpus.objects.filter(content_ptr=work).exists():
        return {'elements': Corpus.objects.get(content_ptr=work).elements.all()}
    return {'elements': Corpus.objects.none()}


def work_metainfo(work):
    tags = work.get_tags()

    creator_claims = Claim.objects.filter(content=work, claim_type='CRT').values('crafter').distinct()
    creators = Crafter.objects.filter(pk__in=creator_claims)
    curator_claims = Claim.objects.filter(content=work, claim_type='CUR').values('crafter').distinct()
    curators = Crafter.objects.filter(pk__in=curator_claims)
    mediator_claims = Claim.objects.filter(content=work, claim_type='MED').values('crafter').distinct()
    mediators = Crafter.objects.filter(pk__in=mediator_claims)

    return tags, creators, curators, mediators


@register.inclusion_tag('panpub/components/cartouche.html')
def cartouche(work, user):
    tags, creators, curators, mediators = work_metainfo(work)

    crt_right = has_creator_claim(user, work)
    cur_right = has_curator_claim(user, work)
    med_right = has_mediator_claim(user, work)

    export_form = None
    work_child = None
    if work.worktype == 'text':
        export_form = TextExport()
        if Text.objects.filter(content_ptr=work).exists():
            work_child = Text.objects.get(content_ptr=work)
    elif work.worktype == 'image':
        export_form = ImageExport()
        if Image.objects.filter(content_ptr=work).exists():
            work_child = Image.objects.get(content_ptr=work)
    elif work.worktype == 'corpus':
        export_form = CorpusExport()
        if Corpus.objects.filter(content_ptr=work).exists():
            work_child = Corpus.objects.get(content_ptr=work)

    update_form = None
    delete_form = None
    if has_creator_claim(user, work) or has_curator_claim(user, work):
        update_form = ContentUpdate(object=work_child).get_form_class()(instance=work_child)
        update_form.fields['description'].widget = Textarea(attrs={'rows': 3})
        for field in update_form.fields:
            update_form.fields[field].widget.attrs.update({'class': 'input-group-field'})
        delete_form = True

    mediate_form = None
    if has_mediator_claim(user, work):
        mediate_form = ContentMediate(object=work_child).get_form_class()(instance=work_child)
        mediate_form.fields['description'].widget = Textarea(attrs={'rows': 3})
        mediate_form.fields['document'].widget = FileInput(attrs={'required': 'false'})
        for field in mediate_form.fields:
            mediate_form.fields[field].widget.attrs.update({'class': 'input-group-field'})

    color = main_color(Platform.load())

    return {'work': work,
            'tags': tags,
            'creators': creators,
            'curators': curators,
            'mediators': mediators,
            'crt_right': crt_right,
            'cur_right': cur_right,
            'med_right': med_right,
            'export_form': export_form,
            'update_form': update_form,
            'delete_form': delete_form,
            'mediate_form': mediate_form,
            'color': color,
           }


@register.inclusion_tag('panpub/components/workcard.html')
def workcard(work):
    tags, creators, curators, mediators = work_metainfo(work)

    return {'work': work,
            'tags': tags,
            'creators': creators,
            'curators': curators,
            'mediators': mediators,
           }


@register.inclusion_tag('panpub/components/recolor_css.html')
def recolor_css(platform):
    return {'color': main_color(platform), }


@register.simple_tag
def workicon(worktype):
    return worktype_icon(worktype)
