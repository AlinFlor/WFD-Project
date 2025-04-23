from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import HttpResponse

from .models import Equipment, Invoice, InvoiceItem, Rental
from .forms import RentalForm, EquipmentForm, SignupForm


# ---------- Helpers ----------

def is_admin(user):
    return user.is_authenticated and user.role == 'ADMIN'


def csrf_failure(request, reason=""):
    return render(request, "403_csrf.html", status=403)


# ---------- Public Views ----------

def index(request):
    return render(request, 'rental/index.html')


def equipment_list(request):
    equipments = Equipment.objects.filter(available=True)
    return render(request, 'rental/equipment_list.html', {'equipments': equipments})


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('equipment_list')
    else:
        form = SignupForm()

    return render(request, 'rental/signup.html', {'form': form})




# ---------- Rentals / Invoice ----------

@login_required
def reserve_equipment(request):
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.user = request.user
            rental.status = 'Reserved'
            rental.save()

            rental.equipment.available = False
            rental.equipment.save()

            days = (rental.end_date - rental.start_date).days or 1
            total = days * rental.equipment.daily_rate

            invoice = Invoice.objects.create(rental=rental, total_amount=total)
            InvoiceItem.objects.create(
                invoice=invoice,
                description=f"{rental.equipment.name} ({days} day{'s' if days > 1 else ''})",
                quantity=1,
                unit_price=rental.equipment.daily_rate
            )

            return redirect('view_invoice', invoice_id=invoice.id)
    else:
        form = RentalForm()

    return render(request, 'rental/reserve_equipment.html', {'form': form})


@login_required
def rental_history(request):
    rentals = request.user.rental_set.select_related('equipment').order_by('-start_date')
    return render(request, 'rental/rental_history.html', {'rentals': rentals})


@require_POST
@login_required
def return_equipment(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    rental.status = 'Returned'
    rental.save()

    rental.equipment.available = True
    rental.equipment.save()

    return redirect('rental_history')


def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'rental/view_invoice.html', {'invoice': invoice})


# ---------- Admin Views ----------

@user_passes_test(is_admin)
def equipment_admin(request):
    equipments = Equipment.objects.all()
    return render(request, 'rental/equipment_admin.html', {'equipments': equipments})


@user_passes_test(is_admin)
def add_equipment(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('equipment_admin')
    else:
        form = EquipmentForm()
    return render(request, 'rental/add_equipment.html', {'form': form})
