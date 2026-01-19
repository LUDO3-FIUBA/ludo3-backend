import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from backend.serializers.google_auth_serializer import (
    GoogleSignInSerializer, 
    GoogleRegistrationSerializer
)
from backend.services.google_auth_service import GoogleAuthService

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_sign_in(request):
    serializer = GoogleSignInSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    id_token = serializer.validated_data['id_token']
    service = GoogleAuthService()
    
    try:
        result = service.authenticate(id_token)
        user = result['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error during Google sign-in: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_complete_registration(request):
    serializer = GoogleRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    service = GoogleAuthService()
    
    try:
        user = service.complete_registration(
            sub=serializer.validated_data['sub'],
            email=serializer.validated_data['email'],
            dni=serializer.validated_data['dni'],
            padron=serializer.validated_data.get('padron'),
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', ''),
            is_student=serializer.validated_data.get('is_student', True),
            is_teacher=serializer.validated_data.get('is_teacher', False)
        )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error during Google registration: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)