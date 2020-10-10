from django.contrib import admin

# Register your models here.
from .models import Pyme

class PostAdmin(admin.ModelAdmin):

    fields = ('pyme_name','pyme_document')

    class Meta:
       model = Pyme

admin.site.register(Pyme)
