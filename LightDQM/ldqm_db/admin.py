from django.contrib import admin

# Register your models here.

from ldqm_db.models import Run, AMC, GEB
admin.site.register(Run)
admin.site.register(AMC)
admin.site.register(GEB)
