from rest_framework_simplejwt.tokens import RefreshToken


def create_jwt_token(user):
    """
    Custom way to create an authentication token using simple jwt.
    """
    token = RefreshToken.for_user(user)
    data = {
        'refresh_token': str(token),
        'access_token': str(token.access_token)
    }
    return data, True
