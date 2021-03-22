from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions

from mal2.utils import remove_url_protocol
from mal2_db.models import Website


class DuplicateURLValidator(object):
    def __call__(self, url):
        url.strip("/")
        url_to_check = remove_url_protocol(url)

        website = Website.objects.filter(
            Q(url="http://%s" % url_to_check)
            | Q(url="https://%s" % url_to_check)
        ).first()

        if website:
            raise exceptions.ValidationError(
                _("URL already exists in the database!"),
                code="invalid",
            )
