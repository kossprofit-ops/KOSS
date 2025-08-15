from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.admin.views.decorators import staff_member_required
from datetime import date, timedelta
import csv
from reportlab.pdfgen import canvas
from io import BytesIO

from .models import Room, RoomCategory, Reservation, Testimonial, Experience
from .utils import generate_reservation_code, is_room_available


def home(request):
	featured_rooms = Room.objects.filter(is_active=True, is_featured=True).select_related('category')[:3]
	testimonials = Testimonial.objects.all().order_by('-created_at')[:3]
	return render(request, 'home.html', {
		'featured_rooms': featured_rooms,
		'testimonials': testimonials,
	})


def about(request):
	return render(request, 'about.html')


@ensure_csrf_cookie
def rooms_catalog(request):
	category_key = request.GET.get('category')
	categories = RoomCategory.objects.all()
	rooms = Room.objects.filter(is_active=True).select_related('category').order_by('category__title', 'number')
	if category_key:
		rooms = rooms.filter(category__key=category_key)
	testimonials = Testimonial.objects.all().order_by('-created_at')[:3]
	return render(request, 'rooms.html', {
		'categories': categories,
		'rooms': rooms,
		'active_category': category_key,
		'testimonials': testimonials,
	})


def activities(request):
	experiences = Experience.objects.all()
	return render(request, 'activities.html', {'experiences': experiences})


def contact(request):
	return render(request, 'contact.html')


@require_http_methods(["GET"])
def search_available_rooms(request):
	check_in = request.GET.get('check_in')
	check_out = request.GET.get('check_out')
	category = request.GET.get('category')
	query = Room.objects.filter(is_active=True)
	if category:
		query = query.filter(category__key=category)
	available = []
	if check_in and check_out:
		for room in query.select_related('category'):
			if is_room_available(room, check_in, check_out):
				available.append({
					'id': room.id,
					'label': f"{room.category.title} – Chambre {room.number} ({room.display_price})",
				})
	return JsonResponse({'results': available})


@require_http_methods(["POST"])
def create_reservation(request, room_id):
	room = get_object_or_404(Room, id=room_id, is_active=True)
	check_in = request.POST.get('check_in')
	check_out = request.POST.get('check_out')
	first_name = request.POST.get('first_name')
	last_name = request.POST.get('last_name')
	email = request.POST.get('email')
	phone = request.POST.get('phone')
	num_guests = int(request.POST.get('num_guests', '1'))
	special_requests = request.POST.get('special_requests', '')
	if not is_room_available(room, check_in, check_out):
		return JsonResponse({'ok': False, 'error': "La chambre n'est plus disponible pour ces dates."}, status=400)
	code = generate_reservation_code()
	reservation = Reservation.objects.create(
		code=code,
		room=room,
		first_name=first_name,
		last_name=last_name,
		email=email,
		phone=phone,
		num_guests=num_guests,
		special_requests=special_requests,
		check_in=check_in,
		check_out=check_out,
	)
	return JsonResponse({'ok': True, 'code': reservation.code})


# Admin dashboard views (simple custom pages)

@staff_member_required
def dashboard(request):
	total_rooms = Room.objects.count()
	total_reservations = Reservation.objects.count()
	current_date = date.today()
	occupied = Reservation.objects.filter(status=Reservation.CONFIRMED, check_in__lte=current_date, check_out__gt=current_date).count()
	occupancy_rate = (occupied / total_rooms * 100) if total_rooms else 0
	monthly_revenue = Reservation.objects.filter(status=Reservation.CONFIRMED, created_at__gte=current_date.replace(day=1)).aggregate(total=Sum('total_price_cfa'))['total'] or 0
	return render(request, 'dashboard/index.html', {
		'total_rooms': total_rooms,
		'total_reservations': total_reservations,
		'occupancy_rate': round(occupancy_rate, 1),
		'monthly_revenue': monthly_revenue,
	})


@staff_member_required
def export_reservations_csv(request):
	status = request.GET.get('status')
	start = request.GET.get('start')
	end = request.GET.get('end')
	qs = Reservation.objects.all()
	if status:
		qs = qs.filter(status=status)
	if start:
		qs = qs.filter(check_in__gte=start)
	if end:
		qs = qs.filter(check_out__lte=end)
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="reservations.csv"'
	writer = csv.writer(response)
	writer.writerow(['Code', 'Chambre', 'Arrivée', 'Départ', 'Nom', 'Prénom', 'Email', 'Téléphone', 'Statut', 'Total'])
	for r in qs:
		writer.writerow([r.code, r.room.number, r.check_in, r.check_out, r.last_name, r.first_name, r.email, r.phone, r.status, r.total_price_cfa])
	return response


@staff_member_required
def export_reservations_pdf(request):
	status = request.GET.get('status')
	start = request.GET.get('start')
	end = request.GET.get('end')
	qs = Reservation.objects.all()
	if status:
		qs = qs.filter(status=status)
	if start:
		qs = qs.filter(check_in__gte=start)
	if end:
		qs = qs.filter(check_out__lte=end)
	buffer = BytesIO()
	p = canvas.Canvas(buffer)
	p.setTitle('Réservations')
	y = 800
	p.drawString(50, y, 'Liste des réservations')
	y -= 20
	for r in qs[:500]:
		line = f"{r.code} | Chambre {r.room.number} | {r.check_in} → {r.check_out} | {r.last_name} {r.first_name} | {r.status} | {r.total_price_cfa} F"
		p.drawString(50, y, line)
		y -= 15
		if y < 50:
			p.showPage()
			y = 800
	p.save()
	buffer.seek(0)
	return HttpResponse(buffer.read(), content_type='application/pdf')
