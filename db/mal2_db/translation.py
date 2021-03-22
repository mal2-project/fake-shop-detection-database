from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from modeltranslation.translator import (
    TranslationOptions,
    register,
)

from mal2_db.models import (
    WebsiteCategory,
    WebsiteReportedBy,
    WebsiteRiskScore,
    WebsiteType,
)


################################################################################
# WEBSITE RISK SCORE

@register(WebsiteRiskScore)
class WebsiteRiskScoreTranslationOptions(TranslationOptions):
    fields = ("name",)
    required_languages = ("en-GB", "de",)


@admin.register(WebsiteRiskScore)
class WebsiteRiskScoreAdmin(TranslationAdmin):
    list_display = ("name",)


################################################################################
# WEBSITE REPORTED BY

@register(WebsiteReportedBy)
class WebsiteReportedByTranslationOptions(TranslationOptions):
    fields = ("reporter",)
    required_languages = ("en-GB", "de",)


@admin.register(WebsiteReportedBy)
class WebsiteReportedByAdmin(TranslationAdmin):
    list_display = ("reporter",)


################################################################################
# WEBSITE REPORTED BY

@register(WebsiteType)
class WebsiteTypeTranslationOptions(TranslationOptions):
    fields = ("type",)
    required_languages = ("en-GB", "de",)


@admin.register(WebsiteType)
class WebsiteTypeAdmin(TranslationAdmin):
    list_display = ("type", "default_category", "ordering_index",)
    ordering = ("ordering_index", "type_de",)


################################################################################
# WEBSITE CATEGORY

@register(WebsiteCategory)
class WebsiteCategoryTranlationOptions(TranslationOptions):
    fields = ("category",)
    required_languages = ("en-GB", "de",)


@admin.register(WebsiteCategory)
class WebsiteCategoryAdmin(TranslationAdmin):
    list_display = ("category",)
