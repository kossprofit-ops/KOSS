from django.core.management.base import BaseCommand
from core.models import RoomCategory, Room, RoomImage, Testimonial, Experience


class Command(BaseCommand):
	help = 'Seed hotel data (categories, rooms, images, testimonials, experiences)'

	def handle(self, *args, **options):
		self.stdout.write('Seeding data...')
		# Categories
		cat_standard, _ = RoomCategory.objects.get_or_create(key='STANDARD', defaults={'title': 'Standard'})
		cat_deluxe, _ = RoomCategory.objects.get_or_create(key='DELUXE', defaults={'title': 'Deluxe'})
		cat_suite, _ = RoomCategory.objects.get_or_create(key='SUITE', defaults={'title': 'Suite Confort'})
		cat_appt, _ = RoomCategory.objects.get_or_create(key='APARTMENT', defaults={'title': 'Appartement'})

		def add_room(number, category, price, ac=True, hot=True, fridge=False, bathtub=False, featured=False):
			room, created = Room.objects.get_or_create(number=str(number), defaults={
				'category': category,
				'price_cfa': price,
				'has_air_conditioning': ac,
				'has_hot_shower': hot,
				'has_mini_fridge': fridge,
				'has_bathtub': bathtub,
				'is_featured': featured,
			})
			if created:
				urls = [
					'https://images.unsplash.com/photo-1560185127-6ed189bf02e3?q=80&w=1200',
					'https://images.unsplash.com/photo-1496412705862-e0088f16f791?q=80&w=1200',
					'https://images.unsplash.com/photo-1551776235-dde6d4829808?q=80&w=1200',
					'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=1200',
					'https://images.unsplash.com/photo-1596436889106-be35e843f974?q=80&w=1200',
					'https://images.unsplash.com/photo-1606046604972-77cc76aee944?q=80&w=1200',
				]
				for u in urls:
					RoomImage.objects.create(room=room, image_url=u)
			return room

		# Standard
		add_room(105, cat_standard, 17000, ac=True, hot=True, featured=True)
		add_room(107, cat_standard, 17000, ac=True, hot=True)
		add_room(208, cat_standard, 17000, ac=True, hot=True)
		add_room(104, cat_standard, 15000, ac=True, hot=False)
		add_room(106, cat_standard, 15000, ac=True, hot=False)
		add_room(101, cat_standard, 12500, ac=False, hot=False)

		# Deluxe
		add_room(202, cat_deluxe, 22000, ac=True, hot=True, fridge=True, featured=True)
		add_room(203, cat_deluxe, 22000, ac=True, hot=True, fridge=True)
		add_room(204, cat_deluxe, 22000, ac=True, hot=True, fridge=True)
		add_room(206, cat_deluxe, 23000, ac=True, hot=True, fridge=True)
		add_room(201, cat_deluxe, 17000, ac=True, hot=False, fridge=True)

		# Suites
		add_room(305, cat_suite, 35000, ac=True, hot=True, bathtub=True, fridge=True, featured=True)
		add_room(304, cat_suite, 25000, ac=True, hot=True, fridge=True)
		add_room(303, cat_suite, 17000, ac=True, hot=False, fridge=True)

		# Appartements
		add_room('A3-Salon', cat_appt, 75000, ac=True, hot=True, fridge=True)
		add_room(207, cat_appt, 35000, ac=True, hot=True, fridge=True)
		add_room(102, cat_appt, 20000, ac=True, hot=True, fridge=True)

		# Testimonials
		if not Testimonial.objects.exists():
			Testimonial.objects.create(name='Patrick', content='5 étoiles – Luxe et confort réunis', rating=5)
			Testimonial.objects.create(name='Nadia', content='Séjour incroyable, personnel attentionné', rating=5)
			Testimonial.objects.create(name='Koffi', content='Très bon rapport qualité/prix', rating=4)

		# Experiences
		Experience.objects.get_or_create(title='Randonnée aux cascades', defaults={'description': 'Explorez les cascades emblématiques de Kpalimé avec guide.', 'price_per_person_cfa': 10000})
		Experience.objects.get_or_create(title='Atelier de percussions', defaults={'description': 'Initiez-vous aux rythmes traditionnels africains.', 'price_per_person_cfa': 8000})
		Experience.objects.get_or_create(title='Dégustation culinaire', defaults={'description': 'Gastronomie locale et européenne au restaurant de l’hôtel.', 'price_per_person_cfa': 15000})

		self.stdout.write(self.style.SUCCESS('Seeding terminé.'))