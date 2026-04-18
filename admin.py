from django.contrib import admin
from .models import Design


@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
	list_display = ('title', 'contractor', 'project', 'product', 'price', 'created_at')
	list_filter = ('contractor', 'created_at')
	search_fields = ('title', 'description')
