# -*- coding: utf-8 -*-

# Copyright 2010 Dirk Holtwick, holtwick.it
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from turbogears.decorator import weak_signature_decorator
import xhtml2pdf.pisa as pisa
from six import StringIO
import cherrypy


def to_pdf(filename=None, content_type="application/pdf"):
    def entangle(func):
        def decorated(func, *args, **kw):
            output = func(*args, **kw)
            dst = StringIO.StringIO()
            result = pisa.CreatePDF(
                StringIO.StringIO(output),
                dst
            )
            if not result.err:
                cherrypy.response.headers["Content-Type"] = content_type
                if filename:
                    cherrypy.response.headers["Content-Disposition"] = "attachment; filename=" + filename
                output = dst.getvalue()
            return output

        return decorated

    return weak_signature_decorator(entangle)


topdf = to_pdf
