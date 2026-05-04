from rest_framework import serializers
from .models import TradeCategory, TradeSubCategory, ProfessionalProfile, ProfessionalCoverageArea


class TradeSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeSubCategory
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'sort_order']


class TradeCategorySerializer(serializers.ModelSerializer):
    subcategories = TradeSubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = TradeCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'is_active', 'sort_order', 'requires_coverage_area', 'subcategories']


class ProfessionalProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalProfile
        fields = ['trade_category', 'business_name', 'business_type', 'number_of_employees', 'first_name', 'surname', 'business_email', 'business_phone', 'mobile_phone', 'postcode', 'address_line_1', 'address_line_2', 'town_city', 'county']


class ProfessionalProfileSerializer(serializers.ModelSerializer):
    trade_category = TradeCategorySerializer(read_only=True)
    sub_categories = TradeSubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = ProfessionalProfile
        fields = ['id', 'user', 'trade_category', 'sub_categories', 'business_name', 'business_type', 'number_of_employees', 'first_name', 'surname', 'business_email', 'business_phone', 'mobile_phone', 'postcode', 'address_line_1', 'address_line_2', 'town_city', 'county', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']


class ProfessionalCoverageAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalCoverageArea
        fields = ['id', 'base_postcode', 'radius_miles', 'postcode_district', 'source', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']