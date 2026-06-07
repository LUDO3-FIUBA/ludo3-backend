from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

COOKIE_NAME = 'refresh_token'
COOKIE_PATH = '/auth'
COOKIE_MAX_AGE = 60 * 60 * 24 * 14  # 14 days


def is_web_client(request):
    return request.headers.get('X-Client') == 'web'


def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        COOKIE_NAME,
        refresh_token,
        max_age=COOKIE_MAX_AGE,
        path=COOKIE_PATH,
        httponly=True,
        samesite='Lax',
        secure=not settings.DEBUG,
    )
    return response


def make_token_response(request, user=None, refresh_instance=None):
    """Build a login/register response: cookie for web, full JSON for native."""
    if refresh_instance is None:
        refresh_instance = RefreshToken.for_user(user)

    access = str(refresh_instance.access_token)
    refresh_str = str(refresh_instance)

    if is_web_client(request):
        response = Response({'access': access}, status=status.HTTP_200_OK)
        set_refresh_cookie(response, refresh_str)
    else:
        response = Response({'access': access, 'refresh': refresh_str}, status=status.HTTP_200_OK)

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def jwt_refresh(request):
    if is_web_client(request):
        refresh_token = request.COOKIES.get(COOKIE_NAME)
        if not refresh_token:
            return Response({'detail': 'No refresh token cookie.'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        access = str(token.access_token)
        token.set_jti()
        token.set_exp()
        new_refresh = str(token)
    except TokenError as e:
        return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    if is_web_client(request):
        response = Response({'access': access})
        set_refresh_cookie(response, new_refresh)
    else:
        response = Response({'access': access, 'refresh': new_refresh})

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def jwt_logout(request):
    response = Response({'detail': 'Logged out.'}, status=status.HTTP_200_OK)
    response.delete_cookie(COOKIE_NAME, path=COOKIE_PATH)
    return response
