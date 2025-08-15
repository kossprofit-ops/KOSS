from django.contrib import admin
from .models import RoomCategory, Room, RoomImage, Reservation, Experience, ExperienceReservation, Testimonial


class RoomImageInline(admin.TabularInline):
	model = RoomImage
	extra = 1


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
	list_display = ('number', 'category', 'price_cfa', 'is_featured', 'is_active')
	list_filter = ('category', 'is_featured', 'is_active')
	search_fields = ('number',)
	inlines = [RoomImageInline]


@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
	list_display = ('title', 'key')
	search_fields = ('title', 'key')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
	list_display = ('code', 'room', 'check_in', 'check_out', 'status', 'total_price_cfa')
	list_filter = ('status', 'room__category')
	search_fields = ('code', 'first_name', 'last_name', 'email', 'phone')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
	list_display = ('title', 'price_per_person_cfa')
	search_fields = ('title',)


@admin.register(ExperienceReservation)
class ExperienceReservationAdmin(admin.ModelAdmin):
	list_display = ('code', 'experience', 'date', 'participants', 'status')
	list_filter = ('status',)
	search_fields = ('code', 'first_name', 'last_name', 'email', 'phone')


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
	list_display = ('name', 'rating', 'created_at')
	search_fields = ('name', 'content')
