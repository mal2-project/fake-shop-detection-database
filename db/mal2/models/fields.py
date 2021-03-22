from django.db import models
from phonenumber_field import modelfields

from mal2.forms.fields import PhoneNumberField as fields_PhoneNumberField
from mal2.forms.widgets import TincyMCE


################################################################################
# DATE/TIME

class CreationDateTimeField(models.DateTimeField):
    """
    By default, sets editable=False, blank=True, auto_now_add=True
    """

    def __init__(self, *args, **kwargs):
        kwargs.update({
            "auto_now_add": True,
            "blank": True,
            "editable": False,
        })

        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return "DateTimeField"


class ModificationDateTimeField(models.DateTimeField):
    """
    By default, sets editable=False, blank=True, auto_now=True
    Sets value to now every time the object is saved.
    """

    def __init__(self, *args, **kwargs):
        kwargs.update({
            "auto_now": True,
            "blank": True,
            "editable": False,
        })

        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return "DateTimeField"

    def pre_save(self, model_instance, add):
        if not getattr(model_instance, "update_modified", True):
            return model_instance.modified

        return super().pre_save(model_instance, add)


################################################################################
# PHONE NUMBER

class PhoneNumberField(modelfields.PhoneNumberField):
    def formfield(self, **kwargs):
        defaults = {
            "form_class": fields_PhoneNumberField,
            "region": self.region,
            "error_messages": self.error_messages,
        }

        defaults.update(kwargs)

        return super().formfield(**defaults)


################################################################################
# TINY MCE

class HTMLField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {
            'widget': TincyMCE,
        }

        defaults.update(kwargs)

        return super(HTMLField, self).formfield(**defaults)
