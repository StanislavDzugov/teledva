from django.contrib.auth.models import update_last_login
from django.db.models import Q
from rest_framework import generics, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from .models import CustomUser
from .serializers import CreateUserSerializer, UserSerializer, UpdatePasswordSerializer


class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class RegisterUserApiView(views.APIView):

    permission_classes = (IsAuthenticated, IsAdminUser)

    def post(self, request, *args, **kwargs):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UpdatePasswordView(views.APIView):

    def post(self, request, *args, **kwargs):
        serializer = UpdatePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'ok': 'ok'})


class LoginView(views.APIView):
    """
    POST Вход пользователя в систему
        @username_or_email
        @password
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    @staticmethod
    def authenticate(email, password):
        """Authenticate user by username_or_email/passwords and return User if okay and None if not okay."""
        user = CustomUser.objects.filter(
            Q(email__iexact=email) | Q(username__iexact=email)
        ).first()
        if user and user.check_password(password):
            return user
        return

    def post(self, request):
        username_or_email = request.data.get('username_or_email')
        password = request.data.get('password')

        if username_or_email is None or password is None:
            return Response(
                {'error': 'username_or_email-and-password-required'}, status=HTTP_400_BAD_REQUEST
            )

        user = self.authenticate(username_or_email, password)

        if not user:
            return Response({'error': 'invalid-credentials'})

        token, _ = Token.objects.get_or_create(user=user)
        update_last_login(None, user)

        return Response(
            {
                'token': token.key,
                'employee': UserSerializer(user).data,
            }
        )


class LogoutView(views.APIView):
    """
    POST    Выход пользователя из системы.
    """

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=HTTP_200_OK)
