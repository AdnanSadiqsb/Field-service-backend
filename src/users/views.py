from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from src.users.models import User
from src.users.permissions import IsUserOrReadOnly
from src.users.serializers import CreateUserSerializer, UserSerializer, LoginSerializer


class UserViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Creates, Updates and Retrieves - User Accounts
    """

    queryset = User.objects.all()
    serializers = {'default': UserSerializer, 'create': CreateUserSerializer}
    permissions = {'default': (IsUserOrReadOnly,), 'create': (AllowAny,)}
    swagger_tags = ['Users']

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['default'])

    def get_permissions(self):
        self.permission_classes = self.permissions.get(self.action, self.permissions['default'])
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='me', url_name='me')
    def get_user_data(self, instance):
        try:
            return Response(UserSerializer(self.request.user, context={'request': self.request}).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Wrong auth token' + e}, status=status.HTTP_400_BAD_REQUEST)


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    swagger_tags = ['Auth']

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        professional = None
        if hasattr(user, 'professional_profile'):
            from src.professionals.serializers import ProfessionalProfileSerializer
            professional = ProfessionalProfileSerializer(user.professional_profile).data

        return Response({
            'tokens': user.get_tokens(),
            'user': UserSerializer(user, context={'request': request}).data,
            'professional': professional,
        }, status=status.HTTP_200_OK)
