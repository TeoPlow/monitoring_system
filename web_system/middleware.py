from django.http import JsonResponse
from threading import Lock


class Token:
    """Хранилище токенов"""
    def __init__(self):
        self.tokens = set()
        self.lock = Lock()

    def add(self, token):
        with self.lock:
            self.tokens.add(token)

    def remove(self, token):
        with self.lock:
            self.tokens.discard(token)

    def is_valid(self, token):
        with self.lock:
            return token in self.tokens


token_store = Token()


class CustomAuthMiddleware:
    """Самописный middleware для аутентификации по токену"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.path.startswith("/web_system/api/")
            and not request.path.endswith("/login/")
            and not request.path.endswith("/logout/")
        ):
            token = request.COOKIES.get("auth_token")
            if not token or not token_store.is_valid(token):
                return JsonResponse({"error": "Unauthorized"}, status=401)
        return self.get_response(request)
