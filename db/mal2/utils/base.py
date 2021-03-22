import logging
import operator
import os
import re
import threading
from glob import glob

import requests
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.utils import get_random_secret_key
from django.template import loader
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    RequestException,
    Timeout,
    TooManyRedirects,
)


################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# SECRET KEY

def get_secret_key():
    secret_key_file = os.path.join(
        os.path.dirname(
            os.path.abspath(os.path.join(__file__, os.pardir)),
        ),
        "secret_key.txt",
    )

    if os.path.exists(secret_key_file):
        f = open(secret_key_file, "r")
        return f.read()

    secret_key = get_random_secret_key()

    f = open(secret_key_file, "w")
    f.write(secret_key)
    f.close()

    return secret_key


################################################################################
# PERMISSIONS

def has_perms(user, permissions):
    if not permissions:
        return True

    return all(
        [user.has_perm(permission) for permission in permissions]
    )


################################################################################
# FORMAT FILE SIZE

def format_file_size(bytes):
    bytes = float(bytes)
    kb = float(1024)
    mb = float(kb ** 2)
    gb = float(kb ** 3)
    tb = float(kb ** 4)

    if bytes < kb:
        return "{0} {1}".format(
            bytes,
            "Bytes" if 0 == bytes > 1 else "Byte"
        )
    elif kb <= bytes < mb:
        return "{0:.2f} kb".format(bytes / kb)
    elif mb <= bytes < gb:
        return "{0:.2f} MB".format(bytes / mb)
    elif gb <= bytes < tb:
        return "{0:.2f} GB".format(bytes / gb)
    elif tb <= bytes:
        return "{0:.2f} TB".format(bytes / tb)


################################################################################
# REMOVE URL PROTOCOL

def remove_url_protocol(url, *args, **kwargs):
    url = re.sub(r"^http(s?):\/\/(.*)$", r"\2", url.lower())

    return re.sub(r"(/?)$", r"", url)


################################################################################
# REGEX

def re_escape(pattern):
    # TODO: use re.escape() instead if updated to python 3.7

    # SPECIAL_CHARS
    # closing ")", "}" and "]"
    # "-" (a range in character set)
    # "&", "~", (extended character set operations)
    # "#" (comment) and WHITESPACE (ignored) in verbose mode

    _special_chars_map = {i: "\\" + chr(i) for i in b"()[]{}?*+-|^$\\.&~# \t\n\r\v\f"}

    if isinstance(pattern, str):
        return pattern.translate(_special_chars_map)

    pattern = str(pattern, "latin1")

    return pattern.translate(_special_chars_map).encode("latin1")


################################################################################
# MEDIA

def get_media_files(request, app_name, accept=None):
    path = os.path.join(settings.MEDIA_ROOT, str(request.user.id), app_name)
    files = []

    if not accept:
        accept = ("*",)

    for ext in accept:
        files.extend(glob(os.path.join(path, ext)))

    return files


################################################################################
# USER

_thread_locals = threading.local()


def set_current_user(user):
    _thread_locals.user = user


def remove_current_user():
    _thread_locals.user = None


def get_current_user():
    return getattr(_thread_locals, "user", None)


################################################################################
# OPERATOR

def get_truth(a, operator_type, b):
    ops = {
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
        "==": operator.eq,
        "in": operator.contains,
    }

    return ops[operator_type](a, b)


################################################################################
# EMAIL

def send_html_mail(subject_template_name, email_template_name, email_recipients, context=None):
    subject = loader.render_to_string(subject_template_name, context)
    subject = "".join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)

    email = EmailMessage(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        email_recipients,
    )

    email.content_subtype = "html"
    email.send()


################################################################################
# REQUESTS

def get_response(url, method="post", data=None, params=None, headers=None, verify=True, timeout=10, log_level="debug", error_text={}):
    response = None

    try:
        if method == "post":
            response = requests.post(
                url,
                data=data,
                headers=headers,
                verify=verify,
                timeout=timeout,
            )
        elif method == "get":
            response = requests.get(
                url,
                params=params,
                headers=headers,
                verify=verify,
                timeout=timeout,
            )
        elif method == "put":
            response = requests.put(
                url,
                timeout=timeout,
            )
        elif method == "delete":
            response = requests.delete(
                url,
                timeout=timeout,
            )
    except HTTPError as e:
        if log_level == "debug":
            logger.debug("%s%s" % (error_text.get("HTTPError", ""), e,))
        elif log_level == "error":
            logger.error("%s%s" % (error_text.get("HTTPError", ""), e,))
    except ConnectionError as e:
        if log_level == "debug":
            logger.debug("%s%s" % (error_text.get("ConnectionError", ""), e,))
        elif log_level == "error":
            logger.error("%s%s" % (error_text.get("ConnectionError", ""), e,))
    except Timeout as e:
        if log_level == "debug":
            logger.debug("%s%s" % (error_text.get("Timeout", ""), e,))
        elif log_level == "error":
            logger.error("%s%s" % (error_text.get("Timeout", ""), e,))
    except TooManyRedirects as e:
        if log_level == "debug":
            logger.debug("%s%s" % (error_text.get("TooManyRedirects", ""), e,))
        elif log_level == "error":
            logger.error("%s%s" % (error_text.get("TooManyRedirects", ""), e,))
    except RequestException as e:
        if log_level == "debug":
            logger.debug("%s%s" % (error_text.get("RequestException", ""), e,))
        elif log_level == "error":
            logger.error("%s%s" % (error_text.get("RequestException", ""), e,))

    if response is not None:
        try:
            response.raise_for_status()
        except HTTPError as e:
            if log_level == "debug":
                logger.debug("%s%s" % (error_text.get("HTTPError", ""), e,))
            elif log_level == "error":
                logger.error("%s%s" % (error_text.get("HTTPError", ""), e,))

    return response
