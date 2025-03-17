# users/backends.py
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailOrUsernameBackend(ModelBackend):
    """
    Allow authentication with either a username or an email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        user = None
        # Try to fetch user by email first
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # If not found by email, try by username
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None
