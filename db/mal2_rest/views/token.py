from rest_framework.authtoken import views as rest_views
from rest_framework.generics import GenericAPIView


################################################################################
# AUTH TOKEN

# GenericAPIView required for swagger
# https://github.com/marcgibbons/django-rest-swagger/issues/629#issuecomment-298806087
class ObtainAuthToken(rest_views.ObtainAuthToken, GenericAPIView):
    pass
