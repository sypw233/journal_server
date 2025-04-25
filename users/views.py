from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User
from .serializers import UserSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors,
                'code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Register error: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({
                'error': 'Internal server error',
                'details': str(e),
                'trace': traceback.format_exc(),
                'code': 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            if not username or not password:
                return Response({
                    'error': 'Missing credentials',
                    'code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({
                'error': 'Invalid credentials',
                'code': 401
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Register error: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({
                'error': 'Internal server error',
                'details': str(e),
                'trace': traceback.format_exc(),
                'code': 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        try:
            user = request.user
            old_password = request.data.get('old_password')
            new_password = request.data.get('new_password')
            if not old_password or not new_password:
                return Response({
                    'error': 'Missing password fields',
                    'code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
            if not user.check_password(old_password):
                return Response({
                    'error': 'Wrong password',
                    'code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            return Response({
                'message': 'Password updated successfully',
                'code': 200
            }, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Register error: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({
                'error': 'Internal server error',
                'details': str(e),
                'trace': traceback.format_exc(),
                'code': 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Register error: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({
                'error': 'Internal server error',
                'details': str(e),
                'trace': traceback.format_exc(),
                'code': 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)