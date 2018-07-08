#!/usr/bin/env python3

import datetime
import tarfile
from io import BytesIO, StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.http import HttpResponse

from panpub.models import PANPUB_MEDIA


FORMAT_TYPE_MATRICE = {
    'gfm': 'text/markdown',
    'markdown': 'text/markdown',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'epub': 'application/epub+zip',
    'html': 'text/html',
    'odt': 'application/vnd.oasis.opendocument.text',
    }


def xprformat_to_ctntype(export_format):
    try:
        return FORMAT_TYPE_MATRICE['export_format']
    except Exception:
        # should be nothing per RFC-7231
        return 'application/octet-stream'


def panpub_export():
    """put dumpdata and /media/ in a tarfile"""

    # dump the db tables into a StringIO
    out = StringIO()
    call_command('dumpdata',
                 exclude=['auth.permission', 'contenttypes', ],
                 indent=4,
                 format='json',
                 stdout=out)

    # create an in-memory tarfile in a BytesIO
    archivefile = BytesIO()
    tarchive = tarfile.open(mode="w", fileobj=archivefile)

    # turn the StringIO into a BytesIO, add it a TarInfo and tar it
    tinfo = tarfile.TarInfo(name="dumpdata.bkp")
    tout = BytesIO(out.getvalue().encode())
    tinfo.size = len(tout.getvalue())
    tout.seek(0)
    tarchive.addfile(fileobj=tout,
                     tarinfo=tinfo)

    # add the panpub-media folder recursively to the archive
    tarchive.add(Path(settings.MEDIA_ROOT, PANPUB_MEDIA).as_posix(),
                 arcname='panpub-media',
                 recursive=True)

    # prepare name, length and data
    pa_name = 'panarchive-{}.tar.gz'.format(datetime.date.today())
    pa_len = len(archivefile.getvalue())
    archivefile.seek(0)
    pa_data = archivefile.getvalue()

    return pa_data, pa_name, pa_len


def prepare_fileresponse(filedata, filename, filelen, filetype):
    response = HttpResponse(filedata,
                            content_type=filetype)
    response['Content-Disposition'] = 'attachment;filename={}'.format(filename)
    response['Content-Length'] = filelen
    return response
