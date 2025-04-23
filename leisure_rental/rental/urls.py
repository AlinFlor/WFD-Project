from django.urls import path
from .views import equipment_list, reserve_equipment, view_invoice, rental_history, return_equipment, signup, equipment_admin, add_equipment

urlpatterns = [
    path('equipment/', equipment_list, name='equipment_list'),
    path('reserve/', reserve_equipment, name='reserve_equipment'),
    path('invoice/<int:invoice_id>/', view_invoice, name='view_invoice'),
    path('history/', rental_history, name='rental_history'),
    path('return/<int:rental_id>/', return_equipment, name='return_equipment'),
    path('signup/', signup, name='signup'),
    path('admin-panel/', equipment_admin, name='equipment_admin'),
    path('admin-panel/add/', add_equipment, name='add_equipment'),


]
