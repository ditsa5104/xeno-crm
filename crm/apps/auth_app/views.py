from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers as drf_serializers
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


_AuthOk = inline_serializer(
    name='AuthTokenResponse',
    fields={
        'token': drf_serializers.CharField(),
        'user': UserSerializer(),
    },
)


@extend_schema(tags=['auth'])
class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Register a new user',
        description='Creates a new user and returns an auth token plus the user record.',
        request=RegisterSerializer,
        responses={201: _AuthOk},
    )
    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=201)


@extend_schema(tags=['auth'])
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Sign in',
        description='Authenticate with username (or email) and password. Returns an auth token.',
        request=LoginSerializer,
        responses={200: _AuthOk},
    )
    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})


@extend_schema(tags=['auth'])
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Sign out',
        description='Invalidates all auth tokens for the current user.',
        request=None,
        responses={200: OpenApiResponse(description='Logged out')},
    )
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'status': 'ok'})


@extend_schema(tags=['auth'])
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Current user',
        description='Returns the authenticated user.',
        responses={200: UserSerializer},
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)
