import logging
import tempfile

from django.http import FileResponse
from django.template.loader import get_template
from django.utils import timezone
from django.views.generic import View
from z3c.rml import rml2pdf


################################################################################
# LOGGER

logger = logging.getLogger(__name__)


################################################################################
# BASE PDF VIEW

class BasePDFView(View):
    document_title = "Detail PDF"
    template_name = "pdf/base.rml"

    def _generate_pdf(self):
        template = get_template(self.template_name)

        xmlstring = template.render({
            "request": self.request,
            "title": self.get_document_title(),
            "current_date": timezone.now(),
            "pdf_data": self.get_pdf_data(),
        })

        pdf_io = rml2pdf.parseString(xmlstring)

        f = tempfile.NamedTemporaryFile()
        f.write(pdf_io.read())
        f.seek(0)

        return f

    def get_pdf_data(self):
        return {
            "headline": "Headline",
            "text": "PDF example text",
        }

    def get_document_title(self):
        return self.document_title

    def get(self, request, *args, **kwargs):
        f = self._generate_pdf()

        response = FileResponse(f, content_type="application/pdf")

        response["Content-Disposition"] = "Attachment; filename=%s.pdf" % (
            self.get_document_title(),
        )

        return response
