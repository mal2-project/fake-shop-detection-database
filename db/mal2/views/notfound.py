import logging

from django.views.generic import TemplateView


################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# ERROR

class ErrorMixin(TemplateView):
    code = None

    @classmethod
    def get_rendered_view(cls):
        as_view_fn = cls.as_view()

        def view_fn(request, exception=None):
            response = as_view_fn(request, exception)
            response.status_code = cls.code
            response.render()

            return response

        return view_fn


class NoPermissionView(ErrorMixin):
    code = 403
    template_name = "403.html"


class PageNotFoundView(ErrorMixin):
    code = 404
    template_name = "404.html"


class ServerErrorView(ErrorMixin):
    code = 500
    template_name = "500.html"
