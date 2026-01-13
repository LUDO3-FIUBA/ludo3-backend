import os
import logging
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class GoogleAuthClient:
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")

    def verify_token(self, token):
        if not self.GOOGLE_CLIENT_ID:
            raise ValueError("GOOGLE_CLIENT_ID not configured")
        
        try:
            claims = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                self.GOOGLE_CLIENT_ID
            )
            return claims
        except ValueError as e:
            raise ValidationError("Invalid Google ID token") from e