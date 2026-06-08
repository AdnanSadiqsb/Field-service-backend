from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import TradeCategory, TradeSubCategory, ProfessionalProfile, ProfessionalCoverageArea
from src.notifications.services import notify, ACTIVITY_PROFESSIONAL_SIGNUP

User = get_user_model()


class TradeSubCategorySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = TradeSubCategory
        fields = ['id', 'name', 'slug', 'description', 'sort_order']
        extra_kwargs = {'slug': {'required': False}}


class TradeCategorySerializer(serializers.ModelSerializer):
    subcategories = TradeSubCategorySerializer(many=True, required=False)

    class Meta:
        model = TradeCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'is_active', 'sort_order', 'requires_coverage_area', 'subcategories']
        extra_kwargs = {'slug': {'required': False}}

    @transaction.atomic
    def create(self, validated_data):
        subcategories = validated_data.pop('subcategories', [])
        print(f"Creating TradeCategory with data: {validated_data} and subcategories: {subcategories}")  # Debug print
        if 'slug' not in validated_data:
            from django.utils.text import slugify
            validated_data['slug'] = slugify(validated_data['name'])

        print("Creating TradeCategory with validated data: ", validated_data)  # Debug print
        category = TradeCategory.objects.create(**validated_data)
        print(f"Created TradeCategory with ID: {category.id}")  # Debug print
        self._upsert_subcategories(category, subcategories)
        return category

    @transaction.atomic
    def update(self, instance, validated_data):
        subcategories = validated_data.pop('subcategories', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if subcategories is not None:
            self._upsert_subcategories(instance, subcategories)
        return instance

    def _upsert_subcategories(self, category, subcategories):
        from django.utils.text import slugify

        print(f"Upserting subcategories for category {category.name} with data: {subcategories}")  # Debug print
        for item in subcategories:
            sub_id = item.pop('id', None)
            if 'slug' not in item or not item['slug']:
                item['slug'] = slugify(item['name'])

            print(f"Upserting subcategory with data: {item}")  # Debug print
            if sub_id:
                TradeSubCategory.objects.filter(id=sub_id, trade_category=category).update(**item)
            else:
                TradeSubCategory.objects.get_or_create(slug=item['slug'], trade_category=category, defaults=item)



class TradeCategoryShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = TradeCategory
        fields = ['id', 'name', 'slug', 'description', 'icon']


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
        # notify(
        #     ACTIVITY_PROFESSIONAL_SIGNUP,
        #     context={
        #         'first_name': first_name,
        #         'business_name': profile.business_name,
        #         'trade': profile.trade_category.name,
        #     },
        #     email_to=[email],
        # )
        return profile


class ProfessionalProfileSerializer(serializers.ModelSerializer):


    class Meta:
        model = ProfessionalProfile
        fields = ['id', 'trade_category', 'business_name', 'business_type', 'number_of_employees', 'first_name', 'surname', 'business_email', 'business_phone', 'mobile_phone', 'postcode', 'address_line_1', 'address_line_2', 'town_city', 'county', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


class ProfessionalCoverageAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalCoverageArea
        fields = ['id', 'base_postcode', 'radius_miles', 'postcode_district', 'source', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProfessionalProfileDetailSerializer(serializers.ModelSerializer):
    trade_category_info = TradeCategorySerializer(read_only=True, source='trade_category')
    # sub_categories_info = TradeSubCategorySerializer(read_only=True, many=True, source='sub_categories')
    coverage_areas_info = ProfessionalCoverageAreaSerializer(read_only=True, many=True, source='coverage_areas')

    class Meta:
        model = ProfessionalProfile
        fields = [
            'id',
            'trade_category',
            'trade_category_info',
            'sub_categories',
           
            'coverage_areas_info',
            'business_name',
            'business_type',
            'number_of_employees',
            'first_name',
            'surname',
            'business_email',
            'business_phone',
            'mobile_phone',
            'postcode',
            'address_line_1',
            'address_line_2',
            'town_city',
            'county',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class ProfessionalProfileListSerializer(serializers.ModelSerializer):
    trade_category_info = TradeCategoryShortSerializer(read_only=True, source='trade_category')

    class Meta:
        model = ProfessionalProfile
        fields = '__all__'
    # trade_category = TradeCategorySerializer(read_only=True)
    # sub_categories = TradeSubCategorySerializer(many=True, read_only=True)
    # user = serializers.UUIDField(read_only=True)
    # id = serializers.UUIDField(read_only=True)
