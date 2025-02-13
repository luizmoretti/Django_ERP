from django.shortcuts import render
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    post=extend_schema(
        tags=["JWT - Auth"],
        summary="Obtain the JWT access and refresh tokens",
    )
)
class DecoratedTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema_view(
    post=extend_schema(
        tags=["JWT - Auth"],
        summary="Refresh the JWT access token",
        description="Refresh the JWT access token",
    )
)
class DecoratedTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(
    tags=["JWT - Auth"],
    summary="Verify the JWT access token",
    description="Verify the JWT access token",
)
class DecoratedTokenVerifyView(TokenVerifyView):
    pass
