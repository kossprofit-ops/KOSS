import random
import string
from datetime import date
from .models import Reservation


def generate_reservation_code() -> str:
	return 'RC' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def is_room_available(room, check_in_str: str, check_out_str: str) -> bool:
	try:
		check_in = date.fromisoformat(check_in_str)
		check_out = date.fromisoformat(check_out_str)
	except Exception:
		return False
	if check_in >= check_out:
		return False
	overlap = Reservation.objects.filter(room=room).filter(check_in__lt=check_out, check_out__gt=check_in).exclude(status=Reservation.CANCELLED).exists()
	return not overlap