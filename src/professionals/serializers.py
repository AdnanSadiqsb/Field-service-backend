from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import TradeCategory, TradeSubCategory, ProfessionalProfile, ProfessionalCoverageArea
from src.notifications.services import notify, ACTIVITY_PROFESSIONAL_SIGNUP

User = get_user_model()


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

    def validate_business_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        first_name = validated_data['first_name']
        surname = validated_data['surname']
        email = validated_data['business_email']

        username = email.split('@')[0]
        base_username = username
        counter = 1
        random_password = User.objects.make_random_password()
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=surname,
            password=random_password,
            role = 'professional',

        )
        profile = ProfessionalProfile.objects.create(user=user, **validated_data)
        print(f'Created user {user.username} with email {email}')  # Debug print
        notify(
            ACTIVITY_PROFESSIONAL_SIGNUP,
            context={
                'first_name': first_name,
                'business_name': profile.business_name,
                'trade': profile.trade_category.name,
            },
            email_to=[email],
        )
        return profile


class ProfessionalProfileSerializer(serializers.ModelSerializer):
    trade_category = TradeCategorySerializer(read_only=True)
    sub_categories = TradeSubCategorySerializer(many=True, read_only=True)
    user = serializers.UUIDField(read_only=True)
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = ProfessionalProfile
        fields = ['id', 'user', 'trade_category', 'sub_categories', 'business_name', 'business_type', 'number_of_employees', 'first_name', 'surname', 'business_email', 'business_phone', 'mobile_phone', 'postcode', 'address_line_1', 'address_line_2', 'town_city', 'county', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']


class ProfessionalCoverageAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalCoverageArea
        fields = ['id', 'base_postcode', 'radius_miles', 'postcode_district', 'source', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']