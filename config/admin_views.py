from django.contrib import admin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse
from django.urls.exceptions import NoReverseMatch


def _safe_reverse(name, default):
    try:
        return reverse(name)
    except NoReverseMatch:
        return default


def import_export_dashboard(request):
    """Admin dashboard for Excel import/export helpers."""
    sections = [
        {
            'title': _('Projects'),
            'description': _('Project ma’lumotlarini Excel orqali boshqarish.'),
            'template_url': _safe_reverse('project-template-xlsx', '/api/v1/project/template-xlsx/'),
            'export_url': _safe_reverse('project-export-xlsx', '/api/v1/project/export-xlsx/'),
            'import_url': _safe_reverse('project-import-xlsx', '/api/v1/project/import-xlsx/'),
        },
        {
            'title': _('Clients'),
            'description': _('Client ma’lumotlari uchun import/export.'),
            'template_url': _safe_reverse('client-template-xlsx', '/api/v1/client/template-xlsx/'),
            'export_url': _safe_reverse('client-export-xlsx', '/api/v1/client/export-xlsx/'),
            'import_url': _safe_reverse('client-import-xlsx', '/api/v1/client/import-xlsx/'),
        },
        {
            'title': _('Nomenklatura'),
            'description': _('Nomenklatura yozuvlari uchun Excel operatsiyalari.'),
            'template_url': _safe_reverse('nomenklatura-template-xlsx', '/api/v1/nomenklatura/template-xlsx/'),
            'export_url': _safe_reverse('nomenklatura-export-xlsx', '/api/v1/nomenklatura/export-xlsx/'),
            'import_url': _safe_reverse('nomenklatura-import-xlsx', '/api/v1/nomenklatura/import-xlsx/'),
        },
    ]

    context = {
        **admin.site.each_context(request),
        'sections': sections,
        'title': _('Import & Export'),
        'site_title': admin.site.site_title,
        'site_header': admin.site.site_header,
    }
    return TemplateResponse(request, 'admin/import_export_dashboard.html', context)

