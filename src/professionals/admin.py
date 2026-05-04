from django.contrib import admin
from .models import TradeCategory, TradeSubCategory, ProfessionalProfile, ProfessionalCoverageArea


@admin.register(TradeCategory)
class TradeCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'sort_order', 'requires_coverage_area']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug']


@admin.register(TradeSubCategory)
class TradeSubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'trade_category', 'slug', 'is_active', 'sort_order']
    list_filter = ['trade_category', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'slug']


@admin.register(ProfessionalProfile)
class ProfessionalProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'trade_category', 'status', 'created_at']
    list_filter = ['status', 'trade_category', 'business_type']
    search_fields = ['business_name', 'user__username', 'business_email']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ProfessionalCoverageArea)
class ProfessionalCoverageAreaAdmin(admin.ModelAdmin):
    list_display = ['professional', 'postcode_district', 'source', 'radius_miles']
    list_filter = ['source']
    search_fields = ['professional__business_name', 'postcode_district']