from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('a-propos/', views.about, name='about'),
	path('chambres/', views.rooms_catalog, name='rooms'),
	path('activites/', views.activities, name='activities'),
	path('contact/', views.contact, name='contact'),

	path('api/rooms/search/', views.search_available_rooms, name='search_rooms'),
	path('api/reservations/create/<int:room_id>/', views.create_reservation, name='create_reservation'),

	path('dashboard/', views.dashboard, name='dashboard'),
	path('dashboard/export/csv/', views.export_reservations_csv, name='export_csv'),
	path('dashboard/export/pdf/', views.export_reservations_pdf, name='export_pdf'),
]