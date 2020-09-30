import io

from django.http import HttpResponse


def docx_response(doc, filename):
    f = io.BytesIO()
    doc.save(f)
    length = f.tell()
    f.seek(0)
    response = HttpResponse(
        f.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}.docx'
    response['Content-Length'] = length
    return response