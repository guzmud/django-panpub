from django.conf import settings

from panpub.forms import ContactForm, LoginForm
from panpub.models import Platform, Content

if hasattr(settings, 'PANPUB_MAX_SUGGEST'):
    PANPUB_MAX_SUGGEST = int(settings.PANPUB_MAX_SUGGEST)
else:
    PANPUB_MAX_SUGGEST = 7


def platform_settings(request):
    platform = Platform.load()

    override_base = 'base.html'
    if platform and platform.use_portal:
        override_base = 'panpub/portal.html'

    if request.path.startswith('/crafters'):
        anchor = 'crafters'
    elif request.path.startswith('/collectives'):
        anchor = 'crafters'
    elif request.path.startswith('/works'):
        anchor = 'works'
    elif request.path.startswith('/op'):
        anchor = 'portal'
    elif platform and platform.use_portal:
        anchor = request.GET.get('anchor', 'portal')
    else:
        anchor = request.GET.get('anchor', 'works')

    search_value = request.GET.get('tags__name', None)
    search_list = None
    if search_value:
        search_list = search_value.replace(',',' ').split()
        suggested_list = list()
        for el in search_list:
            for c in Content.objects.filter(tags__name__contains=el):
                for t in c.tags.values_list('name', flat=True):
                    if t not in suggested_list and t not in search_list:
                        suggested_list.append(t)
    else:
        suggested_list = Content.tags.tag_model.objects.order_by('-count').values_list('slug', flat=True)
    suggested_list = suggested_list[:PANPUB_MAX_SUGGEST]

    contactform = ContactForm()
    loginform = LoginForm()

    return {'platform': platform,
            'override_base': override_base,
            'anchor': anchor,
            'search_value': search_value,
            'search_list': search_list,
            'suggested_list': suggested_list,
            'contactform': contactform,
            'loginform': loginform,
            }
