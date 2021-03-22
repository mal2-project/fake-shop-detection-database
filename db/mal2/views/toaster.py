import logging

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View


################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# TOASTER

class ToasterMixin(object):
    def get_toaster(self, request, text, success):
        return render_to_string(
            "toaster/base.html", {
                "text": text,
                "success": success,
            },
            request=request,
        ),


@method_decorator(csrf_exempt, name="dispatch")
class ToasterView(ToasterMixin, View):
    def post(self, request, *args, **kwargs):
        data = request.POST

        context = {
            "toaster": self.get_toaster(
                request=self.request,
                text=data.get("text", None),
                success=data.get("success", False),
            ),
        }

        return JsonResponse(context)
