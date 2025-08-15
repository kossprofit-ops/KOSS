from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class RoomCategory(models.Model):
	STANDARD = 'STANDARD'
	DELUXE = 'DELUXE'
	SUITE = 'SUITE'
	APARTMENT = 'APARTMENT'

	KEY_CHOICES = [
		(STANDARD, 'Standard'),
		(DELUXE, 'Deluxe'),
		(SUITE, 'Suite Confort'),
		(APARTMENT, 'Appartement'),
	]

	key = models.CharField(max_length=20, choices=KEY_CHOICES, unique=True)
	title = models.CharField(max_length=50)
	description = models.TextField(blank=True)

	def __str__(self) -> str:
		return self.title


class Room(models.Model):
	number = models.CharField(max_length=10, unique=True)
	category = models.ForeignKey(RoomCategory, on_delete=models.PROTECT, related_name='rooms')
	price_cfa = models.PositiveIntegerField()
	breakfast_included = models.BooleanField(default=True)
	description = models.TextField(blank=True)

	# Features
	has_air_conditioning = models.BooleanField(default=True)
	has_hot_shower = models.BooleanField(default=True)
	has_king_bed = models.BooleanField(default=True)
	has_tv_canal_plus = models.BooleanField(default=True)
	has_desk_wifi = models.BooleanField(default=True)
	has_bath_accessories = models.BooleanField(default=True)
	has_mini_fridge = models.BooleanField(default=False)
	has_bathtub = models.BooleanField(default=False)

	is_featured = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)

	def __str__(self) -> str:
		return f"Chambre {self.number} - {self.category.title}"

	@property
	def display_price(self) -> str:
		return f"{self.price_cfa:,} F CFA".replace(',', ' ')


class RoomImage(models.Model):
	room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
	image_url = models.URLField()
	caption = models.CharField(max_length=120, blank=True)

	def __str__(self) -> str:
		return f"Image {self.room.number}"


class Reservation(models.Model):
	PENDING = 'PENDING'
	CONFIRMED = 'CONFIRMED'
	CANCELLED = 'CANCELLED'
	STATUS_CHOICES = [
		(PENDING, 'En attente'),
		(CONFIRMED, 'Confirmée'),
		(CANCELLED, 'Annulée'),
	]

	code = models.CharField(max_length=20, unique=True)
	room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='reservations')
	first_name = models.CharField(max_length=60)
	last_name = models.CharField(max_length=60)
	email = models.EmailField()
	phone = models.CharField(max_length=30)
	num_guests = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], default=1)
	special_requests = models.TextField(blank=True)
	check_in = models.DateField()
	check_out = models.DateField()
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
	total_price_cfa = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self) -> str:
		return f"{self.code} - {self.room} ({self.check_in} → {self.check_out})"

	@property
	def nights(self) -> int:
		return (self.check_out - self.check_in).days

	def compute_total(self) -> int:
		return max(self.nights, 1) * self.room.price_cfa

	def save(self, *args, **kwargs):
		self.total_price_cfa = self.compute_total()
		super().save(*args, **kwargs)

	def overlaps(self, start_date, end_date) -> bool:
		return not (self.check_out <= start_date or self.check_in >= end_date)


class Experience(models.Model):
	title = models.CharField(max_length=120)
	description = models.TextField()
	price_per_person_cfa = models.PositiveIntegerField(default=0)

	def __str__(self) -> str:
		return self.title


class ExperienceReservation(models.Model):
	PENDING = 'PENDING'
	CONFIRMED = 'CONFIRMED'
	CANCELLED = 'CANCELLED'
	STATUS_CHOICES = [
		(PENDING, 'En attente'),
		(CONFIRMED, 'Confirmée'),
		(CANCELLED, 'Annulée'),
	]

	code = models.CharField(max_length=20, unique=True)
	experience = models.ForeignKey(Experience, on_delete=models.PROTECT, related_name='reservations')
	date = models.DateField()
	participants = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], default=1)
	first_name = models.CharField(max_length=60)
	last_name = models.CharField(max_length=60)
	email = models.EmailField()
	phone = models.CharField(max_length=30)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"{self.code} - {self.experience.title} ({self.date})"


class Testimonial(models.Model):
	name = models.CharField(max_length=80)
	content = models.TextField()
	rating = models.PositiveSmallIntegerField(default=5)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"{self.name} ({self.rating}★)"
