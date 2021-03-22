import datetime
import logging
import os
import re
from mimetypes import MimeTypes
from urllib import request

import phonenumbers
from django import template
from django.conf import settings
from django.template.defaultfilters import stringformat
from django.utils import (
    formats,
    timezone,
)
from django.utils.html import (
    escape,
    mark_safe,
)
from mal2 import constants
from mal2.utils import (
    format_file_size as utils_format_file_size,
    remove_url_protocol as utils_remove_url_protocol,
)


register = template.Library()

################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# HELPER

@register.simple_tag
def update_from_defaults(defaults, options):
    if isinstance(defaults, dict) and isinstance(options, dict):
        return {**defaults, **options}


@register.filter
def get_item(item, key):
    if isinstance(item, dict):
        return item.get(key)
    elif isinstance(item, list):
        return item[key]


@register.simple_tag
def attrs(attrs_data=None, quotes="double", *args, **kwargs):
    html_attrs = ""

    if not attrs_data:
        return html_attrs

    for name, value in attrs_data.items():
        if value is not False and name != "class":
            html_attrs += " %s" % name

            if value is not True:
                if quotes == "single":
                    quote = "'"
                elif quotes == "double":
                    quote = "\""

                html_attrs += "=%(quote)s%(value)s%(quote)s" % {
                    "quote": quote,
                    "value": escape(stringformat(value, "s")),
                }

    return mark_safe(html_attrs)


@register.simple_tag
def classes(classes_data=None, extra_classes=None):
    if not classes_data:
        classes_data = []

    if extra_classes:
        classes_data += extra_classes.split(" ")

    classes_data.sort()

    return " ".join(classes_data)


@register.simple_tag
def get_constants():
    return constants


################################################################################
# GET CONTENT TYPE

@register.filter
def ge_content_type(file):
    url = request.pathname2url(
        os.path.join(settings.MEDIA_ROOT, str(file))
    )

    mime_type = MimeTypes().guess_type(url)

    return mime_type[0]


################################################################################
# DATE / TIME

@register.filter
def date_format(iso_date, format=None):
    try:
        date = timezone.datetime.strptime(
            str(iso_date),
            "%Y-%m-%d",
        ).date()
    except ValueError:
        date = iso_date

    if isinstance(date, datetime.date):
        return formats.date_format(date, format)
    else:
        return date


@register.filter
def datetime_format(iso_date_time, format=None):
    try:
        date_time = timezone.datetime.strptime(
            str(iso_date_time),
            "%Y-%m-%d %H:%M",
        )
    except ValueError:
        date_time = iso_date_time

    if isinstance(date_time, datetime.datetime):
        return formats.date_format(date_time, format)
    else:
        return iso_date_time


################################################################################
# FORMAT FILE SIZE

@register.filter
def format_file_size(bytes):
    return utils_format_file_size(bytes)


################################################################################
# REMOVE URL PROTOCOL

@register.simple_tag
def remove_url_protocol(url, *args, **kwargs):
    return utils_remove_url_protocol(url)


################################################################################
# FORMAT PHONE NUMBER

@register.filter
def format_phone_number(phone_number):
    """
    A filter to format phone numbers.

    Args:
        phone_number (obj): A phone number object.

    Returns:
        str: The formatted phone number.
    """
    return phonenumbers.format_number(
        phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
    )


@register.filter
def unformat_phone_number(number):
    return re.sub(r'\s+', '', str(number))
