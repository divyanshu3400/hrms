import threading

thread_local = threading.local()

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        thread_local.current_user = request.user
        response = self.get_response(request)
        return response

    @staticmethod
    def get_current_user():
        return getattr(thread_local, 'current_user', None)
