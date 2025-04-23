from django.shortcuts import render, redirect
from .forms import RentalForm
from .models import Equipment, Invoice, InvoiceItem, Rental
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def csrf_failure(request, reason=""):
    return render(request, "403_csrf.html", status=403)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log them in
            return redirect('equipment_list')
    else:
        form = UserCreationForm()
    
    return render(request, 'rental/signup.html', {'form': form})


def index(request):
    return render(request, 'rental/index.html')


@require_POST
@login_required
def return_equipment(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    rental.status = 'Returned'
    rental.save()

    rental.equipment.available = True
    rental.equipment.save()

    return redirect('rental_history')


@login_required
def rental_history(request):
    rentals = request.user.rental_set.select_related('equipment').order_by('-start_date')
    return render(request, 'rental/rental_history.html', {'rentals': rentals})



def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'rental/view_invoice.html', {'invoice': invoice})

def equipment_list(request):
    equipments = Equipment.objects.filter(available=True)
    return render(request, 'rental/equipment_list.html', {'equipments': equipments})

@login_required(login_url='login')
def reserve_equipment(request):
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.user = request.user
            rental.status = 'Reserved'
            rental.save()

            # Mark equipment as unavailable
            rental.equipment.available = False
            rental.equipment.save()

            # Create invoice
            days = (rental.end_date - rental.start_date).days or 1
            total = days * rental.equipment.daily_rate
            invoice = Invoice.objects.create(rental=rental, total_amount=total)

            # Add invoice item
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