from django.core import validators as django_validators
from rest_framework import serializers

from mal2.utils import take_screenshot
from mal2_db import models
from mal2_db.models import WebsiteCategory
from mal2_rest import validators


################################################################################
# WEBSITE RISK SCORE

class WebsiteRiskScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WebsiteRiskScore
        fields = "__all__"


################################################################################
# WEBSITE REPORTER

class WebsiteReporterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WebsiteReportedBy
        fields = "__all__"


################################################################################
# WEBSITE TYPE

class WebsiteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WebsiteType
        fields = "__all__"


################################################################################
# WEBSITE

class WebsiteSerializer(serializers.ModelSerializer):
    db_id = serializers.IntegerField(
        required=False,
    )

    url = serializers.CharField(
        max_length=2000,
        validators=[
            django_validators.URLValidator(),
            validators.DuplicateURLValidator(),
        ],
    )

    class Meta:
        model = models.Website

        exclude = [
            "assigned_to",
            "modified_by",
        ]

        read_only_fields = [
            "website_type",
            "screenshot",
            "website_category",
        ]

        extra_kwargs = {
            "risk_score": {
                "required": True,
            },
            "reported_by": {
                "required": True,
            },
        }

    def create(self, validated_data):
        website = super().create(validated_data)
        take_screenshot(website)

        return website


################################################################################
# FAKE SHOP DB

class FakeShopDBSerializer(serializers.ModelSerializer):
    company_name = serializers.StringRelatedField(many=True)
    language_example = serializers.StringRelatedField(many=True)
    website_image = serializers.StringRelatedField(many=True)
    website_text = serializers.StringRelatedField(many=True)
    search_result = serializers.StringRelatedField(many=True)

    class Meta:
        model = models.mal2FakeShopDB
        fields = "__all__"


################################################################################
# BRAND COUNTERFEITER SHOP DB

class BrandCounterfeiterDBSerializer(serializers.ModelSerializer):
    language_url = serializers.StringRelatedField(many=True)
    product_example = serializers.StringRelatedField(many=True)

    class Meta:
        model = models.mal2CounterfeitersDB
        fields = "__all__"
