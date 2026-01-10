from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    filterset_fields = ['is_staff', 'is_active']

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, inline_serializer
from rest_framework import serializers
from .services import OneCAuthService

class OneCLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary="1C orqali login qilish",
        description="Client 1C credentials (login, password) va project_code orqali autentifikatsiya qiladi.",
        request=inline_serializer(
            name='OneCLoginRequest',
            fields={
                'login': serializers.CharField(required=True, help_text="1C Login (username)"),
                'password': serializers.CharField(required=True, help_text="1C Parol"),
                'project_name': serializers.CharField(required=True, help_text="Auth Project Nomi (masalan: Evyap)"),
            }
        ),
        responses={
            200: OpenApiResponse(
                description="Muvaffaqiyatli login va tokenlar",
                response=inline_serializer(
                    name='OneCLoginResponse',
                    fields={
                        'user': serializers.DictField(),
                        'tokens': serializers.DictField(),
                        'message': serializers.CharField(),
                    }
                )
            ),
            400: OpenApiResponse(description="Noto'g'ri ma'lumotlar"),
            401: OpenApiResponse(description="Login yoki parol xato"),
            404: OpenApiResponse(description="Project topilmadi"),
            500: OpenApiResponse(description="1C Service xatosi"),
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        login = serializer.validated_data['login']
        password = serializer.validated_data['password']
        project_name = serializer.validated_data['project_name']

        result, error = OneCAuthService.authenticate(project_name, login, password)

        if error:
            # Determine status code based on error
            if "Project not found" in error:
                status_code = status.HTTP_404_NOT_FOUND
            elif "Service Error" in error:
                status_code = status.HTTP_502_BAD_GATEWAY
            elif "Connection Error" in error:
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            else:
                status_code = status.HTTP_401_UNAUTHORIZED
                
            return Response({'error': error}, status=status_code)

        return Response(result, status=status.HTTP_200_OK)


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    project_name = serializers.CharField(required=True)
