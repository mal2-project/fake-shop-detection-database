from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from mal2.models.fields import (
    CreationDateTimeField,
    ModificationDateTimeField,
)
from mal2.utils import get_current_user


################################################################################
# AUTH STAMPED

class AuthStampedModel(models.Model):
    """
    An abstract base class model that provides auth information fields.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        editable=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created_by",
        verbose_name=_("Created by"),
    )

    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        editable=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_modified_by",
        verbose_name=_("Modified by"),
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()

        if user and user.is_authenticated:
            self.modified_by = user

            if self._state.adding:
                self.created_by = user

        super().save(*args, **kwargs)


################################################################################
# TIME STAMPED

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-managed "created" and
    "modified" fields.
    """

    created_at = CreationDateTimeField(
        verbose_name=_("Created at"),
    )

    modified_at = ModificationDateTimeField(
        verbose_name=_("Modified at"),
    )

    def save(self, **kwargs):
        self.update_modified = kwargs.pop(
            "update_modified",
            getattr(self, "update_modified", True)
        )

        super().save(**kwargs)

    class Meta:
        abstract = True
        get_latest_by = "modified_at"

        ordering = [
            "-modified_at",
            "-created_at",
        ]


################################################################################
# AUTH TIME STAMPED

class AuthTimeStampedModel(AuthStampedModel, TimeStampedModel):
    class Meta:
        abstract = True
