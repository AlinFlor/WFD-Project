from django.test import TestCase, Client
from django.urls import reverse
from rental.models import Equipment, Rental, User, Invoice
from datetime import date, timedelta


class EquipmentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='password', role='ADMIN')
        self.customer = User.objects.create_user(username='user1', password='password', role='CUSTOMER')

        self.equipment1 = Equipment.objects.create(
            name="Bike", type="Outdoor", daily_rate=10, available=True, condition="Good"
        )
        self.equipment2 = Equipment.objects.create(
            name="Rod", type="Fishing", daily_rate=5, available=False, condition="Worn"
        )

    # ------------------ ORIGINAL TESTS ------------------

    def test_equipment_list_shows_only_available(self):
        response = self.client.get(reverse('equipment_list'))
        self.assertContains(response, "Bike")
        self.assertNotContains(response, "Rod")

    def test_admin_panel_requires_admin(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('equipment_admin'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_admin_panel_grants_admin_access(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('equipment_admin'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Panel")

    def test_reserve_equipment_creates_rental_invoice(self):
        self.client.login(username='user1', password='password')
        start = date.today()
        end = start + timedelta(days=2)

        response = self.client.post(reverse('reserve_equipment'), {
            'equipment': self.equipment1.id,
            'start_date': start,
            'end_date': end
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        rental = Rental.objects.get(user=self.customer)
        invoice = Invoice.objects.get(rental=rental)

        self.assertEqual(invoice.total_amount, 20)
        self.assertFalse(rental.equipment.available)
        self.assertContains(response, "Invoice")

    def test_return_equipment_marks_available(self):
        rental = Rental.objects.create(
            user=self.customer,
            equipment=self.equipment1,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            status='Reserved'
        )
        self.equipment1.available = False
        self.equipment1.save()

        self.client.login(username='user1', password='password')
        response = self.client.post(reverse('return_equipment', args=[rental.id]), follow=True)

        rental.refresh_from_db()
        self.equipment1.refresh_from_db()
        self.assertEqual(rental.status, 'Returned')
        self.assertTrue(self.equipment1.available)

    def test_signup_creates_customer(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'password',
            'password2': 'password'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.role, 'CUSTOMER')


    def test_equipment_detail_page_redirects_for_anonymous(self):
        response = self.client.get(reverse('reserve_equipment'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_rental_history_requires_login(self):
        response = self.client.get(reverse('rental_history'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_signup_invalid_passwords(self):
        response = self.client.post(reverse('signup'), {
        'username': 'failuser',
        'password1': '123',
        'password2': '123'
    })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This password is too short")



    def test_admin_can_add_equipment(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('add_equipment'), {
            'name': 'Helmet',
            'type': 'Safety',
            'daily_rate': 3.5,
            'available': True,
            'condition': 'Good'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Helmet')

    def test_invoice_string_representation(self):
        rental = Rental.objects.create(
            user=self.customer,
            equipment=self.equipment1,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            status='Reserved'
        )
        invoice = Invoice.objects.create(rental=rental, total_amount=10.00)
        self.assertEqual(str(invoice), f"Invoice #{invoice.id}")

    def test_equipment_string_representation(self):
        self.assertEqual(str(self.equipment1), "Bike")
