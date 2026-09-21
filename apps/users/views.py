from django.contrib.auth.models import Group
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegisterSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, inline_serializer


class UserViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    # без этого swagger не видит эндпоинты
    serializer_class = UserSerializer

    @extend_schema(request=RegisterSerializer, responses={201: UserSerializer})
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=inline_serializer('LogoutRequest', {'refresh': serializers.CharField()}),
        responses={205: None, 400: None},
    )
    @action(detail=False, methods=['post'], url_path='logout', permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get', 'patch'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method == 'GET':
            return Response(UserSerializer(request.user).data)

        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(request=None, responses={200: UserSerializer})
    @action(detail=False, methods=['post'], url_path='become-landlord', permission_classes=[IsAuthenticated])
    def become_landlord(self, request):
        # из Tenants не убираем, можно быть в обеих группах
        if request.user.groups.filter(name='Landlords').exists():
            return Response({'detail': 'Вы уже арендодатель.'}, status=status.HTTP_400_BAD_REQUEST)

        landlord_group, _ = Group.objects.get_or_create(name='Landlords')
        request.user.groups.add(landlord_group)
        return Response(UserSerializer(request.user).data)
