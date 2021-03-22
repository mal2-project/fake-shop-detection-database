import json
import re

from django.core import exceptions
from django.forms import (
    fields,
    widgets,
)
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField

from mal2.forms.widgets import (
    DateInput,
    FileTree,
    RangeInput,
    Select,
    TimeInput,
    TincyMCE,
)


################################################################################
# DATE/TIME

class DateField(fields.DateField):
    widget = DateInput


class TimeField(fields.TimeField):
    widget = TimeInput


################################################################################
# SELECT

class ChoiceField(fields.ChoiceField):
    widget = Select


################################################################################
# INTEGER

class IntegerField(fields.IntegerField):
    def __init__(self, step=None, **kwargs):
        self.step = step

        super().__init__(**kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)

        if isinstance(widget, widgets.NumberInput) or isinstance(widget, RangeInput):
            if self.min_value is not None:
                attrs["min"] = self.min_value

            if self.max_value is not None:
                attrs["max"] = self.max_value

            if self.step is not None:
                attrs["step"] = self.step

        return attrs


################################################################################
# GROUP

class FieldGroupMixin(object):
    def __init__(self, *args, **kwargs):
        self.group_append = kwargs.pop("append", None)
        self.group_prepend = kwargs.pop("prepend", None)

        super().__init__(*args, **kwargs)


class IntegerFieldGroup(FieldGroupMixin, fields.IntegerField):
    pass


class CharFieldGroup(FieldGroupMixin, fields.CharField):
    pass


class DecimalFieldGroup(FieldGroupMixin, fields.DecimalField):
    pass


################################################################################
# PHONE NUMBER

class PhoneNumberField(PhoneNumberField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.help_text = _("e.g. +43 12345678")


################################################################################
# RESTRICTED FILE

class RestrictedFileField(fields.FileField):
    def __init__(self, accept=None, content_types=None, help_text=None, max_upload_size=None, upload_to='', **kwargs):
        self.accept = accept
        self.content_types = content_types
        self.max_upload_size = max_upload_size
        self.upload_to = upload_to

        attrs = {
            "data-max-size": max_upload_size,
        }

        if accept:
            attrs["accept"] = ",".join(accept)

        self.widget = widgets.FileInput(attrs)

        super().__init__(
            help_text=self.get_help_text(help_text),
            **kwargs,
        )

    def get_help_text(self, help_text):
        if not help_text and self.accept:
            accept_text = ""

            if len(self.accept) == 1:
                return _("The allowed format is <strong>%s</strong>.") % self.accept[0][1:].upper()

            for index, item in enumerate(self.accept):
                text = "<strong>%s</strong>" % item[1:].upper()

                if index + 1 == len(self.accept):
                    accept_text += _(" and %s") % text
                elif index == 0:
                    accept_text += text
                else:
                    accept_text += " ,%s" % text

            return _("The allowed formats are %s.") % accept_text

        return help_text

    def clean(self, *args, **kwargs):
        data = super().clean(*args, **kwargs)

        f = getattr(data, "file", None)
        size = getattr(data, "size", getattr(f, "size", None))
        content_type = getattr(data, "content_type", getattr(f, "content_type", None))

        if content_type and self.content_types:
            if content_type not in self.content_types:
                raise exceptions.ValidationError(
                    _("This filetype is not supported!"),
                    code="invalid",
                )

        if self.max_upload_size:
            if size and size > self.max_upload_size:
                raise exceptions.ValidationError(
                    _("Please keep filesize under %(max_upload_size)s. Current filesize is %(size)s.") % {
                        "max_upload_size": filesizeformat(self.max_upload_size),
                        "size": filesizeformat(size),
                    },
                    code="invalid",
                )

        return data


################################################################################
# TINY MCE

class HTMLField(fields.CharField):
    widget = TincyMCE


################################################################################
# FILE TREE

class FileTreeField(fields.CharField):
    widget = FileTree

    def __init__(self, accept_extensions=None, accept_folder=None, root=None, view=None, **kwargs):
        self.accept_extensions = accept_extensions and json.dumps(accept_extensions) or False
        self.accept_folder = accept_folder and 1 or 0
        self.root = root
        self.view = view

        super().__init__(**kwargs)


################################################################################
# COLOR

class ColorField(fields.CharField):
    default_error_messages = {
        "invalid": "Enter a valid color value: e.g. \"#FF0022\"",
    }

    def clean(self, *args, **kwargs):
        data = super().clean(*args, **kwargs)

        if not re.match('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', data):
            raise exceptions.ValidationError(
                self.error_messages['invalid'],
                code="invalid",
            )

        return data
