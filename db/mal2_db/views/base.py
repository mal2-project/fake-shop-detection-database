import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.forms.models import model_to_dict
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django.views.generic.detail import SingleObjectMixin

from mal2.constants.data_table import OPTIONS_BOOLEAN
from mal2.views.data_table import (
    DataTableDataView,
    DataTableView,
)
from mal2.views.edit import (
    AjaxAddView,
    AjaxDeleteView,
    AjaxEditView,
)
from mal2.views.pdf import BasePDFView
from mal2_db.constants.db import (
    DB_COUNTERFEITE,
    DB_FAKE_SHOP,
)
from mal2_db.forms.base import (
    CompanyNameFormSetFactory,
    CounterfeiterForm,
    FakeShopForm,
    LanguageExampleFormSetFactory,
    LanguageUrlFormSetFactory,
    ProductExampleFormSetFactory,
    SearchResultFormSetFactory,
    WebsiteForm,
    WebsiteImageFormSetFactory,
    WebsiteTextFormSetFactory,
)
from mal2_db.models.base import (
    CompanyName,
    LanguageExample,
    LanguageUrl,
    ProductExample,
    SearchResult,
    Website,
    WebsiteCategory,
    WebsiteImage,
    WebsiteReportedBy,
    WebsiteRiskScore,
    WebsiteText,
    WebsiteType,
    mal2CounterfeitersDB,
    mal2FakeShopDB,
)
from mal2_db.models.registration import User


################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# HELPERS

class DetailsPDFView(SingleObjectMixin, BasePDFView):
    def _get_pdf_field_data(self, model, object_dict, fields, field_data=None):
        if not field_data:
            field_data = []

        for field in fields:
            if isinstance(field, tuple):
                objects = field[0].objects.filter(**{
                    "%s" % field[1]: self.object.id
                }).all()

                for object in objects:
                    sub_object_dict = model_to_dict(object)

                    field_data.append(
                        self._get_pdf_field_data(
                            field[0], sub_object_dict, field[2].get("fields"), field_data
                        )
                    )
            else:
                field_data.append({
                    "label": model._meta.get_field(field).verbose_name.title(),
                    "id": field,
                    "value": object_dict[field],
                })

        return field_data

    def get_document_title(self):
        return "%s %s" % (
            self.model._meta.verbose_name.title(),
            self.object,
        )

    def get_pdf_data(self):
        object_dict = model_to_dict(self.object)
        pdf_data = []

        for fieldset in self.fieldsets:
            fields = fieldset[1].get("fields")

            pdf_data.append({
                "legend": fieldset[0],
                "fields": self._get_pdf_field_data(self.model, object_dict, fields),
            })

        return pdf_data


################################################################################
# ALL WEBSITES

class AllWebsitesDataTableMixin(object):
    def get_data_table(self):
        return {
            "table": "check_websites",
            "options": {
                "order": "[[3, \"desc\"], [1, \"desc\"]]",
                "page-length": "50",
            },
            "urls": {
                "defaults": {
                    "attrs": {
                        "data-modal-link": True,
                    },
                    "template": "data_table/link.html",
                },
                "data": reverse_lazy("mal2_db:all_websites_data"),
                "add": {
                    "href": "mal2_db:add_website",
                    "text": _("Add website"),
                    "permissions": [
                        "mal2_db.add_website",
                    ],
                    "template": "data_table/add.html",
                },
                "item": [
                    {
                        "field_name": "edit",
                        "href": "mal2_db:edit_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.change_website",
                        ],
                        "context": {
                            "svg": "pencil",
                            "text": _("Edit website"),
                        },
                    },
                    {
                        "field_name": "delete",
                        "href": "mal2_db:delete_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.delete_website",
                        ],
                        "context": {
                            "icon_color": "danger",
                            "svg": "delete",
                            "text": _("Delete website"),
                        },
                    },
                ],
            },
            "row_id": "id",
            "field_names": [
                "id",
                "url",
                "risk_score__risk_score",
                "risk_score__name",
                "reported_by__reporter",
                "created_at",
                "assigned_to__username",
                "website_type__type",
                "website_type__id",
                "screenshot",
                "website_category__category",
            ],
            "field_hidden": [
                "risk_score__name",
                "website_type__id",
                "screenshot",
            ],
            "field_labels": {
                "risk_score__risk_score": _("Risk score"),
                "reported_by__reporter": _("Reported by"),
                "created_at": _("Reported at"),
                "assigned_to__username": _("Assigned to"),
                "website_type__type": _("Type"),
                "website_category__category": _("Category"),
            },
            "field_filters": {
                "regex_enabled": [
                ],
                "type": "collapse",
                # exclude is optional - it is possible to hide search fields for
                # specific columns (in collapse and colunn mode)
                "exclude": [
                    "risk_score__name",
                    "website_type__id",
                    "screenshot",
                ],
                # default_classes is optional col for all columns
                # you can specify specific columns class inside "custom" with
                # "classes" --> if nothing is provided default is "col-12 col-md-3"
                "default_classes": "col-12 col-md-3",
                # custom is optional -
                # filters get automatically created by field_names above
                # custom can customize a type of a field and add options for
                # type select or customize col classes with "classes"
                "custom": {
                    "id": {
                        "classes": "col-12 col-md-2",
                        "type": "number",
                    },
                    "url": {
                        "classes": "col-12 col-md-10",
                        "type": "text",
                    },
                    "risk_score__risk_score": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteRiskScore.objects.all().values_list("risk_score", "name")
                        ),
                        "type": "select",
                    },
                    "reported_by__reporter": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteReportedBy.objects.all().values_list("reporter", "reporter")
                        ),
                        "type": "select",
                    },
                    "created_at": {
                        "classes": "col-6 col-md-2",
                        "type": "date",
                    },
                    "assigned_to__username": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            User.objects.all().values_list("username", "username")
                        ),
                        "type": "select",
                    },
                    "website_type__type": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteType.objects.all().values_list("type", "type")
                        ),
                        "type": "select",
                    },
                    "website_category__category": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteCategory.objects.all().values_list("category", "category")
                        ),
                        "type": "select",
                    },
                },
            },
            "field_templates": {
                "url": "mal2_db/data_table/url.html",
                "risk_score__risk_score": "mal2_db/data_table/risk_score.html",
                "created_at": "data_table/datetime.html",
            },
            "responsive_priorities": {
                "id": 9995,
                "url": 9990,
                "risk_score__risk_score": 9996,
                "check_website": 9994,
                "edit": 9993,
                "delete": 9992,
            },
        }


class AllWebsitesDataTableView(PermissionRequiredMixin, AllWebsitesDataTableMixin, DataTableView):
    permission_required = "mal2_db.view_website"

    template_name = "mal2_db/data_table/all_websites.html"
    model = Website


class AllWebsitesDataTableDataView(PermissionRequiredMixin, AllWebsitesDataTableMixin, DataTableDataView):
    permission_required = "mal2_db.view_website"

    model = Website

    def get_objects(self):
        return self.model.objects.all()


################################################################################
# WEBSITES TO CHECK

class WebsitesToCheckDataTableMixin(object):
    def get_data_table(self):
        return {
            "table": "check_websites",
            "options": {
                # "autoreload": 3000,
                "order": "[[3, \"desc\"], [1, \"desc\"]]",
                "page-length": "50",
            },
            "urls": {
                "defaults": {
                    "attrs": {
                        "data-modal-link": True,
                    },
                    "template": "data_table/link.html",
                },
                "data": reverse_lazy("mal2_db:check_websites_data"),
                "add": {
                    "href": "mal2_db:add_website",
                    "text": _("Add website"),
                    "permissions": [
                        "mal2_db.add_website",
                    ],
                    "template": "data_table/add.html",
                },
                "item": [
                    {
                        "field_name": "check_website",
                        "href": "mal2_db:check_website",
                        "id": "id",
                        "template": "mal2_db/data_table/check_website.html",
                        "context": {
                            "text": _("Check website"),
                        },
                        "permissions": [
                            "mal2_db.check_website",
                        ],
                    },
                    {
                        "field_name": "edit",
                        "href": "mal2_db:edit_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.change_website",
                        ],
                        "context": {
                            "svg": "pencil",
                            "text": _("Edit website"),
                        },
                    },
                    {
                        "field_name": "delete",
                        "href": "mal2_db:delete_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.delete_website",
                        ],
                        "context": {
                            "icon_color": "danger",
                            "svg": "delete",
                            "text": _("Delete website"),
                        },
                    },
                ],
            },
            "row_id": "id",
            "field_names": [
                "id",
                "url",
                "risk_score__risk_score",
                "risk_score__name",
                "reported_by__reporter",
                "created_at",
                "assigned_to__username",
                "website_type__type",
                "website_type__id",
                "screenshot",
                "website_category__category",
            ],
            "field_hidden": [
                "risk_score__name",
                "website_type__id",
                "screenshot",
            ],
            "field_labels": {
                "risk_score__risk_score": _("Risk score"),
                "reported_by__reporter": _("Reported by"),
                "created_at": _("Reported at"),
                "assigned_to__username": _("Assigned to"),
                "website_type__type": _("Type"),
                "website_category__category": _("Category")
            },
            "field_filters": {
                "regex_enabled": [
                ],
                "type": "collapse",
                # exclude is optional - it is possible to hide search fields for
                # specific columns (in collapse and colunn mode)
                "exclude": [
                    "risk_score__name",
                    "website_type__id",
                    "screenshot",
                ],
                # default_classes is optional col for all columns
                # you can specify specific columns class inside "custom" with
                # "classes" --> if nothing is provided default is "col-12 col-md-3"
                "default_classes": "col-12 col-md-3",
                # custom is optional -
                # filters get automatically created by field_names above
                # custom can customize a type of a field and add options for
                # type select or customize col classes with "classes"
                "custom": {
                    "id": {
                        "classes": "col-12 col-md-2",
                        "type": "number",
                    },
                    "url": {
                        "classes": "col-12 col-md-10",
                        "type": "text",
                    },
                    "risk_score__risk_score": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteRiskScore.objects.all().values_list("risk_score", "name")
                        ),
                        "type": "select",
                    },
                    "reported_by__reporter": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteReportedBy.objects.all().values_list("reporter", "reporter")
                        ),
                        "type": "select",
                    },
                    "created_at": {
                        "classes": "col-6 col-md-2",
                        "type": "date",
                    },
                    "assigned_to__username": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            User.objects.all().values_list("username", "username")
                        ),
                        "type": "select",
                    },
                    "website_type__type": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteType.objects.all().values_list("type", "type")
                        ),
                        "type": "select",
                    },
                    "website_category__category": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteCategory.objects.all().values_list("category", "category")
                        ),
                        "type": "select",
                    },
                },
            },
            "field_templates": {
                "url": "mal2_db/data_table/url.html",
                "risk_score__risk_score": "mal2_db/data_table/risk_score.html",
                "created_at": "data_table/datetime.html",
            },
            "responsive_priorities": {
                "id": 9995,
                "url": 9990,
                "risk_score__risk_score": 9996,
                "check_website": 9994,
                "edit": 9993,
                "delete": 9992,
            },
        }


class WebsitesToCheckDataTableView(PermissionRequiredMixin, WebsitesToCheckDataTableMixin, DataTableView):
    permission_required = "mal2_db.view_website"

    template_name = "mal2_db/data_table/check_websites.html"
    model = Website


class WebsitesToCheckDataTableDataView(PermissionRequiredMixin, WebsitesToCheckDataTableMixin, DataTableDataView):
    permission_required = "mal2_db.view_website"

    model = Website

    def get_objects(self):
        return self.model.objects.to_check()


################################################################################
# SAFE WEBSITES

class WebsitesWithoutVerificationDataTableMixin(object):
    def get_data_table(self):
        return {
            "table": "check_websites",
            "options": {
                # "autoreload": 3000,
                "order": "[[1, \"desc\"]]",
                "page-length": "50",
            },
            "urls": {
                "defaults": {
                    "attrs": {
                        "data-modal-link": True,
                    },
                    "template": "data_table/link.html",
                },
                "data": reverse_lazy("mal2_db:safe_websites_data"),
                "item": [
                    {
                        "field_name": "edit",
                        "href": "mal2_db:edit_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.change_website",
                        ],
                        "context": {
                            "svg": "pencil",
                            "text": _("Edit website"),
                        },
                    },
                    {
                        "field_name": "delete",
                        "href": "mal2_db:delete_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.delete_website",
                        ],
                        "context": {
                            "icon_color": "danger",
                            "svg": "delete",
                            "text": _("Delete website"),
                        },
                    },
                ],
            },
            "row_id": "id",
            "field_names": [
                "id",
                "url",
                "risk_score__risk_score",
                "risk_score__name",
                "reported_by__reporter",
                "created_at",
                "assigned_to__username",
                "screenshot",
            ],
            "field_hidden": [
                "risk_score__name",
                "screenshot",
            ],
            "field_labels": {
                "risk_score__risk_score": _("Risk score"),
                "reported_by__reporter": _("Reported by"),
                "created_at": _("Reported at"),
                "assigned_to__username": _("Assigned to"),
            },
            "field_filters": {
                "regex_enabled": [
                ],
                "type": "collapse",
                # exclude is optional - it is possible to hide search fields for
                # specific columns (in collapse and colunn mode)
                "exclude": [
                    "risk_score__name",
                    "screenshot",
                ],
                # default_classes is optional col for all columns
                # you can specify specific columns class inside "custom" with
                # "classes" --> if nothing is provided default is "col-12 col-md-3"
                "default_classes": "col-12 col-md-3",
                # custom is optional -
                # filters get automatically created by field_names above
                # custom can customize a type of a field and add options for
                # type select or customize col classes with "classes"
                "custom": {
                    "id": {
                        "classes": "col-12 col-md-2",
                        "type": "number",
                    },
                    "url": {
                        "classes": "col-12 col-md-10",
                        "type": "text",
                    },
                    "risk_score__risk_score": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteRiskScore.objects.all().values_list("risk_score", "name")
                        ),
                        "type": "select",
                    },
                    "reported_by__reporter": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteReportedBy.objects.all().values_list("reporter", "reporter")
                        ),
                        "type": "select",
                    },
                    "created_at": {
                        "classes": "col-6 col-md-2",
                        "type": "date",
                    },
                    "assigned_to__username": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            User.objects.all().values_list("username", "username")
                        ),
                        "type": "select",
                    },
                },
            },
            "field_templates": {
                "url": "mal2_db/data_table/url.html",
                "risk_score__risk_score": "mal2_db/data_table/risk_score.html",
                "created_at": "data_table/datetime.html",
            },
            "responsive_priorities": {
                "id": 9994,
                "url": 9990,
                "risk_score__risk_score": 9995,
                "edit": 9993,
                "delete": 9992,
            },
        }


class WebsitesNoVerificationRequiredDataTableView(PermissionRequiredMixin, WebsitesWithoutVerificationDataTableMixin, DataTableView):
    permission_required = "mal2_db.view_website"

    template_name = "mal2_db/data_table/safe_websites.html"
    model = Website


class WebsitesNoVerificationRequiredDataTableDataView(PermissionRequiredMixin, WebsitesWithoutVerificationDataTableMixin, DataTableDataView):
    permission_required = "mal2_db.view_website"

    model = Website

    def get_objects(self):
        return self.model.objects.without_verification()


################################################################################
# UNSURE WEBSITES

class WebsitesUnsureDataTableMixin(object):
    def get_data_table(self):
        return {
            "table": "unsure_websites",
            "options": {
                # "autoreload": 3000,
                "order": "[[1, \"desc\"]]",
                "page-length": "50",
            },
            "urls": {
                "defaults": {
                    "attrs": {
                        "data-modal-link": True,
                    },
                    "template": "data_table/link.html",
                },
                "data": reverse_lazy("mal2_db:unsure_websites_data"),
                "item": [
                    {
                        "field_name": "edit",
                        "href": "mal2_db:edit_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.change_website",
                        ],
                        "context": {
                            "svg": "pencil",
                            "text": _("Edit website"),
                        },
                    },
                    {
                        "field_name": "delete",
                        "href": "mal2_db:delete_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.delete_website",
                        ],
                        "context": {
                            "icon_color": "danger",
                            "svg": "delete",
                            "text": _("Delete website"),
                        },
                    },
                ],
            },
            "row_id": "id",
            "field_names": [
                "id",
                "url",
                "risk_score__risk_score",
                "risk_score__name",
                "reported_by__reporter",
                "created_at",
                "assigned_to__username",
                "screenshot",
            ],
            "field_hidden": [
                "risk_score__name",
                "screenshot",
            ],
            "field_labels": {
                "risk_score__risk_score": _("Risk score"),
                "reported_by__reporter": _("Reported by"),
                "created_at": _("Reported at"),
                "assigned_to__username": _("Assigned to"),
            },
            "field_filters": {
                "regex_enabled": [
                ],
                "type": "collapse",
                # exclude is optional - it is possible to hide search fields for
                # specific columns (in collapse and colunn mode)
                "exclude": [
                    "risk_score__name",
                    "screenshot",
                ],
                # default_classes is optional col for all columns
                # you can specify specific columns class inside "custom" with
                # "classes" --> if nothing is provided default is "col-12 col-md-3"
                "default_classes": "col-12 col-md-3",
                # custom is optional -
                # filters get automatically created by field_names above
                # custom can customize a type of a field and add options for
                # type select or customize col classes with "classes"
                "custom": {
                    "id": {
                        "classes": "col-12 col-md-2",
                        "type": "number",
                    },
                    "url": {
                        "classes": "col-12 col-md-10",
                        "type": "text",
                    },
                    "risk_score__risk_score": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteRiskScore.objects.all().values_list("risk_score", "name")
                        ),
                        "type": "select",
                    },
                    "reported_by__reporter": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteReportedBy.objects.all().values_list("reporter", "reporter")
                        ),
                        "type": "select",
                    },
                    "created_at": {
                        "classes": "col-6 col-md-2",
                        "type": "date",
                    },
                    "assigned_to__username": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            User.objects.all().values_list("username", "username")
                        ),
                        "type": "select",
                    },
                },
            },
            "field_templates": {
                "url": "mal2_db/data_table/url.html",
                "risk_score__risk_score": "mal2_db/data_table/risk_score.html",
                "created_at": "data_table/datetime.html",
            },
            "responsive_priorities": {
                "id": 9994,
                "url": 9990,
                "risk_score__risk_score": 9995,
                "edit": 9993,
                "delete": 9992,
            },
        }


class WebsitesUnsureDataTableView(PermissionRequiredMixin, WebsitesUnsureDataTableMixin, DataTableView):
    permission_required = "mal2_db.view_website"

    template_name = "mal2_db/data_table/unsure_websites.html"
    model = Website


class WebsitesUnsureDataTableDataView(PermissionRequiredMixin, WebsitesUnsureDataTableMixin, DataTableDataView):
    permission_required = "mal2_db.view_website"

    model = Website

    def get_objects(self):
        return self.model.objects.unsure()


################################################################################
# EDIT UNSURE WEBSITE

class EditDisagreementWebsiteView(PermissionRequiredMixin, AjaxEditView):
    permission_required = "mal2_db.change_website"

    template_name = "mal2_db/dialog/edit_website.html"
    model = Website

    form_class = WebsiteForm
    pk_url_kwarg = "id"

    extra_context = {
        "datatable": True,
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs.update({
            "admin_edit": True,
        })

        return kwargs


################################################################################
# DISAGREEMENT WEBSITES

class WebsitesDisagreementDataTableMixin(object):
    def get_data_table(self):
        return {
            "table": "disagreement_websites",
            "options": {
                # "autoreload": 3000,
                "order": "[[1, \"desc\"]]",
                "page-length": "50",
            },
            "urls": {
                "defaults": {
                    "attrs": {
                        "data-modal-link": True,
                    },
                    "template": "data_table/link.html",
                },
                "data": reverse_lazy("mal2_db:disagreement_websites_data"),
                "item": [
                    {
                        "field_name": "edit",
                        "href": "mal2_db:edit_disagreement_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.change_website",
                        ],
                        "context": {
                            "svg": "pencil",
                            "text": _("Edit website"),
                        },
                    },
                    {
                        "field_name": "delete",
                        "href": "mal2_db:delete_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.delete_website",
                        ],
                        "context": {
                            "icon_color": "danger",
                            "svg": "delete",
                            "text": _("Delete website"),
                        },
                    },
                ],
            },
            "row_id": "id",
            "field_names": [
                "id",
                "url",
                "risk_score__risk_score",
                "risk_score__name",
                "reported_by__reporter",
                "created_at",
                "assigned_to__username",
                "screenshot",
            ],
            "field_hidden": [
                "risk_score__name",
                "screenshot",
            ],
            "field_labels": {
                "risk_score__risk_score": _("Risk score"),
                "reported_by__reporter": _("Reported by"),
                "created_at": _("Reported at"),
                "assigned_to__username": _("Assigned to"),
            },
            "field_filters": {
                "regex_enabled": [
                ],
                "type": "collapse",
                # exclude is optional - it is possible to hide search fields for
                # specific columns (in collapse and colunn mode)
                "exclude": [
                    "risk_score__name",
                    "screenshot",
                ],
                # default_classes is optional col for all columns
                # you can specify specific columns class inside "custom" with
                # "classes" --> if nothing is provided default is "col-12 col-md-3"
                "default_classes": "col-12 col-md-3",
                # custom is optional -
                # filters get automatically created by field_names above
                # custom can customize a type of a field and add options for
                # type select or customize col classes with "classes"
                "custom": {
                    "id": {
                        "classes": "col-12 col-md-2",
                        "type": "number",
                    },
                    "url": {
                        "classes": "col-12 col-md-10",
                        "type": "text",
                    },
                    "risk_score__risk_score": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteRiskScore.objects.all().values_list("risk_score", "name")
                        ),
                        "type": "select",
                    },
                    "reported_by__reporter": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteReportedBy.objects.all().values_list("reporter", "reporter")
                        ),
                        "type": "select",
                    },
                    "created_at": {
                        "classes": "col-6 col-md-2",
                        "type": "date",
                    },
                    "assigned_to__username": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            User.objects.all().values_list("username", "username")
                        ),
                        "type": "select",
                    },
                },
            },
            "field_templates": {
                "url": "mal2_db/data_table/url.html",
                "risk_score__risk_score": "mal2_db/data_table/risk_score.html",
                "created_at": "data_table/datetime.html",
            },
            "responsive_priorities": {
                "id": 9994,
                "url": 9990,
                "risk_score__risk_score": 9995,
                "edit": 9993,
                "delete": 9992,
            },
        }


class WebsitesDisagreementDataTableView(PermissionRequiredMixin, WebsitesDisagreementDataTableMixin, DataTableView):
    permission_required = "mal2_db.view_website"

    template_name = "mal2_db/data_table/disagreement_websites.html"
    model = Website


class WebsitesDisagreementDataTableDataView(PermissionRequiredMixin, WebsitesDisagreementDataTableMixin, DataTableDataView):
    permission_required = "mal2_db.view_website"

    model = Website

    def get_objects(self):
        return self.model.objects.disagreement()


################################################################################
# ADD WEBSITE

class AddWebsiteView(PermissionRequiredMixin, AjaxAddView):
    permission_required = "mal2_db.add_website"

    template_name = "mal2_db/dialog/add_website.html"
    model = Website
    form_class = WebsiteForm

    extra_context = {
        "datatable": True,
    }


################################################################################
# EDIT WEBSITE

class EditWebsiteView(PermissionRequiredMixin, AjaxEditView):
    permission_required = "mal2_db.change_website"

    template_name = "mal2_db/dialog/edit_website.html"
    model = Website

    form_class = WebsiteForm
    pk_url_kwarg = "id"

    extra_context = {
        "datatable": True,
    }


################################################################################
# DELETE WEBSITE

class DeleteWebsiteView(PermissionRequiredMixin, AjaxDeleteView):
    permission_required = "mal2_db.delete_website"

    template_name = "mal2_db/dialog/delete_website.html"
    model = Website

    pk_url_kwarg = "id"

    extra_context = {
        "datatable": True,
    }


################################################################################
# CHECK WEBSITE

class CheckWebsiteView(PermissionRequiredMixin, RedirectView):
    permission_required = "mal2_db.check_website"

    def dispatch(self, request, *args, **kwargs):
        self.website = get_object_or_404(Website, pk=kwargs.get("id"))

        if self.website.assigned_to is None or not self.website.website_type:
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        website_type = self.website.website_type.id

        if website_type == DB_FAKE_SHOP:
            return reverse_lazy("mal2_db:add_fake_shop", kwargs={
                "website_id": self.website.id,
            })
        elif website_type == DB_COUNTERFEITE:
            return reverse_lazy("mal2_db:add_counterfeiter", kwargs={
                "website_id": self.website.id,
            })


################################################################################
# FAKE SHOP

class FakeShopDataTableMixin(object):
    def get_data_table(self):
        return {
            "table": "fakeshop",
            "options": {
                # "autoreload": 3000,
                "order": "[[1, \"desc\"]]",
                "page-length": "50",
            },
            "urls": {
                "defaults": {
                    "attrs": {
                        "data-modal-link": True,
                    },
                    "template": "data_table/link.html",
                },
                "data": reverse_lazy("mal2_db:fake_shop_data"),
                "add": {
                    "href": "mal2_db:add_fake_shop",
                    "text": _("Add fake shop"),
                    "permissions": [
                        "mal2_db.add_mal2fakeshopdb",
                    ],
                    "template": "data_table/add.html",
                },
                "item": [
                    {
                        "field_name": "details",
                        "href": "mal2_db:fake_shop_details",
                        "id": "id",
                        "template": "mal2_db/data_table/details.html",
                        "context": {
                            "text": _("Fake shop details"),
                        },
                        "permissions": [
                            "mal2_db.view_mal2fakeshopdb",
                        ],
                    },
                    {
                        "field_name": "edit",
                        "href": "mal2_db:edit_fake_shop",
                        "id": "id",
                        "permissions": [
                            "mal2_db.change_mal2fakeshopdb",
                        ],
                        "context": {
                            "svg": "pencil",
                            "text": _("Edit fake shop"),
                        },
                    },
                    {
                        "field_name": "delete",
                        "href": "mal2_db:delete_fake_shop",
                        "id": "id",
                        "permissions": [
                            "mal2_db.delete_mal2fakeshopdb",
                        ],
                        "context": {
                            "icon_color": "danger",
                            "svg": "delete",
                            "text": _("Delete fake shop"),
                        },
                    },
                ],
            },
            "row_id": "id",
            "field_names": [
                "id",
                "url",
                "product_name",
                "website__risk_score__name",
                "website__risk_score__risk_score",
                "suspected_fraud_search",
                "suspected_fraud_price_comparison",
                "suspected_fraud_payment_method",
                "suspected_fraud_company_data",
                "suspected_fraud_vat",
                "suspected_fraud_domain",
                "suspected_fraud_images",
                "suspected_fraud_website_text",
                "suspected_fraud_quality_mark_seal",
                "website__assigned_to__username",
                "website__screenshot",
            ],
            "field_hidden": [
                "website__risk_score__name",
                "website__screenshot",
            ],
            "field_labels": {
                "suspected_fraud_search": _("Search"),
                "suspected_fraud_price_comparison": _("Price comparison"),
                "suspected_fraud_payment_method": _("Payment method"),
                "suspected_fraud_company_data": _("Company data"),
                "suspected_fraud_vat": _("VAT"),
                "suspected_fraud_domain": _("Domain"),
                "suspected_fraud_images": _("Images"),
                "suspected_fraud_website_text": _("Text"),
                "suspected_fraud_quality_mark_seal": _("Quality mark"),
                "website__risk_score__risk_score": _("Risk score"),
                "website__assigned_to__username": _("Checked by"),
            },
            "field_filters": {
                "regex_enabled": [
                ],
                "type": "collapse",
                # exclude is optional - it is possible to hide search fields for
                # specific columns (in collapse and colunn mode)
                "exclude": [
                    "website__risk_score__name",
                    "website__screenshot",
                ],
                # default_classes is optional col for all columns
                # you can specify specific columns class inside "custom" with
                # "classes" --> if nothing is provided default is "col-12 col-md-3"
                "default_classes": "col-12 col-md-3",
                # custom is optional -
                # filters get automatically created by field_names above
                # custom can customize a type of a field and add options for
                # type select or customize col classes with "classes"
                "custom": {
                    "id": {
                        "classes": "col-12 col-md-2",
                        "type": "number",
                    },
                    "url": {
                        "classes": "col-12 col-md-5",
                        "type": "text",
                    },
                    "product_name": {
                        "classes": "col-12 col-md-5",
                        "type": "text",
                    },
                    "suspected_fraud_search": {
                        "classes": "col-6 col-md-2",
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                    "suspected_fraud_price_comparison": {
                        "classes": "col-6 col-md-2",
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                    "suspected_fraud_payment_method": {
                        "classes": "col-6 col-md-2",
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                    "suspected_fraud_company_data": {
                        "classes": "col-6 col-md-2",
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                    "suspected_fraud_vat": {
                        "classes": "col-6 col-md-2",
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                    "suspected_fraud_domain": {
                        "classes": "col-6 col-md-2",
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                    "suspected_fraud_images": {
                        "classes": "col-6 col-md-2",
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                    "suspected_fraud_website_text": {
                        "classes": "col-6 col-md-2",
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                    "suspected_fraud_quality_mark_seal": {
                        "classes": "col-6 col-md-2",
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                    "website__risk_score__risk_score": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteRiskScore.objects.all().values_list("risk_score", "name")
                        ),
                        "type": "select",
                    },
                    "website__assigned_to__username": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            User.objects.all().values_list("username", "username")
                        ),
                        "type": "select",
                    },
                }
            },
            "field_templates": {
                "url": "mal2_db/data_table/db_url.html",
                "website__risk_score__risk_score": "mal2_db/data_table/risk_score.html",
                "suspected_fraud_search": "data_table/boolean.html",
                "suspected_fraud_price_comparison": "data_table/boolean.html",
                "suspected_fraud_payment_method": "data_table/boolean.html",
                "suspected_fraud_company_data": "data_table/boolean.html",
                "suspected_fraud_vat": "data_table/boolean.html",
                "suspected_fraud_domain": "data_table/boolean.html",
                "suspected_fraud_images": "data_table/boolean.html",
                "suspected_fraud_website_text": "data_table/boolean.html",
                "suspected_fraud_quality_mark_seal": "data_table/boolean.html",
            },
            "responsive_priorities": {
                "id": 9994,
                "url": 9990,
                "website__assigned_to__username": 9995,
                "details": 9993,
                "edit": 9992,
                "delete": 9991,
            },
        }


class FakeShopDataTableView(PermissionRequiredMixin, FakeShopDataTableMixin, DataTableView):
    permission_required = "mal2_db.view_mal2fakeshopdb"

    template_name = "mal2_db/data_table/fake_shop.html"
    model = mal2FakeShopDB


class FakeShopDataTableDataView(PermissionRequiredMixin, FakeShopDataTableMixin, DataTableDataView):
    permission_required = "mal2_db.view_mal2fakeshopdb"

    model = mal2FakeShopDB


################################################################################
# FAKE SHOP MIXIN

class FakeShopMixin(object):
    def get_formsets_data(self, data=None, instance=None):
        return [
            {
                "after_field": "search_term",
                "formset_factory": SearchResultFormSetFactory(
                    data=data,
                    instance=instance,
                ),
            },
            {
                "after_field": "different_company_names",
                "formset_factory": CompanyNameFormSetFactory(
                    data=data,
                    instance=instance,
                ),
            },
            {
                "after_field": "copied_website_images",
                "formset_factory": WebsiteImageFormSetFactory(
                    data=data,
                    instance=instance,
                ),
            },
            {
                "after_field": "website_text_example",
                "formset_factory": WebsiteTextFormSetFactory(
                    data=data,
                    instance=instance,
                ),
            },
            {
                "after_field": "changing_languages_available",
                "formset_factory": LanguageExampleFormSetFactory(
                    data=data,
                    instance=instance,
                ),
            },
        ]


################################################################################
# ADD FAKE SHOP

class AddFakeShopView(PermissionRequiredMixin, FakeShopMixin, AjaxAddView):
    permission_required = "mal2_db.add_mal2fakeshopdb"

    template_name = "mal2_db/dialog/add_fake_shop.html"
    model = mal2FakeShopDB
    form_class = FakeShopForm

    extra_context = {
        "datatable": True,
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs.update({
            "website_id": self.kwargs.get("website_id", None),
        })

        return kwargs


################################################################################
# EDIT FAKE SHOP

class EditFakeShopView(PermissionRequiredMixin, FakeShopMixin, AjaxEditView):
    permission_required = "mal2_db.change_mal2fakeshopdb"

    template_name = "mal2_db/dialog/edit_fake_shop.html"
    model = mal2FakeShopDB

    form_class = FakeShopForm
    pk_url_kwarg = "id"

    extra_context = {
        "datatable": True,
    }


################################################################################
# DELETE FAKE SHOP

class DeleteFakeShopView(PermissionRequiredMixin, AjaxDeleteView):
    permission_required = "mal2_db.delete_mal2fakeshopdb"

    template_name = "mal2_db/dialog/delete_fake_shop.html"
    model = mal2FakeShopDB

    pk_url_kwarg = "id"

    extra_context = {
        "datatable": True,
    }


################################################################################
# FAKE SHOP DETAILS

class FakeShopDetailsView(PermissionRequiredMixin, DetailsPDFView):
    permission_required = "mal2_db.view_mal2fakeshopdb"

    template_name = "mal2_db/pdf/details.rml"
    model = mal2FakeShopDB

    pk_url_kwarg = "id"

    def dispatch(self, request, *args, **kwargs):
        self.fieldsets = (
            (None, {
                "fields": (
                    "url",
                ),
            }),
            (_("Search"), {
                "fields": (
                    "search_term",
                    (SearchResult, "mal2_db", {
                        "fields": (
                            "result_url",
                        )
                    }),
                    "suspected_fraud_search",
                ),
            }),
            (_("Price comparison"), {
                "fields": (
                    "product_url",
                    "product_name",
                    "product_reason",
                    "price_comparison_geizhals_eu_url",
                    "price_comparison_reason",
                    "suspected_fraud_price_comparison",
                ),
            }),
            (_("Payment method"), {
                "fields": (
                    "terms_of_payment_url",
                    "checkout_page_address_url",
                    "checkout_page_payment_method_url",
                    "payment_method_assessment",
                    "suspected_fraud_payment_method",
                ),
            }),
            (_("Evaluation"), {
                "fields": (
                    "is_fake",
                ),
            }),
            (_("Database queries"), {
                "fields": (
                    "imprint",
                    "database_search_term",
                    "is_wko_checked",
                    "is_handelsregister_de_checked",
                    "is_justice_europe_checked",
                    "database_review_result",
                    "suspected_fraud_company_data",
                ),
            }),
            (_("VAT"), {
                "fields": (
                    "vat",
                    "vat_review_result",
                    "suspected_fraud_vat",
                ),
            }),
            (_("Domain"), {
                "fields": (
                    "domain_whois_url",
                    "domain_registration_check",
                    "domain_registration_contradiction_url",
                    "domain_registrar",
                    "suspected_fraud_domain",
                    "domain_is_fake",
                ),
            }),
            (_("Company name"), {
                "fields": (
                    "different_company_names",
                    (CompanyName, "mal2_db", {
                        "fields": (
                            "company_name_url",
                        )
                    }),
                ),
            }),
            (_("Images"), {
                "fields": (
                    "can_not_copy_website_images",
                    "copied_website_images",
                    (WebsiteImage, "mal2_db", {
                        "fields": (
                            "image_url",
                        )
                    }),
                    "suspected_fraud_images",
                ),
            }),
            (_("Text"), {
                "fields": (
                    "can_not_copy_website_text",
                    "checked_website_text_url",
                    "website_text_example",
                    (WebsiteText, "mal2_db", {
                        "fields": (
                            "website_text_url",
                        )
                    }),
                    "suspected_fraud_website_text",
                ),
            }),
            (_("Language"), {
                "fields": (
                    "changing_languages_available",
                    (LanguageExample, "mal2_db", {
                        "fields": (
                            "language_example_url",
                        )
                    }),
                ),
            }),
            (_("General conditions of contract"), {
                "fields": (
                    "terms_and_conditions_of_contract_url",
                    "very_short_terms",
                ),
            }),
            (_("Label/seal"), {
                "fields": (
                    "suspected_fraud_quality_mark_seal",
                    "quality_mark_url",
                    "is_guetezeichen_at_checked",
                    "is_ehi_seal_checked",
                    "is_trusted_shops_checked",
                    "is_fictitious_quality_marks",
                    "fictitious_quality_mark_url",
                ),
            }),
            (_("Evaluation"), {
                "fields": (
                    "further_review_is_fake",
                ),
            }),
        )

        self.object = self.get_object()

        return super().dispatch(request, *args, **kwargs)


################################################################################
# COUNTERFEITS

class CounterfeitersDataTableMixin(object):
    def get_data_table(self):
        return {
            "table": "brand_counterfeiters",
            "options": {
                # "autoreload": 3000,
                "order": "[[1, \"desc\"]]",
                "page-length": "50",
            },
            "urls": {
                "defaults": {
                    "attrs": {
                        "data-modal-link": True,
                    },
                    "template": "data_table/link.html",
                },
                "data": reverse_lazy("mal2_db:counterfeiters_data"),
                "add": {
                    "href": "mal2_db:add_counterfeiter",
                    "text": _("Add brand counterfeiter"),
                    "permissions": [
                        "mal2_db.add_mal2counterfeitersdb",
                    ],
                    "template": "data_table/add.html",
                },
                "item": [
                    {
                        "field_name": "details",
                        "href": "mal2_db:counterfeiter_details",
                        "id": "id",
                        "template": "mal2_db/data_table/details.html",
                        "context": {
                            "text": _("Brand counterfeiter details"),
                        },
                        "permissions": [
                            "mal2_db.change_mal2counterfeitersdb",
                        ],
                    },
                    {
                        "field_name": "edit",
                        "href": "mal2_db:edit_counterfeiter",
                        "id": "id",
                        "permissions": [
                            "mal2_db.change_mal2counterfeitersdb",
                        ],
                        "context": {
                            "svg": "pencil",
                            "text": _("Edit brand counterfeiter"),
                        },
                    },
                    {
                        "field_name": "delete",
                        "href": "mal2_db:delete_counterfeiter",
                        "id": "id",
                        "permissions": [
                            "mal2_db.delete_mal2counterfeitersdb",
                        ],
                        "context": {
                            "icon_color": "danger",
                            "svg": "delete",
                            "text": _("Delete brand counterfeiter"),
                        },
                    },
                ],
            },
            "row_id": "id",
            "field_names": [
                "id",
                "url",
                "website__risk_score__risk_score",
                "website__risk_score__name",
                "domain_is_counterfeiter",
                "imprint_is_counterfeiter",
                "language_is_counterfeiter",
                "website__assigned_to__username",
                "website__screenshot",
            ],
            "field_hidden": [
                "website__risk_score__name",
                "website__screenshot",
            ],
            "field_labels": {
                "website__risk_score__risk_score": _("Risk score"),
                "domain_is_counterfeiter": _("Domain"),
                "imprint_is_counterfeiter": _("Imprint"),
                "language_is_counterfeiter": _("Language"),
                "website__assigned_to__username": _("Checked by"),
            },
            "field_filters": {
                "regex_enabled": [
                ],
                "type": "collapse",
                # exclude is optional - it is possible to hide search fields for
                # specific columns (in collapse and colunn mode)
                "exclude": [
                    "website__risk_score__name",
                    "website__screenshot",
                ],
                # default_classes is optional col for all columns
                # you can specify specific columns class inside "custom" with
                # "classes" --> if nothing is provided default is "col-12 col-md-3"
                "default_classes": "col-12 col-md-3",
                # custom is optional -
                # filters get automatically created by field_names above
                # custom can customize a type of a field and add options for
                # type select or customize col classes with "classes"
                "custom": {
                    "id": {
                        "classes": "col-12 col-md-2",
                        "type": "number",
                    },
                    "url": {
                        "classes": "col-12 col-md-10",
                        "type": "text",
                    },
                    "domain_is_counterfeiter": {
                        "classes": "col-6 col-md-2",
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                    "imprint_is_counterfeiter": {
                        "classes": "col-6 col-md-2",
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                    "language_is_counterfeiter": {
                        "classes": "col-6 col-md-2",
                        "options": OPTIONS_BOOLEAN,
                        "type": "select",
                    },
                    "website__risk_score__risk_score": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteRiskScore.objects.all().values_list("risk_score", "name")
                        ),
                        "type": "select",
                    },
                    "website__assigned_to__username": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            User.objects.all().values_list("username", "username")
                        ),
                        "type": "select",
                    },
                },
            },
            "field_templates": {
                "url": "mal2_db/data_table/db_url.html",
                "domain_is_counterfeiter": "data_table/boolean.html",
                "imprint_is_counterfeiter": "data_table/boolean.html",
                "language_is_counterfeiter": "data_table/boolean.html",
                "website__risk_score__risk_score": "mal2_db/data_table/risk_score.html",
            },
            "responsive_priorities": {
                "id": 9994,
                "url": 9990,
                "website__assigned_to__username": 9995,
                "details": 9993,
                "edit": 9992,
                "delete": 9991,
            },
        }


class CounterfeitersDataTableView(PermissionRequiredMixin, CounterfeitersDataTableMixin, DataTableView):
    permission_required = "mal2_db.view_mal2counterfeitersdb"

    template_name = "mal2_db/data_table/counterfeiter.html"
    model = mal2CounterfeitersDB


class CounterfeitersDataTableDataView(PermissionRequiredMixin, CounterfeitersDataTableMixin, DataTableDataView):
    permission_required = "mal2_db.view_mal2counterfeitersdb"

    model = mal2CounterfeitersDB


################################################################################
# COUNTERFEITS MIXIN

class CounterfeitersMixin(object):
    def get_formsets_data(self, data=None, instance=None):
        return [
            {
                "after_field": "no_product_description",
                "formset_factory": ProductExampleFormSetFactory(
                    data=data,
                    instance=instance,
                ),
            },
            {
                "after_field": "switching_language",
                "formset_factory": LanguageUrlFormSetFactory(
                    data=data,
                    instance=instance,
                ),
            },
        ]


###########################################################################
# ADD COUNTERFEITERS

class AddCounterfeiterView(PermissionRequiredMixin, CounterfeitersMixin, AjaxAddView):
    permission_required = "mal2_db.add_mal2counterfeitersdb"

    template_name = "mal2_db/dialog/add_counterfeiter.html"
    model = mal2CounterfeitersDB

    form_class = CounterfeiterForm

    extra_context = {
        "datatable": True,
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs.update({
            "website_id": self.kwargs.get("website_id", None),
        })

        return kwargs


################################################################################
# EDIT COUNTERFEITER

class EditCounterfeiterView(PermissionRequiredMixin, CounterfeitersMixin, AjaxEditView):
    permission_required = "mal2_db.change_mal2counterfeitersdb"

    template_name = "mal2_db/dialog/edit_counterfeiter.html"
    model = mal2CounterfeitersDB

    form_class = CounterfeiterForm
    pk_url_kwarg = "id"

    extra_context = {
        "datatable": True,
    }


################################################################################
# DELETE COUNTERFEITER

class DeleteCounterfeiterView(PermissionRequiredMixin, AjaxDeleteView):
    permission_required = "mal2_db.delete_mal2counterfeitersdb"

    template_name = "mal2_db/dialog/delete_counterfeiter.html"
    model = mal2CounterfeitersDB

    pk_url_kwarg = "id"

    extra_context = {
        "datatable": True,
    }


################################################################################
# COUNTERFEITER DETAILS

class CounterfeiterDetailsView(PermissionRequiredMixin, DetailsPDFView):
    permission_required = "mal2_db.delete_mal2counterfeitersdb"

    template_name = "mal2_db/pdf/details.rml"
    model = mal2CounterfeitersDB

    pk_url_kwarg = "id"

    def dispatch(self, request, *args, **kwargs):
        self.fieldsets = (
            (None, {
                "fields": (
                    "url",
                    "website",
                    "domain_is_plausible",
                    "has_discount",
                    "no_ssl",
                    "has_currency_selection",
                    "domain_is_counterfeiter"
                ),
            }),
            (_("Products"), {
                "fields": (
                    "products_in_stock",
                    "no_product_description",
                    (ProductExample, "mal2_counterfeiter", {
                        "fields": (
                            "product_example_url",
                        )
                    }),
                ),
            }),
            (_("Contact and Imprint"), {
                "fields": (
                    "contact_url",
                    "has_contact_mail",
                    "imprint",
                    "has_no_imprint",
                    "terms_and_conditions_of_contract_url",
                    "has_no_terms_and_conditions",
                    "imprint_is_counterfeiter",
                )
            }),
            (_("Language"), {
                "fields": (
                    "switching_language",
                    (LanguageUrl, "mal2_counterfeiter", {
                        "fields": (
                            "language_url",
                        )
                    }),
                    "language_is_counterfeiter",
                )
            })
        )

        self.object = self.get_object()

        return super().dispatch(request, *args, **kwargs)


################################################################################
# CHECKED - NO FAKE
class WebsitesNoFakeDataTableMixin(object):
    def get_data_table(self):
        return {
            "table": "check_websites_no_fake",
            "options": {
                # "autoreload": 3000,
                "order": "[[1, \"desc\"]]",
                "page-length": "50",
            },
            "urls": {
                "defaults": {
                    "attrs": {
                        "data-modal-link": True,
                    },
                    "template": "data_table/link.html",
                },
                "data": reverse_lazy("mal2_db:no_fake_websites_data"),
                "item": [
                    {
                        "field_name": "edit",
                        "href": "mal2_db:edit_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.change_website",
                        ],
                        "context": {
                            "svg": "pencil",
                            "text": _("Edit website"),
                        },
                    },
                    {
                        "field_name": "delete",
                        "href": "mal2_db:delete_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.delete_website",
                        ],
                        "context": {
                            "icon_color": "danger",
                            "svg": "delete",
                            "text": _("Delete website"),
                        },
                    },
                ],
            },
            "row_id": "id",
            "field_names": [
                "id",
                "url",
                "risk_score__risk_score",
                "risk_score__name",
                "reported_by__reporter",
                "created_at",
                "assigned_to__username",
                "screenshot",
                "website_category__category",
            ],
            "field_hidden": [
                "risk_score__name",
                "screenshot",
                "website_category__category",
            ],
            "field_labels": {
                "risk_score__risk_score": _("Risk score"),
                "reported_by__reporter": _("Reported by"),
                "created_at": _("Reported at"),
                "assigned_to__username": _("Assigned to"),
                "website_category__category": _("Category"),
            },
            "field_filters": {
                "regex_enabled": [
                ],
                "type": "collapse",
                # exclude is optional - it is possible to hide search fields for
                # specific columns (in collapse and colunn mode)
                "exclude": [
                    "risk_score__name",
                    "screenshot",
                ],
                # default_classes is optional col for all columns
                # you can specify specific columns class inside "custom" with
                # "classes" --> if nothing is provided default is "col-12 col-md-3"
                "default_classes": "col-12 col-md-3",
                # custom is optional -
                # filters get automatically created by field_names above
                # custom can customize a type of a field and add options for
                # type select or customize col classes with "classes"
                "custom": {
                    "id": {
                        "classes": "col-12 col-md-2",
                        "type": "number",
                    },
                    "url": {
                        "classes": "col-12 col-md-10",
                        "type": "text",
                    },
                    "risk_score__risk_score": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteRiskScore.objects.all().values_list("risk_score", "name")
                        ),
                        "type": "select",
                    },
                    "reported_by__reporter": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteReportedBy.objects.all().values_list("reporter", "reporter")
                        ),
                        "type": "select",
                    },
                    "created_at": {
                        "classes": "col-6 col-md-2",
                        "type": "date",
                    },
                    "assigned_to__username": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            User.objects.all().values_list("username", "username")
                        ),
                        "type": "select",
                    },
                    "website_category__category": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteCategory.objects.all().values_list("category", "category")
                        ),
                        "type": "select",
                    },
                },
            },
            "field_templates": {
                "url": "mal2_db/data_table/url.html",
                "risk_score__risk_score": "mal2_db/data_table/risk_score.html",
                "created_at": "data_table/datetime.html",
            },
            "responsive_priorities": {
                "id": 9994,
                "url": 9990,
                "risk_score__risk_score": 9995,
                "edit": 9993,
                "delete": 9992,
            },
        }


class WebsitesNoFakeDataTableView(PermissionRequiredMixin, WebsitesNoFakeDataTableMixin, DataTableView):
    permission_required = "mal2_db.view_website"

    template_name = "mal2_db/data_table/no_fake_websites.html"
    model = Website


class WebsitesNoFakeDataTableDataView(PermissionRequiredMixin, WebsitesNoFakeDataTableMixin, DataTableDataView):
    permission_required = "mal2_db.view_website"

    model = Website

    def get_objects(self):
        return self.model.objects.is_no_fake()


################################################################################
# OTHER WEBSITES
class WebsitesOtherTableMixin(object):
    def get_data_table(self):
        return {
            "table": "other_websites",
            "options": {
                # "autoreload": 3000,
                "order": "[[1, \"desc\"]]",
                "page-length": "50",
            },
            "urls": {
                "defaults": {
                    "attrs": {
                        "data-modal-link": True,
                    },
                    "template": "data_table/link.html",
                },
                "data": reverse_lazy("mal2_db:other_websites_data"),
                "item": [
                    {
                        "field_name": "edit",
                        "href": "mal2_db:edit_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.change_website",
                        ],
                        "context": {
                            "svg": "pencil",
                            "text": _("Edit website"),
                        },
                    },
                    {
                        "field_name": "delete",
                        "href": "mal2_db:delete_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.delete_website",
                        ],
                        "context": {
                            "icon_color": "danger",
                            "svg": "delete",
                            "text": _("Delete website"),
                        },
                    },
                ],
            },
            "row_id": "id",
            "field_names": [
                "id",
                "url",
                "risk_score__risk_score",
                "risk_score__name",
                "reported_by__reporter",
                "created_at",
                "assigned_to__username",
                "screenshot",
                "website_category__category",
            ],
            "field_hidden": [
                "risk_score__name",
                "screenshot",
                "website_category__category",
            ],
            "field_labels": {
                "risk_score__risk_score": _("Risk score"),
                "reported_by__reporter": _("Reported by"),
                "created_at": _("Reported at"),
                "assigned_to__username": _("Assigned to"),
                "website_category__category": _("Category"),
            },
            "field_filters": {
                "regex_enabled": [
                ],
                "type": "collapse",
                # exclude is optional - it is possible to hide search fields for
                # specific columns (in collapse and colunn mode)
                "exclude": [
                    "risk_score__name",
                    "screenshot",
                ],
                # default_classes is optional col for all columns
                # you can specify specific columns class inside "custom" with
                # "classes" --> if nothing is provided default is "col-12 col-md-3"
                "default_classes": "col-12 col-md-3",
                # custom is optional -
                # filters get automatically created by field_names above
                # custom can customize a type of a field and add options for
                # type select or customize col classes with "classes"
                "custom": {
                    "id": {
                        "classes": "col-12 col-md-2",
                        "type": "number",
                    },
                    "url": {
                        "classes": "col-12 col-md-10",
                        "type": "text",
                    },
                    "risk_score__risk_score": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteRiskScore.objects.all().values_list("risk_score", "name")
                        ),
                        "type": "select",
                    },
                    "reported_by__reporter": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteReportedBy.objects.all().values_list("reporter", "reporter")
                        ),
                        "type": "select",
                    },
                    "created_at": {
                        "classes": "col-6 col-md-2",
                        "type": "date",
                    },
                    "assigned_to__username": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            User.objects.all().values_list("username", "username")
                        ),
                        "type": "select",
                    },
                    "website_category__category": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteCategory.objects.all().values_list("category", "category")
                        ),
                        "type": "select",
                    },
                },
            },
            "field_templates": {
                "url": "mal2_db/data_table/url.html",
                "risk_score__risk_score": "mal2_db/data_table/risk_score.html",
                "created_at": "data_table/datetime.html",
            },
            "responsive_priorities": {
                "id": 9994,
                "url": 9990,
                "risk_score__risk_score": 9995,
                "edit": 9993,
                "delete": 9992,
            },
        }


class WebsitesOtherDataTableView(PermissionRequiredMixin, WebsitesOtherTableMixin, DataTableView):
    permission_required = "mal2_db.view_website"

    template_name = "mal2_db/data_table/other_websites.html"
    model = Website


class WebsitesOtherDataTableDataView(PermissionRequiredMixin, WebsitesOtherTableMixin, DataTableDataView):
    permission_required = "mal2_db.view_website"

    model = Website

    def get_objects(self):
        return self.model.objects.is_other_sites()


################################################################################
# ONLINE SHOPS

class WebsitesOnlineShopsTableMixin(object):
    def get_data_table(self):
        return {
            "table": "online_shops",
            "options": {
                # "autoreload": 3000,
                "order": "[[1, \"desc\"]]",
                "page-length": "50",
            },
            "urls": {
                "defaults": {
                    "attrs": {
                        "data-modal-link": True,
                    },
                    "template": "data_table/link.html",
                },
                "data": reverse_lazy("mal2_db:online_shop_data"),
                "item": [
                    {
                        "field_name": "edit",
                        "href": "mal2_db:edit_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.change_website",
                        ],
                        "context": {
                            "svg": "pencil",
                            "text": _("Edit website"),
                        },
                    },
                    {
                        "field_name": "delete",
                        "href": "mal2_db:delete_website",
                        "id": "id",
                        "permissions": [
                            "mal2_db.delete_website",
                        ],
                        "context": {
                            "icon_color": "danger",
                            "svg": "delete",
                            "text": _("Delete website"),
                        },
                    },
                ],
            },
            "row_id": "id",
            "field_names": [
                "id",
                "url",
                "risk_score__risk_score",
                "risk_score__name",
                "reported_by__reporter",
                "created_at",
                "assigned_to__username",
                "screenshot",
                "website_category__category",
            ],
            "field_hidden": [
                "risk_score__name",
                "screenshot",
                "website_category__category",
            ],
            "field_labels": {
                "risk_score__risk_score": _("Risk score"),
                "reported_by__reporter": _("Reported by"),
                "created_at": _("Reported at"),
                "assigned_to__username": _("Assigned to"),
                "website_category__category": _("Category"),
            },
            "field_filters": {
                "regex_enabled": [
                ],
                "type": "collapse",
                # exclude is optional - it is possible to hide search fields for
                # specific columns (in collapse and colunn mode)
                "exclude": [
                    "risk_score__name",
                    "screenshot",
                ],
                # default_classes is optional col for all columns
                # you can specify specific columns class inside "custom" with
                # "classes" --> if nothing is provided default is "col-12 col-md-3"
                "default_classes": "col-12 col-md-3",
                # custom is optional -
                # filters get automatically created by field_names above
                # custom can customize a type of a field and add options for
                # type select or customize col classes with "classes"
                "custom": {
                    "id": {
                        "classes": "col-12 col-md-2",
                        "type": "number",
                    },
                    "url": {
                        "classes": "col-12 col-md-10",
                        "type": "text",
                    },
                    "risk_score__risk_score": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteRiskScore.objects.all().values_list("risk_score", "name")
                        ),
                        "type": "select",
                    },
                    "reported_by__reporter": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteReportedBy.objects.all().values_list("reporter", "reporter")
                        ),
                        "type": "select",
                    },
                    "created_at": {
                        "classes": "col-6 col-md-2",
                        "type": "date",
                    },
                    "assigned_to__username": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            User.objects.all().values_list("username", "username")
                        ),
                        "type": "select",
                    },
                    "website_category__category": {
                        "classes": "col-6 col-md-2",
                        "options": list(
                            WebsiteCategory.objects.all().values_list("category", "category")
                        ),
                        "type": "select",
                    },
                },
            },
            "field_templates": {
                "url": "mal2_db/data_table/url.html",
                "risk_score__risk_score": "mal2_db/data_table/risk_score.html",
                "created_at": "data_table/datetime.html",
            },
            "responsive_priorities": {
                "id": 9994,
                "url": 9990,
                "risk_score__risk_score": 9995,
                "edit": 9993,
                "delete": 9992,
            },
        }


class WebsitesOnlineShopsDataTableView(PermissionRequiredMixin, WebsitesOnlineShopsTableMixin, DataTableView):
    permission_required = "mal2_db.view_website"

    template_name = "mal2_db/data_table/online_shop.html"
    model = Website


class WebsitesOnlineShopsDataTableDataView(PermissionRequiredMixin, WebsitesOnlineShopsTableMixin, DataTableDataView):
    permission_required = "mal2_db.view_website"

    model = Website

    def get_objects(self):
        return self.model.objects.is_online_shop()
