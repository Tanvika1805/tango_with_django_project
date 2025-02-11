from django.contrib import admin
from rango.models import Category, Page
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')   # Display these fields in the admin panel

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'views', 'likes')  # Optional: Display extra fields

# Register models with their custom admin views
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)

# Register your models here.
