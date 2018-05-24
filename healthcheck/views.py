from directory_healthcheck.views import BaseHealthCheckAPIView

from healthcheck.backends import SingleSignOnBackend


class SingleSignOnAPIView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return SingleSignOnBackend()
