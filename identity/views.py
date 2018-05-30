from rest_framework.response import Response

from rest_framework import views


class IdentityVerificationAPIView(views.APIView):
    http_method_names = ("post", )

    def post(self, request, *args, **kwargs):
        # trigger the Matching Service Adaptor to provide user data to the
        # government service that triggered the verification flow
        return Response({'result': 'no-match'})
