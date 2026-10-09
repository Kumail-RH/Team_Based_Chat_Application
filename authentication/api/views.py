from bson.errors import InvalidId
from django.contrib.auth.hashers import check_password, make_password
from pymongo.errors import DuplicateKeyError
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers import LoginSerializer, RegisterSerializer
from authentication.repositories import user_repository
from authentication.services.token_service import create_access_token


def user_response(user: dict) -> dict:
    """Return only public user fields."""
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "is_active": user["is_active"],
        "email_verified": bool(user.get("email_verified_at")),
        "created_at": user["created_at"].isoformat(),
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            user = user_repository.create_user(
                name=data["name"],
                email=data["email"],
                password_hash=make_password(data["password"]),
            )
        except DuplicateKeyError:
            return Response(
                {"email": ["An account with this email already exists."]},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {
                "message": "Account created successfully.",
                "user": user_response(user),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = user_repository.find_user_by_email(data["email"])

        if not user or not check_password(
            data["password"],
            user["password_hash"],
        ):
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.get("is_active", False):
            return Response(
                {"detail": "This account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )

        raw_token = create_access_token(user["_id"])
        return Response(
            {
                "message": "Login successful.",
                "token_type": "Token",
                "access_token": raw_token,
                "expiry_in": 7 * 24 * 60 * 60,
                "user": user_response(user),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from authentication.repositories.token_repository import revoke_token

        revoke_token(request.auth["_id"])

        return Response(
            {"message": "Logout successful."},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = user_repository.find_user_by_id(request.user.id)
        except (InvalidId, TypeError):
            user = None

        if not user:
            return Response(
                {"user": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"user": user_response(user)},
            status=status.HTTP_200_OK,
        )