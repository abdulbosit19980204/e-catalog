from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
    TokenVerifySerializer,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


@extend_schema(
    tags=['Authentication'],
    summary="JWT access va refresh token olish",
    description=(
        "Foydalanuvchi `username` va `password` ma'lumotlari asosida JWT token juftligini qaytaradi. "
        "Qaytgan `access` token'ni API so'rovlarida `Authorization: Bearer <access_token>` header'i orqali yuboring. "
        "`refresh` token esa keyinchalik yangi access token olish uchun ishlatiladi."
    ),
    request=TokenObtainPairSerializer,
    responses=TokenObtainPairSerializer,
    examples=[
        OpenApiExample(
            name="Curl misoli",
            value=(
                "curl -X POST http://localhost:8000/api/token/ "
                "-H \"Content-Type: application/json\" "
                "-d '{\"username\": \"admin\", \"password\": \"secret\"}'"
            ),
        )
    ],
)
class APITokenObtainPairView(TokenObtainPairView):
    """JWT access va refresh token juftligini olish."""


@extend_schema(
    tags=['Authentication'],
    summary="Refresh token orqali yangi access token olish",
    description=(
        "Oldin olingan refresh token'ni yuborib yangi access token yarating. "
        "Agar `ROTATE_REFRESH_TOKENS=True` bo'lsa, javobda yangi refresh ham qaytadi."
    ),
    request=TokenRefreshSerializer,
    responses=TokenRefreshSerializer,
    examples=[
        OpenApiExample(
            name="HTTPie misoli",
            value="http POST http://localhost:8000/api/token/refresh/ refresh=<refresh_token>",
        )
    ],
)
class APITokenRefreshView(TokenRefreshView):
    """Yangi access token yaratish."""


@extend_schema(
    tags=['Authentication'],
    summary="Access yoki refresh tokenni tekshirish",
    description="JWT tokenning haqiqiyligini tekshiradi. Token noto'g'ri bo'lsa 401 qaytaradi.",
    request=TokenVerifySerializer,
    responses={200: TokenVerifySerializer},
)
class APITokenVerifyView(TokenVerifyView):
    """JWT tokenni tekshirish."""

