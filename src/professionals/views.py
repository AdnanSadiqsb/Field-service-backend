from rest_framework import viewsets, status, mixins, filters
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import TradeCategory, ProfessionalProfile, ProfessionalCoverageArea, TradeSubCategory
from .serializers import (
    ProfessionalProfileListSerializer,
    TradeCategorySerializer,
    ProfessionalProfileSerializer,
    ProfessionalProfileCreateSerializer,
    ProfessionalCoverageAreaSerializer,
    ProfessionalProfileDetailSerializer,
)


class TradeCategoryViewSet(viewsets.ModelViewSet):
    queryset = TradeCategory.objects.filter(is_active=True).prefetch_related('subcategories')
    serializer_class = TradeCategorySerializer
    permission_classes = [AllowAny]
    swagger_tags = ['Trades']




class ProfessionalProfileViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin):
    queryset = ProfessionalProfile.objects.select_related('trade_category', 'user').prefetch_related(
        'trade_category__subcategories',
        'sub_categories',
        'coverage_areas',
    )
    serializer_class = ProfessionalProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'business_name',
        'first_name',
        'surname',
        'business_email',
        'business_phone',
        'mobile_phone',
        'postcode',
        'town_city',
        'county',
        'status',
        'user__username',
        'trade_category__name',
        'trade_category__slug',
        'sub_categories__name',
        'sub_categories__slug',
        'coverage_areas__postcode_district',
    ]
    filterset_fields = {
        'status': ['exact', 'in'],
        'trade_category': ['exact'],
        'sub_categories': ['exact'],
        'business_type': ['exact', 'in'],
        'number_of_employees': ['exact', 'in'],
        'town_city': ['exact', 'icontains'],
        'county': ['exact', 'icontains'],
        'coverage_areas__source': ['exact'],
        'coverage_areas__postcode_district': ['exact', 'icontains'],
        'created_at': ['exact', 'gte', 'lte'],
        'updated_at': ['exact', 'gte', 'lte'],
    }
    ordering_fields = [
        'business_name',
        'first_name',
        'surname',
        'business_email',
        'status',
        'business_type',
        'number_of_employees',
        'town_city',
        'county',
        'created_at',
        'updated_at',
    ]
    ordering = ['-created_at']
    swagger_tags = ['Professional']

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if self.action == 'list':
            queryset = queryset.distinct()
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return ProfessionalProfileCreateSerializer
        if self.action == 'professional_details':
            return ProfessionalProfileDetailSerializer
        if self.action in ['list', 'retrieve']:
            return ProfessionalProfileListSerializer
        return ProfessionalProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response(
            {
                'profile': ProfessionalProfileSerializer(profile, context={'request': request}).data,
                'tokens': profile.user.get_tokens(),
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        profile = get_object_or_404(ProfessionalProfile, user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='me')
    def update_me(self, request):
        profile = get_object_or_404(ProfessionalProfile, user=request.user)
        if profile.status == ProfessionalProfile.Status.APPROVED and not request.user.is_staff:
            return Response({'error': 'Cannot update approved profile'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='details')
    def professional_details(self, request, pk=None):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    # @action(detail=False, methods=['post'], url_path='me/submit')
    # def submit(self, request):
    #     profile = get_object_or_404(ProfessionalProfile, user=request.user)
    #     if profile.status != ProfessionalProfile.Status.DRAFT:
    #         return Response({'error': 'Profile must be in draft status to submit'}, status=status.HTTP_400_BAD_REQUEST)

    #     # Validation
    #     required_fields = ['business_email', 'business_phone', 'postcode', 'address_line_1', 'town_city']
    #     missing = [field for field in required_fields if not getattr(profile, field)]
    #     if missing:
    #         return Response({'error': f'Missing required fields: {", ".join(missing)}'}, status=status.HTTP_400_BAD_REQUEST)

    #     if profile.trade_category.requires_coverage_area and not profile.coverage_areas.exists():
    #         return Response({'error': 'Coverage area is required for this trade'}, status=status.HTTP_400_BAD_REQUEST)

    #     profile.status = ProfessionalProfile.Status.PENDING_REVIEW
    #     profile.save()
    #     serializer = self.get_serializer(profile)
    #     return Response(serializer.data)


class ProfessionalCoverageAreaViewSet(viewsets.ModelViewSet):
    queryset = ProfessionalCoverageArea.objects.all()  # For router basename
    serializer_class = ProfessionalCoverageAreaSerializer
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Professional']

    def get_queryset(self):
        return ProfessionalCoverageArea.objects.filter(professional__user=self.request.user)

    # def perform_create(self, serializer):
    #     profile = get_object_or_404(ProfessionalProfile, user=self.request.user)
    #     serializer.save(professional=profile)

    # @action(detail=False, methods=['get'], url_path='me/coverage')
    # def me_coverage(self, request):
    #     profile = get_object_or_404(ProfessionalProfile, user=request.user)
    #     areas = profile.coverage_areas.all()
    #     serializer = self.get_serializer(areas, many=True)
    #     return Response(serializer.data)

    # @action(detail=False, methods=['post'], url_path='me/coverage')
    # def create_me_coverage(self, request):
    #     profile = get_object_or_404(ProfessionalProfile, user=request.user)
    #     # Replace existing areas
    #     profile.coverage_areas.all().delete()
    #     data_list = request.data if isinstance(request.data, list) else [request.data]
    #     areas = []
    #     for data in data_list:
    #         serializer = self.get_serializer(data=data)
    #         serializer.is_valid(raise_exception=True)
    #         areas.append(serializer.save(professional=profile))
    #     serializer = self.get_serializer(areas, many=True)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
