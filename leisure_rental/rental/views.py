from django.shortcuts import render
from .models import Equipment

def equipment_list(request):
    equipments = Equipment.objects.filter(available=True)
    return render(request, 'rental/equipment_list.html', {'equipments': equipments})