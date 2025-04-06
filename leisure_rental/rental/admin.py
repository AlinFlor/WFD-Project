from django.contrib import admin
from .models import User, Equipment, Rental, Invoice, InvoiceItem

admin.site.register(User)
admin.site.register(Equipment)
admin.site.register(Rental)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)