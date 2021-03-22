import logging

from mal2.utils import (
    remove_current_user,
    set_current_user,
)


################################################################################
# LOGGING

logger = logging.getLogger(__name__)


################################################################################
# CURRENT USER

class CurrentUserMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_user(getattr(request, "user", None))

        response = self.get_response(request)

        remove_current_user()

        return response
