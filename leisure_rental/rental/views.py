from django.shortcuts import render
from .models import Equipment

def equipment_list(request):
    equipments = Equipment.object.filter(available=True)
    return rende(request, 'rental/equipment_list.html', {'equipments': equipments})