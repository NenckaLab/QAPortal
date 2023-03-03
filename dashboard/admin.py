from django.contrib import admin

from .models import Graph, DateChoice, Scanner, Coil

# Register your models here.
admin.site.register(Graph)
admin.site.register(DateChoice)
admin.site.register(Scanner)
admin.site.register(Coil)
