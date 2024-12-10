from django.contrib import admin
from .models import Art

@admin.register(Art)
class ArtAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'created_at')
