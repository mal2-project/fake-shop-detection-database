from django.core import exceptions
from django.db.models import Q
from django.forms import (
    HiddenInput,
    inlineformset_factory,
)
from django.shortcuts import (
    get_object_or_404,
)
from django.utils.translation import ugettext_lazy as _

from mal2.forms import (
    BaseInlineFormSet,
    FieldsetModelForm,
    ModelForm,
)
from mal2.utils import (
    remove_url_protocol,
    take_screenshot,
)
from mal2_db.constants.db import (
    DB_COUNTERFEITE,
    DB_FAKE_SHOP,
    WEBSITE_CATEGORY_UNKNOWN,
)
from mal2_db.models.base import (
    CompanyName,
    LanguageExample,
    LanguageUrl,
    ProductExample,
    SearchResult,
    Website,
    WebsiteImage,
    WebsiteText,
    mal2CounterfeitersDB,
    mal2FakeShopDB,
)


################################################################################
# WEBSITE

class WebsiteForm(FieldsetModelForm):
    class Meta:
        model = Website

        exclude = (
            "screenshot",
        )

    @property
    def grid_data(self):
        return {
            "url": "col-12 col-md-8",
            "risk_score": "col-12 col-md-4",
            "reported_by": "col-12 col-md-3",
            "assigned_to": "col-12 col-md-3",
            "website_type": "col-12 col-md-3",
            "website_category": "col-12 col-md-3",
        }

    @property
    def fieldsets_data(self):
        return [
            (None, {
                "fields": (
                    "url",
                    "risk_score",
                    "reported_by",
                    "assigned_to",
                    "website_type",
                    "website_category",
                ),
            }),
        ]

    def __init__(self, *args, **kwargs):
        self.admin_edit = kwargs.pop("admin_edit", False)

        super().__init__(*args, **kwargs)

        self.initial["assigned_to"] = self.request.user

        if not self.admin_edit:
            self.fields["website_category"].widget.attrs["readonly"] = True

        if not self.instance.website_category:
            self.initial["website_category"] = WEBSITE_CATEGORY_UNKNOWN

    def clean_url(self):
        url = self.cleaned_data["url"]
        url.strip("/")

        url_to_check = remove_url_protocol(url)

        website = Website.objects.filter(
            Q(url="http://%s" % url_to_check)
            | Q(url="https://%s" % url_to_check)
        ).first()

        if website and website.id != self.instance.id:
            raise exceptions.ValidationError(
                _("URL already exists in the database!"),
                code="invalid",
            )

        return url

    def save(self):
        data = self.cleaned_data
        website_type = data.get("website_type", [])

        website = super().save(commit=False)

        if not self.admin_edit:
            if website_type:
                website.website_category = website_type.default_category
            else:
                website.website_category_id = WEBSITE_CATEGORY_UNKNOWN

        website.save()

        take_screenshot(website)

        return website


################################################################################
# SEARCH RESULT

class SearchResultForm(ModelForm):
    class Meta:
        model = SearchResult

        fields = (
            "result_url",
        )

    @property
    def grid_data(self):
        return {
            "result_url": "col-12",
        }


class SearchResultInlineFormSet(BaseInlineFormSet):
    help_text = _("Enter URLs for search results")


SearchResultFormSetFactory = inlineformset_factory(
    parent_model=mal2FakeShopDB,
    model=SearchResult,
    can_delete=True,
    form=SearchResultForm,
    formset=SearchResultInlineFormSet,
    min_num=2,
    extra=0,
)


################################################################################
# COMPANY NAME

class CompanyNameForm(ModelForm):
    class Meta:
        model = CompanyName

        fields = (
            "company_name_url",
        )

    @property
    def grid_data(self):
        return {
            "company_name_url": "col-12",
        }


class CompanyNameInlineFormSet(BaseInlineFormSet):
    help_text = _("Enter URLs for company names")


CompanyNameFormSetFactory = inlineformset_factory(
    parent_model=mal2FakeShopDB,
    model=CompanyName,
    can_delete=True,
    form=CompanyNameForm,
    formset=CompanyNameInlineFormSet,
    min_num=2,
    extra=0,
)


################################################################################
# WEBSITE IMAGE

class WebsiteImageForm(ModelForm):
    class Meta:
        model = WebsiteImage

        fields = (
            "image_url",
        )

    @property
    def grid_data(self):
        return {
            "image_url": "col-12",
        }


class WebsiteImageInlineFormSet(BaseInlineFormSet):
    help_text = _("Enter URLs for website images")


WebsiteImageFormSetFactory = inlineformset_factory(
    parent_model=mal2FakeShopDB,
    model=WebsiteImage,
    can_delete=True,
    form=WebsiteImageForm,
    formset=WebsiteImageInlineFormSet,
    min_num=2,
    extra=0,
)


################################################################################
# WEBSITE TEXT

class WebsiteTextForm(ModelForm):
    class Meta:
        model = WebsiteText

        fields = (
            "website_text_url",
        )

    @property
    def grid_data(self):
        return {
            "website_text_url": "col-12",
        }


class WebsiteTextInlineFormSet(BaseInlineFormSet):
    help_text = _("Enter URLs that have the same website text")


WebsiteTextFormSetFactory = inlineformset_factory(
    parent_model=mal2FakeShopDB,
    model=WebsiteText,
    can_delete=True,
    form=WebsiteTextForm,
    formset=WebsiteTextInlineFormSet,
    min_num=2,
    extra=0,
)


################################################################################
# LANGUAGE EXAMPLE

class LanguageExampleForm(ModelForm):
    class Meta:
        model = LanguageExample

        fields = (
            "language_example_url",
        )

    @property
    def grid_data(self):
        return {
            "language_example_url": "col-12",
        }


class LanguageExampleInlineFormSet(BaseInlineFormSet):
    help_text = _("Enter URLs for language examples")


LanguageExampleFormSetFactory = inlineformset_factory(
    parent_model=mal2FakeShopDB,
    model=LanguageExample,
    can_delete=True,
    form=LanguageExampleForm,
    formset=LanguageExampleInlineFormSet,
    min_num=2,
    extra=0,
)


################################################################################
# PRODUCT EXAMPLE URL

class ProductExampleForm(ModelForm):
    class Meta:
        model = ProductExample

        fields = (
            "product_example_url",
        )

    @property
    def grid_data(self):
        return {
            "product_example_url": "col-12",
        }


class ProductExampleInlineFormSet(BaseInlineFormSet):
    help_text = _("Enter URLs for product examples")


ProductExampleFormSetFactory = inlineformset_factory(
    parent_model=mal2CounterfeitersDB,
    model=ProductExample,
    can_delete=True,
    form=ProductExampleForm,
    formset=ProductExampleInlineFormSet,
    min_num=2,
    extra=0,
)


################################################################################
# LANGUAGE URL

class LanguageUrlForm(ModelForm):
    class Meta:
        model = LanguageUrl

        fields = (
            "language_url",
        )

    @property
    def grid_data(self):
        return {
            "language_url": "col-12",
        }


class LanguageUrlInlineFormSet(BaseInlineFormSet):
    help_text = _("Enter URLs for product examples")


LanguageUrlFormSetFactory = inlineformset_factory(
    parent_model=mal2CounterfeitersDB,
    model=LanguageUrl,
    can_delete=True,
    form=LanguageUrlForm,
    formset=LanguageUrlInlineFormSet,
    min_num=2,
    extra=0,
)


################################################################################
# FAKE SHOP / COUNTERFEITERS FORM

class DBFormMixin(object):
    def __init__(self, website_id=None, *args, **kwargs):
        self.website = None
        self.website_id = website_id

        super().__init__(*args, **kwargs)

        self.fields["website"].widget = HiddenInput()

        if self.website_id:
            self.website = get_object_or_404(Website, pk=self.website_id)

            self.fields["url"].initial = self.website.url
            self.fields["url"].widget.attrs["readonly"] = True

    def clean_url(self):
        url = self.cleaned_data["url"]
        url.strip("/")

        url_to_check = remove_url_protocol(url)

        website = Website.objects.filter(
            Q(url="http://%s" % url_to_check)
            | Q(url="https://%s" % url_to_check)
        ).first()

        raise_error = False
        website_id = getattr(self, "website_id", None)

        if website_id:
            raise_error = False
        elif website and not self.instance.website:
            raise_error = True
        elif website and website.id != self.instance.website.id:
            raise_error = True

        if raise_error:
            raise exceptions.ValidationError(
                _("URL already exists in the database!"),
                code="invalid",
            )

        return url

    def save(self, commit=False):
        data = self.cleaned_data

        instance = super().save(commit=commit)

        if not self.website and not instance.website:
            self.website = Website.objects.create(
                url=data["url"],
                website_type_id=self.website_type_id,
                assigned_to_id=self.request.user.id,
            )

        if self.website:
            instance.website = self.website

        instance.save()

        # Update URL in website model
        website = instance.website
        website.url = instance.url
        website.save()

        take_screenshot(website)

        return instance


################################################################################
# FAKE SHOP FORM

class FakeShopForm(DBFormMixin, FieldsetModelForm):
    website_type_id = DB_FAKE_SHOP

    class Meta:
        model = mal2FakeShopDB
        fields = "__all__"

    @property
    def grid_data(self):
        return {
            "url": "col-12",

            "search_term": "col-12",
            "suspected_fraud_search": "col-12",

            "product_url": "col-12",
            "product_name": "col-12 col-md-6",
            "product_reason": "col-12 col-md-6",
            "price_comparison_geizhals_eu_url": "col-12 col-md-6",
            "price_comparison_reason": "col-12 col-md-6",
            "suspected_fraud_price_comparison": "col-12",

            "terms_of_payment_url": "col-12 col-md-6",
            "checkout_page_address_url": "col-12 col-md-6",
            "checkout_page_payment_method_url": "col-12 col-md-6",
            "payment_method_assessment": "col-12 col-md-6",
            "suspected_fraud_payment_method": "col-12",

            "is_fake": "col-12",

            "imprint": "col-12 col-md-6",
            "database_search_term": "col-12 col-md-6",
            "is_wko_checked": "col-12 col-md-6",
            "is_handelsregister_de_checked": "col-12 col-md-6",
            "is_justice_europe_checked": "col-12",
            "database_review_result": "col-12 col-md-6",
            "suspected_fraud_company_data": "col-12",

            "vat": "col-12 col-md-6",
            "vat_review_result": "col-12 col-md-6",
            "suspected_fraud_vat": "col-12",

            "domain_whois_url": "col-12",
            "domain_registration_check": "col-12",
            "domain_registration_contradiction_url": "col-12",
            "domain_registrar": "col-12",
            "suspected_fraud_domain": "col-12",
            "domain_is_fake": "col-12",

            "different_company_names": "col-12",

            "can_not_copy_website_images": "col-12",
            "copied_website_images": "col-12",
            "suspected_fraud_images": "col-12",

            "can_not_copy_website_text": "col-12",
            "checked_website_text_url": "col-12",
            "website_text_example": "col-12",
            "suspected_fraud_website_text": "col-12",

            "changing_languages_available": "col-12",

            "terms_and_conditions_of_contract_url": "col-12 col-md-6",
            "very_short_terms": "col-12 col-md-6",

            "suspected_fraud_quality_mark_seal": "col-12",
            "quality_mark_url": "col-12",
            "is_guetezeichen_at_checked": "col-12",
            "is_ehi_seal_checked": "col-12",
            "is_trusted_shops_checked": "col-12",
            "is_fictitious_quality_marks": "col-12",
            "fictitious_quality_mark_url": "col-12",

            "further_review_is_fake": "col-12",
        }

    @property
    def fieldsets_data(self):
        return [
            (None, {
                "fields": (
                    "url",
                    "website"
                ),
            }),
            (_("Search"), {
                "fields": (
                    "search_term",
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
                ),
            }),
            (_("Images"), {
                "fields": (
                    "can_not_copy_website_images",
                    "copied_website_images",
                    "suspected_fraud_images",
                ),
            }),
            (_("Text"), {
                "fields": (
                    "can_not_copy_website_text",
                    "checked_website_text_url",
                    "website_text_example",
                    "suspected_fraud_website_text",
                ),
            }),
            (_("Language"), {
                "fields": (
                    "changing_languages_available",
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
        ]


################################################################################
# COUNTERFEITERS FORM

class CounterfeiterForm(DBFormMixin, FieldsetModelForm):
    website_type_id = DB_COUNTERFEITE

    class Meta:
        model = mal2CounterfeitersDB
        fields = "__all__"

    @property
    def grid_data(self):
        return {
            "url": "col-12",
            "domain_is_plausible": "col-12 col-md-6",
            "has_discount": "col-12 col-md-6",
            "no_ssl": "col-12 col-md-6",
            "has_currency_selection": "col-12 col-md-6",
            "domain_is_counterfeiter": "col-12",
            "products_in_stock": "col-12 col-md-6",
            "no_product_description": "col-12 col-md-6",
            "contact_url": "col-12",
            "has_contact_mail": "col-12 col-md-6",
            "has_no_imprint": "col-12 col-md-6",
            "terms_and_conditions_of_contract_url": "col-12",
            "has_no_terms_and_conditions": "col-12 col-md-6",
            "imprint": "col-12",
            "imprint_is_counterfeiter": "col-12",
            "switching_language": "col-12 col-md-6",
            "language_is_counterfeiter": "col-12",
        }

    @property
    def fieldsets_data(self):
        return [
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
                    "language_is_counterfeiter",
                )
            })
        ]
