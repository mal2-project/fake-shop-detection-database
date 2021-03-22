import base64
import logging
import mimetypes
import os
from urllib import parse

import magic
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import (
    TemplateView,
    View,
)

from mal2.views.toaster import ToasterMixin


################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# UPLOAD MIXIN

class UploadMixin(object):
    accept = None
    location = settings.MEDIA_ROOT
    max_upload_size = settings.MAX_UPLOAD_SIZE

    def get_filename(self, f):
        path = os.path.join(self.get_location(), f.name)

        if os.path.exists(path):
            name, ext = os.path.splitext(f.name)

            return "%s (%s)%s" % (
                name,
                timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                ext,
            )

        return f.name

    def get_location(self):
        return os.path.join(self.location)

    def post(self, request):
        fs = FileSystemStorage(
            location=self.get_location(),
        )

        self.files = []

        for key, f in request.FILES.items():
            filename = self.get_filename(f)

            name, ext = os.path.splitext(f.name)

            if (self.accept is None or ext in self.accept) and f.size <= self.max_upload_size:
                filename = fs.save(filename, f)
                self.files.append(filename)

        if len(self.files) == 0:
            raise Exception(
                "Files dictionary is empty! Extensions not exists in \"accept\" and/or all file sizes are to large."
            )

        context = self.get_context_data()

        return JsonResponse(context)

    def get_context_data(self):
        context = {
            "files": self.files,
            "location": self.get_location(),
        }

        return context


################################################################################
# SECURE MEDIA VIEW

class SecureMediaView(LoginRequiredMixin, View):
    def is_server_localhost(self):
        server = self.request.META.get("HTTP_HOST", None)

        if server is not None and (server == "127.0.0.1:8000" or server == "localhost:8000"):
            return True

        return False

    def get(self, request, *args, **kwargs):
        path_str = kwargs.get("path_str", "")
        path = os.path.join(settings.MEDIA_ROOT, path_str)

        if not path.startswith(os.path.join(settings.MEDIA_ROOT, str(request.user.id))):
            return HttpResponseForbidden()

        if not os.path.exists(path) or os.path.isdir(path):
            raise Http404(_("File not found"))

        filename = os.path.basename(path)

        http_response = HttpResponse(
            content_type=magic.from_file(path, mime=True)
        )

        http_response["Content-Disposition"] = "inline; filename=\"%s\"" % (filename,)
        http_response["Content-Length"] = os.path.getsize(path)

        if self.is_server_localhost():
            with open(path, "rb") as f:
                http_response.write(f.read())
        else:
            http_response["X-Sendfile"] = path.encode("utf-8")

        return http_response


################################################################################
# FILE TREE

class FileTreeView(LoginRequiredMixin, TemplateView):
    allowed_file_extensions = None
    template_name = "media/file_tree.html"
    file_storage_root = settings.MEDIA_ROOT

    def listdir_nohidden(self, path):
        for f in os.listdir(path):
            if not f.startswith("."):
                yield f

    def get_all_file_extensions(self, path):
        list_of_files = self.listdir_nohidden(path)
        file_extensions = []

        for file_name in list_of_files:
            absolute_path = os.path.join(path, file_name)

            if os.path.isdir(absolute_path):
                file_extensions += self.get_all_file_extensions(absolute_path)
            else:
                file_extension = os.path.splitext(file_name)[1]
                file_extensions.append(file_extension)

        return set(file_extensions)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        path = request.POST.get("dir", self.file_storage_root)
        content = []

        try:
            path = parse.unquote(path)

            for file_name in sorted(self.listdir_nohidden(path)):
                absolute_path = os.path.join(path, file_name)

                if os.path.isdir(absolute_path):
                    all_file_extensions = self.get_all_file_extensions(absolute_path)

                    file_content = {
                        "absolute_path": absolute_path,
                        "extension": None,
                        "file_name": file_name,
                        "is_dir": True,
                    }

                    if self.allowed_file_extensions is False:
                        content.append(file_content)
                    else:
                        for all_file_extension in all_file_extensions:
                            if all_file_extension in self.allowed_file_extensions:
                                content.append(file_content)
                                break
                else:
                    file_extension = os.path.splitext(file_name)[1]

                    if self.allowed_file_extensions is not False:
                        if self.allowed_file_extensions is None or file_extension in self.allowed_file_extensions:
                            content.append({
                                "absolute_path": absolute_path,
                                "file_extension": file_extension,
                                "file_name": file_name,
                                "is_dir": False,
                            })
        except OSError:
            logger.exception(type(self).__class__.__name)

        context.update({
            "content": content,
        })

        return self.render_to_response(context)


################################################################################
# DOWNLOAD BLOB

class DownloadBlobView(ToasterMixin, View):
    file_path = None

    @property
    def success_message(self):
        return _("Downloading %s") % self.file_name

    @property
    def error_message(self):
        return _("Can't download file!")

    def get_file_path(self):
        if self.file_path is None:
            raise ImproperlyConfigured(
                "%s requires either a definition of "
                "'file_path' or an implementation of 'get_file_path()'" % self.__class__.__name__
            )

        return self.file_path

    def to_base64(self, file):
        with open(file, "rb") as f:
            base64_file = base64.b64encode(f.read())

        return base64_file.decode("utf-8")

    def get(self, request, *args, **kwargs):
        file_path = self.get_file_path()

        if os.path.exists(file_path):
            self.file_name = os.path.basename(file_path)
            text = self.success_message
            base64_file = self.to_base64(file_path)
            success = True
        else:
            self.file_name = None
            text = self.error_message
            base64_file = None
            success = False

        data = {
            "toaster": self.get_toaster(
                request=self.request,
                text=text,
                success=success
            ),
        }

        if base64_file:
            data.update({
                "base64": base64_file,
                "content_type": mimetypes.MimeTypes().guess_type(file_path)[0],
                "file_name": self.file_name,
            })

        return JsonResponse(data)
