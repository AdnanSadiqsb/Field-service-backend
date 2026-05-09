from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TradeCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True, default='')
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    requires_coverage_area = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = _('Trade Category')
        verbose_name_plural = _('Trade Categories')

    def __str__(self):
        return self.name


class TradeSubCategory(BaseModel):
    trade_category = models.ForeignKey(TradeCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        unique_together = ['trade_category', 'slug']
        verbose_name = _('Trade Subcategory')
        verbose_name_plural = _('Trade Subcategories')

    def __str__(self):
        return f"{self.trade_category.name} - {self.name}"


class ProfessionalProfile(BaseModel):
    class BusinessType(models.TextChoices):
        SELF_EMPLOYED = 'SELF_EMPLOYED', _('Self Employed')
        LIMITED_COMPANY = 'LIMITED_COMPANY', _('Limited Company')
        STARTING_BUSINESS = 'STARTING_BUSINESS', _('Starting Business')

    class NumberOfEmployees(models.TextChoices):
        ONE = 'ONE', _('1')
        TWO_TO_FIVE = 'TWO_TO_FIVE', _('2-5')
        SIX_TO_NINE = 'SIX_TO_NINE', _('6-9')
        TEN_PLUS = 'TEN_PLUS', _('10+')

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PENDING_REVIEW = 'PENDING_REVIEW', _('Pending Review')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='professional_profile')
    trade_category = models.ForeignKey(TradeCategory, on_delete=models.CASCADE)
    sub_categories = models.ManyToManyField(TradeSubCategory, blank=True, related_name='professionals')
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=20, choices=BusinessType.choices)
    number_of_employees = models.CharField(max_length=20, choices=NumberOfEmployees.choices)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    business_email = models.EmailField()
    business_phone = models.CharField(max_length=20)
    mobile_phone = models.CharField(max_length=20, blank=True)
    postcode = models.CharField(max_length=10)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    town_city = models.CharField(max_length=100)
    county = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        verbose_name = _('Professional Profile')
        verbose_name_plural = _('Professional Profiles')

    def __str__(self):
        return f"{self.business_name} - {self.user.username}"


class ProfessionalCoverageArea(BaseModel):
    class Source(models.TextChoices):
        RADIUS = 'RADIUS', _('Radius')
        MANUAL = 'MANUAL', _('Manual')

    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name='coverage_areas')
    base_postcode = models.CharField(max_length=10, blank=True)
    radius_miles = models.PositiveIntegerField(null=True, blank=True)
    postcode_district = models.CharField(max_length=10)
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.MANUAL)

    class Meta:
        unique_together = ['professional', 'postcode_district']
        verbose_name = _('Professional Coverage Area')
        verbose_name_plural = _('Professional Coverage Areas')

    def __str__(self):
        return f"{self.professional.business_name} - {self.postcode_district}"