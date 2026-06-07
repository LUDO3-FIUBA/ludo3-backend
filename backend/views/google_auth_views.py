import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from backend.api_exceptions import ValidationError
from backend.serializers.google_auth_serializer import (
    GoogleSignInSerializer,
    GoogleRegistrationSerializer
)
from backend.services.google_auth_service import GoogleAuthService
from .cookie_auth_views import make_token_response

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
        
        if result['status'] == 'existing_user':
            user = result['user']
            refresh = RefreshToken.for_user(user)
            return make_token_response(request, refresh_instance=refresh)
        
        elif result['status'] == 'needs_registration':
            return Response({
                'data': result['google_data']
            }, status=status.HTTP_409_CONFLICT)
    
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
            password=serializer.validated_data['password'],
            padron=serializer.validated_data.get('padron'),
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', ''),
            is_student=serializer.validated_data.get('is_student', True),
            is_teacher=serializer.validated_data.get('is_teacher', False)
        )
        
        refresh = RefreshToken.for_user(user)
        response = make_token_response(request, refresh_instance=refresh)
        response.status_code = status.HTTP_201_CREATED
        return response
    
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error during Google registration: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)