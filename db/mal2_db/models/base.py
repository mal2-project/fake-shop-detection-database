import os

from django.conf import settings
from django.core import validators
from django.db import models
from django.db.models import (
    F,
    Q,
)
from django.db.models.functions import (
    Coalesce,
)
from django.utils.translation import ugettext_lazy as _

from mal2.models import AuthTimeStampedModel
from mal2.utils import remove_url_protocol
from mal2_db.constants.db import (
    DB_COUNTERFEITE,
    DB_FAKE_SHOP,
    DB_NO_FAKE,
    DB_NO_VERIFICATION_NECESSARY,
    DB_UNSURE,
    WEBSITE_CATEGORY_ONLINE_SHOP,
    WEBSITE_CATEGORY_OTHER,
    WEBSITE_CATEGORY_UNKNOWN,
)
from mal2_db.models.registration import User


################################################################################
# WEBSITE

class WebsiteCategory(models.Model):
    category = models.CharField(
        max_length=255,
        verbose_name=_("Category"),
    )

    class Meta:
        ordering = ("-category",)
        verbose_name = _("Website category")
        verbose_name_plural = _("Website categories")

    def __str__(self):
        return str(self.category)


class WebsiteRiskScore(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
    )

    risk_score = models.CharField(
        max_length=50,
        verbose_name=_("Risk score"),
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = _("Website risk score")
        verbose_name_plural = _("Website risk scores")

    def __str__(self):
        return str(self.name)


class WebsiteReportedBy(models.Model):
    reporter = models.CharField(
        max_length=255,
        verbose_name=_("Reporter"),
    )

    class Meta:
        ordering = ("-reporter",)
        verbose_name = _("Website reported by")
        verbose_name_plural = _("Websites reported by")

    def __str__(self):
        return str(self.reporter)


class WebsiteType(models.Model):
    ordering_index = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ordering index")
    )

    type = models.CharField(
        max_length=255,
        verbose_name=_("Type"),
    )

    default_category = models.ForeignKey(
        WebsiteCategory,
        blank=False,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Website category"),
    )

    class Meta:
        ordering = ("ordering_index", "type_de",)
        verbose_name = _("Website type")
        verbose_name_plural = _("Website types")

    def __str__(self):
        return str(self.type)


class WebsiteQuerySet(models.QuerySet):
    def to_check(self):
        return self.exclude(
            Q(url__in=mal2FakeShopDB.objects.values_list("url"))
            | Q(url__in=mal2CounterfeitersDB.objects.values_list("url"))
        ).filter(
            Q(website_type_id__isnull=True)
            | Q(website_type_id=DB_FAKE_SHOP)
            | Q(website_type_id=DB_COUNTERFEITE)
        )

    def without_verification(self):
        return self.exclude(
            Q(url__in=mal2FakeShopDB.objects.values_list("url"))
            | Q(url__in=mal2CounterfeitersDB.objects.values_list("url"))
        ).filter(
            website_type_id=DB_NO_VERIFICATION_NECESSARY
        )

    def unsure(self):
        return self.exclude(
            Q(url__in=mal2FakeShopDB.objects.values_list("url"))
            | Q(url__in=mal2CounterfeitersDB.objects.values_list("url"))
        ).filter(
            website_type_id=DB_UNSURE
        )

    def disagreement(self):
        return self.exclude(
            Q(url__in=mal2FakeShopDB.objects.values_list("url"))
            | Q(url__in=mal2CounterfeitersDB.objects.values_list("url"))
        ).filter(
            ~Q(website_category=F("website_type__default_category"))
        )

    def is_fake_shop(self):
        return self.filter(
            url__in=mal2FakeShopDB.objects.values_list("url")
        )

    def is_brand_counterfeiter(self):
        return self.filter(
            url__in=mal2CounterfeitersDB.objects.values_list("url")
        )

    def is_no_fake(self):
        return self.exclude(
            Q(url__in=mal2FakeShopDB.objects.values_list("url"))
            | Q(url__in=mal2CounterfeitersDB.objects.values_list("url"))
        ).filter(
            website_type_id=DB_NO_FAKE
        )

    def is_other_sites(self):
        return self.exclude(
            Q(url__in=mal2FakeShopDB.objects.values_list("url"))
            | Q(url__in=mal2CounterfeitersDB.objects.values_list("url"))
        ).filter(
            website_category_id=WEBSITE_CATEGORY_OTHER,
        )

    def is_online_shop(self):
        return self.exclude(
            Q(url__in=mal2FakeShopDB.objects.values_list("url"))
            | Q(url__in=mal2CounterfeitersDB.objects.values_list("url"))
        ).filter(
            website_category_id=WEBSITE_CATEGORY_ONLINE_SHOP,
        )


class WebsiteManager(models.Manager):
    def get_queryset(self):
        return WebsiteQuerySet(self.model, using=self._db).annotate(
            db_id=Coalesce(
                F("mal2fakeshopdb__id"),
                F("mal2counterfeitersdb__id"),
            ),
        )


class Website(AuthTimeStampedModel):
    objects = WebsiteManager.from_queryset(WebsiteQuerySet)()

    url = models.CharField(
        help_text=_("Enter url of the reviewing website"),
        max_length=2000,
        null=True,
        validators=[
            validators.URLValidator(),
        ],
        verbose_name=_("URL"),
    )

    risk_score = models.ForeignKey(
        WebsiteRiskScore,
        blank=False,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Risk score"),
    )

    reported_by = models.ForeignKey(
        WebsiteReportedBy,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Reported by"),
    )

    assigned_to = models.ForeignKey(
        User,
        blank=False,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Assigned to"),
    )

    website_type = models.ForeignKey(
        WebsiteType,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Website type"),
    )

    screenshot = models.FilePathField(
        blank=True,
        null=True,
        path=settings.SCREENSHOTS_PATH,
    )

    website_category = models.ForeignKey(
        WebsiteCategory,
        default=WEBSITE_CATEGORY_UNKNOWN,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Website category"),
    )

    class Meta:
        verbose_name = _("Website")
        verbose_name_plural = _("Websites")

        permissions = [
            ("check_website", "Can check website")
        ]

    def __str__(self):
        return remove_url_protocol(self.url)

    def delete(self, *args, **kwargs):
        name = "%s.png" % self.id
        screenshot = os.path.join(settings.SCREENSHOTS_PATH, name)

        if os.path.exists(screenshot):
            os.remove(screenshot)

        return super().delete(*args, **kwargs)


################################################################################
# FAKESHOP DB

class mal2FakeShopDB(AuthTimeStampedModel):
    website = models.ForeignKey(
        Website,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    url = models.CharField(
        help_text=_("Enter url of the reviewing online shop"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("URL"),
    )

    is_fake = models.BooleanField(
        default=False,
        help_text=_("Do not tick if no or uncertain assessment.<br><strong>There are more checks necessary if not checked!</strong>"),
        verbose_name=_("Assessment: is certainly a fake shop?")
    )

    imprint = models.CharField(
        blank=True,
        help_text=_("Enter the URL of the imprint"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Imprint"),
    )

    # Search

    search_term = models.CharField(
        help_text=_("Entered search term on google.at"),
        max_length=2000,
        null=True,
        verbose_name=_("Search term"),
    )

    suspected_fraud_search = models.BooleanField(
        default=False,
        help_text=_("Do not tick if there is no or uncertain <strong>suspicion of fraud</strong>"),
        verbose_name=_("Suspected fraud (search)"),
    )

    # Price comparison

    product_name = models.CharField(
        help_text=_("Enter the name of the product"),
        max_length=2000,
        null=True,
        verbose_name=_("Name"),
    )

    product_url = models.CharField(
        blank=True,
        help_text=_("Enter the URL of the product page"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Product page"),
    )

    product_reason = models.CharField(
        blank=True,
        help_text=_("Reason of the product selection eg. offer, sale, ..."),
        max_length=2000,
        null=True,
        verbose_name=_("Reason of product selection"),
    )

    price_comparison_geizhals_eu_url = models.CharField(
        blank=True,
        help_text=_("Enter the URL of the geizhals.eu search"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Price comparison on geizhals.eu"),
    )

    price_comparison_reason = models.CharField(
        blank=True,
        help_text=_("Short explanation why the price is suspicious"),
        max_length=2000,
        null=True,
        verbose_name=_("Reason of suspected fraud"),
    )

    suspected_fraud_price_comparison = models.BooleanField(
        default=False,
        help_text=_("Do not tick if there is no or uncertain <strong>suspicion of fraud</strong>"),
        verbose_name=_("Suspected fraud (price comparison)"),
    )

    # Payment method

    terms_of_payment_url = models.CharField(
        blank=True,
        help_text=_("Enter the URL of the terms of payment"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Terms of payment"),
    )

    checkout_page_address_url = models.CharField(
        blank=True,
        help_text=_("Enter the URL of the checkout page"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Checkout page (address)"),
    )

    checkout_page_payment_method_url = models.CharField(
        blank=True,
        help_text=_("Enter the URL of the payment method selection"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Checkout page (payment method)"),
    )

    payment_method_assessment = models.CharField(
        blank=True,
        help_text=_("Enter assessment of payment method"),
        max_length=2000,
        null=True,
        verbose_name=_("Assessment of the payment method"),
    )

    suspected_fraud_payment_method = models.BooleanField(
        default=False,
        help_text=_("Do not tick if there is no or uncertain <strong>suspicion of fraud</strong>"),
        verbose_name=_("Suspected fraud (payment method)"),
    )

    # Database queries

    database_search_term = models.CharField(
        blank=True,
        help_text=_("Used search term in the databases"),
        max_length=2000,
        null=True,
        verbose_name=_("Search term"),
    )

    is_wko_checked = models.BooleanField(
        default=False,
        help_text="%s <a href=\"https://firmen.wko.at\" target=\"_blank\">firmen.wko.at</a>" % _("Database:"),
        verbose_name=_("WKO checked"),
    )

    is_handelsregister_de_checked = models.BooleanField(
        default=False,
        help_text="%s <a href=\"https://www.handelsregister.de/rp_web/search.do\" target=\"_blank\">www.handelsregister.de</a>" % _("Database:"),
        verbose_name=_("handelsregister.de checked"),
    )

    is_justice_europe_checked = models.BooleanField(
        default=False,
        help_text="%s <a href=\"https://e-justice.europa.eu/content_find_a_company-489-de.do?clang=de\" target=\"_blank\">e-justice.europa.eu</a>" % _("Database:"),
        verbose_name=_("justice.europa.eu checked"),
    )

    database_review_result = models.CharField(
        blank=True,
        help_text=_("Enter assessment for company inquiry"),
        max_length=2000,
        null=True,
        verbose_name=_("Result of the review"),
    )

    suspected_fraud_company_data = models.BooleanField(
        default=False,
        help_text=_("Do not tick if there is no or uncertain <strong>suspicion of fraud</strong>"),
        verbose_name=_("Suspected fraud (company data)"),
    )

    # UID

    vat = models.CharField(
        blank=True,
        help_text="%s <a href=\"https://ec.europa.eu/taxation_customs/vies/vatRequest.html\" target=\"_blank\">ec.europa.eu</a>" % _("Check VAT on"),
        max_length=2000,
        null=True,
        verbose_name=_("VAT"),
    )

    vat_review_result = models.CharField(
        blank=True,
        help_text=_("Enter assessment for VAT review"),
        max_length=2000,
        null=True,
        verbose_name=_("Result of the VAT review"),
    )

    suspected_fraud_vat = models.BooleanField(
        default=False,
        help_text=_("Do not tick if there is no or uncertain <strong>suspicion of fraud</strong>"),
        verbose_name=_("Suspected fraud (VAT)"),
    )

    # Domain

    domain_whois_url = models.CharField(
        blank=True,
        help_text="%s <a href=\"https://www.whois.com/whois\" target=\"_blank\">www.whois.com/whois</a>" % _("Enter URL of the domain query e.g."),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Domain WHOIS"),
    )

    domain_registration_check = models.BooleanField(
        default=False,
        verbose_name=_("Date of domain registration is less than a month"),
    )

    domain_registration_contradiction_url = models.CharField(
        blank=True,
        help_text=_("URL of the website if a founding date was specified that does not match the domain registration"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Contradiction with information on the website"),
    )

    domain_registrar = models.BooleanField(
        default=False,
        help_text=_("Check if the anonymization service / entry is not suitable for the imprint"),
        verbose_name=_("Domain registrar"),
    )

    suspected_fraud_domain = models.BooleanField(
        default=False,
        help_text=_("Do not tick if there is no or uncertain <strong>suspicion of fraud</strong>"),
        verbose_name=_("Suspected fraud (domain)"),
    )

    domain_is_fake = models.BooleanField(
        default=False,
        help_text=_("Do not tick if no or uncertain assessment.<br><strong>There are more checks necessary if not checked!</strong>"),
        verbose_name=_("Assessment: is certainly a fake shop?"),
    )

    # Company name

    different_company_names = models.BooleanField(
        default=False,
        help_text=_("If different company names exist, there is a suspicion of fraud"),
        verbose_name=_("Specify different company names"),
    )

    # Images

    can_not_copy_website_images = models.BooleanField(
        default=False,
        help_text=_("If not copyable then there is a suspicion of fraud"),
        verbose_name=_("Can not copy images on web page"),
    )

    copied_website_images = models.BooleanField(
        default=False,
        help_text="%s <a href=\"https://www.google.at/imghp?hl=detab\" target=\"_blank\">www.google.at/imghp</a>" % _("Apply reverse image search on:"),
        verbose_name=_("Image copied from other website"),
    )

    suspected_fraud_images = models.BooleanField(
        default=False,
        help_text=_("Do not tick if there is no or uncertain <strong>suspicion of fraud</strong>"),
        verbose_name=_("Suspected fraud (images)"),
    )

    # Text

    can_not_copy_website_text = models.BooleanField(
        default=False,
        help_text=_("If not copyable then there is a suspicion of fraud"),
        verbose_name=_("Can not copy text on web page"),
    )

    checked_website_text_url = models.CharField(
        blank=True,
        help_text=_("URL of the checked website text"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Website text"),
    )

    website_text_example = models.TextField(
        blank=True,
        max_length=2000,
        null=True,
        help_text="%s <a href=\"https://www.google.at\" target=\"_blank\">www.google.at</a>" % _("Enter text section and search on"),
        verbose_name=_("Text clipping"),
    )

    suspected_fraud_website_text = models.BooleanField(
        default=False,
        help_text=_("Do not tick if there is no or uncertain <strong>suspicion of fraud</strong>"),
        verbose_name=_("Suspected fraud (website text)"),
    )

    # Language

    changing_languages_available = models.BooleanField(
        default=False,
        help_text=_("If changing languages exist, there is a suspicion of fraud"),
        verbose_name=_("Changing languages available"),
    )

    # Terms and conditions of contract

    terms_and_conditions_of_contract_url = models.CharField(
        blank=True,
        help_text=_("URL to the terms and conditions"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Terms and conditions of contract"),
    )

    very_short_terms = models.BooleanField(
        default=False,
        help_text=_("If very short terms exist, there is a suspicion of fraud"),
        verbose_name=_("Very short terms"),
    )

    # Label/seal

    suspected_fraud_quality_mark_seal = models.BooleanField(
        default=False,
        help_text=_("Do not tick if there is no or uncertain <strong>suspicion of fraud</strong>"),
        verbose_name=_("Suspected fraud (quality mark)"),
    )

    quality_mark_url = models.CharField(
        blank=True,
        help_text=_("URL of the used quality mark"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Quality mark image"),
    )

    is_guetezeichen_at_checked = models.BooleanField(
        default=False,
        help_text="%s <a href=\"https://www.guetezeichen.at/zertifizierte-websites/guetezeichen/\" target=\"_blank\">www.guetezeichen.at</a>" % _("Database:"),
        verbose_name=_("guetezeichen.at checked"),
    )

    is_ehi_seal_checked = models.BooleanField(
        default=False,
        help_text="%s <a href=\"https://www.ehi-siegel.de/verbraucher/shops-mit-siegel/shops-zertifiziert/es/Shop///2\" target=\"_blank\">www.ehi-siegel.de</a>" % _("Database:"),
        verbose_name=_("EHI-seal checked"),
    )

    is_trusted_shops_checked = models.BooleanField(
        default=False,
        help_text="%s <a href=\"https://www.trustedshops.de\" target=\"_blank\">www.trustedshops.de</a>" % _("Database:"),
        verbose_name=_("Trusted shops checked"),
    )

    is_fictitious_quality_marks = models.BooleanField(
        default=False,
        help_text=_("If invented quality marks are available, there is a suspicion of fraud"),
        verbose_name=_("Fictitious quality marks available"),
    )

    fictitious_quality_mark_url = models.CharField(
        blank=True,
        help_text=_("URL of the used fictitious quality mark"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Fictitious quality mark"),
    )

    further_review_is_fake = models.BooleanField(
        default=False,
        help_text=_("Do not tick if no or uncertain assessment.<br><strong>There are more checks necessary if not checked!</strong>"),
        verbose_name=_("Assessment: is certainly a fake shop?"),
    )

    class Meta:
        verbose_name = _("Fake shop")
        verbose_name_plural = _("Fake shops")

    def __str__(self):
        return remove_url_protocol(self.url)


################################################################################
# BRAND COUNTERFEITER DB

class mal2CounterfeitersDB(AuthTimeStampedModel):
    website = models.ForeignKey(
        Website,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    url = models.CharField(
        help_text=_("Enter url of the reviewing online shop"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("URL"),
    )

    # Domain

    domain_is_plausible = models.BooleanField(
        default=False,
        help_text=_("Does the domain fit for the advertised products?"),
        verbose_name=_("Domainname plausible")
    )

    has_discount = models.BooleanField(
        default=False,
        help_text=_("Do all products have a discount?"),
        verbose_name=_("Discount")
    )

    no_ssl = models.BooleanField(
        default=False,
        help_text=_("Check if no https"),
        verbose_name=_("No SSL")
    )

    has_currency_selection = models.BooleanField(
        default=False,
        help_text=_("Is a wide variety of currency options offered?"),
        verbose_name=_("Currency selection")
    )

    domain_is_counterfeiter = models.BooleanField(
        default=False,
        help_text=_("Do not tick if no or uncertain assessment.<br><strong>There are more checks necessary if not checked!</strong>"),
        verbose_name=_("Domain assessment: is certainly a  brand counterfeiter?")
    )

    # Products

    products_in_stock = models.BooleanField(
        default=False,
        help_text=_("Are <strong> all </strong> in stock?"),
        verbose_name=_("Products in stock")
    )

    no_product_description = models.BooleanField(
        default=False,
        help_text=_("Only product title no description?"),
        verbose_name=_("No product description")
    )

    contact_url = models.CharField(
        blank=True,
        help_text=_("Url of the contact or term and conditions url"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Contact url"),
    )

    has_contact_mail = models.BooleanField(
        default=False,
        help_text=_("Mail address from an standard provider or no mail at all? (Gmail, Yahoo, hotmail etc."),
        verbose_name=_("Contact mail address"),
    )

    has_no_imprint = models.BooleanField(
        default=False,
        help_text=_("No imprint url only a contact form"),
        verbose_name=_("No imprint url")
    )

    terms_and_conditions_of_contract_url = models.CharField(
        blank=True,
        help_text=_("URL to the terms and conditions"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Terms and conditions of contract"),
    )

    has_no_terms_and_conditions = models.BooleanField(
        default=False,
        help_text=_("bad translation, foreign language, no terms and conditions content"),
        verbose_name=_("no terms and conditions")
    )

    imprint = models.CharField(
        blank=True,
        help_text=_("Enter the URL of the imprint"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("Imprint"),
    )

    imprint_is_counterfeiter = models.BooleanField(
        default=False,
        help_text=_("Do not tick if no or uncertain assessment.<br><strong>There are more checks necessary if not checked!</strong>"),
        verbose_name=_("Imprint assessment: is certainly a brand counterfeiter?")
    )

    switching_language = models.BooleanField(
        default=False,
        help_text=_("Language is changing between the sites of the homepage"),
        verbose_name=_("Switching language")
    )

    language_is_counterfeiter = models.BooleanField(
        default=False,
        help_text=_("Do not tick if no or uncertain assessment.<br><strong>There are more checks necessary if not checked!</strong>"),
        verbose_name=_("Imprint assessment: is certainly a brand counterfeiter?")
    )

    class Meta:
        verbose_name = _("Counterfeits DB")
        verbose_name_plural = _("Counterfeits DBS")

    def __str__(self):
        return remove_url_protocol(self.url)


################################################################################
# SEARCH RESULT

class SearchResult(models.Model):
    result_url = models.CharField(
        blank=True,
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("URL"),
    )

    mal2_db = models.ForeignKey(
        mal2FakeShopDB,
        on_delete=models.CASCADE,
        related_name="search_result",
    )

    class Meta:
        verbose_name = _("Search result")
        verbose_name_plural = _("Enter URLs for search results")

    def __str__(self):
        return str(self.result_url)


################################################################################
# COMPANY NAME

class CompanyName(models.Model):
    company_name_url = models.CharField(
        blank=True,
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("URL"),
    )

    mal2_db = models.ForeignKey(
        mal2FakeShopDB,
        on_delete=models.CASCADE,
        related_name="company_name",
    )

    class Meta:
        verbose_name = _("Company name")
        verbose_name_plural = _("Enter URLs for company names")

    def __str__(self):
        return str(self.company_name_url)


################################################################################
# WEBSITE IMAGE

class WebsiteImage(models.Model):
    image_url = models.CharField(
        blank=True,
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("URL"),
    )

    mal2_db = models.ForeignKey(
        mal2FakeShopDB,
        on_delete=models.CASCADE,
        related_name="website_image",
    )

    class Meta:
        verbose_name = _("Website image")
        verbose_name_plural = _("Enter URLs for website images")

    def __str__(self):
        return str(self.image_url)


################################################################################
# WEBSITE TEXT

class WebsiteText(models.Model):
    website_text_url = models.CharField(
        blank=True,
        help_text=_("URL of the checked text"),
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("URL"),
    )

    mal2_db = models.ForeignKey(
        mal2FakeShopDB,
        on_delete=models.CASCADE,
        related_name="website_text",
    )

    class Meta:
        verbose_name = _("Website text")
        verbose_name_plural = _("Enter URLs that have the same website text")

    def __str__(self):
        return str(self.website_text_url)


################################################################################
# LANGUAGE EXAMPLE

class LanguageExample(models.Model):
    language_example_url = models.CharField(
        blank=True,
        max_length=2000,
        null=True,
        validators=[validators.URLValidator()],
        verbose_name=_("URL"),
    )

    mal2_db = models.ForeignKey(
        mal2FakeShopDB,
        on_delete=models.CASCADE,
        related_name="language_example",
    )

    class Meta:
        verbose_name = _("Language example")
        verbose_name_plural = _("Enter URLs for language examples")

    def __str__(self):
        return str(self.language_example_url)


################################################################################
# PRODUCT EXAMPLE URL

class ProductExample(models.Model):
    product_example_url = models.CharField(
        blank=True,
        max_length=2000,
        null=True,
        verbose_name=_("URL"),
    )

    mal2_counterfeiter = models.ForeignKey(
        mal2CounterfeitersDB,
        on_delete=models.CASCADE,
        related_name="product_example",
    )

    class Meta:
        verbose_name = _("Product example")
        verbose_name_plural = _("Enter URLs for product examples")

    def __str__(self):
        return str(self.product_example_url)


################################################################################
# LANGUAGE URL

class LanguageUrl(models.Model):
    language_url = models.CharField(
        blank=True,
        max_length=2000,
        null=True,
        verbose_name=_("URL"),
    )

    mal2_counterfeiter = models.ForeignKey(
        mal2CounterfeitersDB,
        on_delete=models.CASCADE,
        related_name="language_url",
    )

    class Meta:
        verbose_name = _("Language url")
        verbose_name_plural = _("Enter URLs for language examples")

    def __str__(self):
        return str(self.language_url)
