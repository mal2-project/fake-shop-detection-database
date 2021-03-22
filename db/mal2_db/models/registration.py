from django.contrib.auth.models import (
    AbstractUser,
    UserManager,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


################################################################################
# USER

class UserManager(UserManager):
    use_in_migrations = False


class User(AbstractUser):
    objects = UserManager()

    first_name = models.CharField(
        blank=False,
        max_length=30,
        verbose_name=_("First name"),
    )

    last_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name=_("Last name"),
    )

    email = models.EmailField(
        blank=False,
        verbose_name=_("Email"),
    )

    class Meta:
        ordering = ("username",)
        verbose_name = _("User")
        verbose_name_plural = _("Users")
