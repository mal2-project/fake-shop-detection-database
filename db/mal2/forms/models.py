from django.forms import models

from mal2.forms.widgets import Select


################################################################################
# SELECT

class ModelChoiceField(models.ModelChoiceField):
    widget = Select
