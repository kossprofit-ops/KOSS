document.addEventListener('DOMContentLoaded',()=>{
	// Marquee rows
	document.querySelectorAll('.marquee-row').forEach(row=>{
		const track=row.querySelector('.marquee-track');
		const direction=row.getAttribute('data-direction')==='right'?-1:1;
		let offset=0;
		function step(){
			offset+=0.5*direction;
			track.style.transform=`translateX(${offset}px)`;
			if(direction>0 && offset>0){offset=-track.scrollWidth/2}
			if(direction<0 && -offset>track.scrollWidth/2){offset=0}
			requestAnimationFrame(step);
		}
		// Duplicate images for seamless loop
		track.innerHTML=track.innerHTML+track.innerHTML;
		step();
	});

	// Booking modal handlers
	const bookingModal=document.getElementById('bookingModal');
	if(bookingModal){
		const modal=new bootstrap.Modal(bookingModal);
		document.querySelectorAll('button[data-room-id]').forEach(btn=>{
			btn.addEventListener('click',()=>{
				document.getElementById('roomId').value=btn.getAttribute('data-room-id');
				document.getElementById('roomLabel').textContent=btn.getAttribute('data-room-label');
				modal.show();
			});
		});

		document.getElementById('bookingForm').addEventListener('submit',async(e)=>{
			e.preventDefault();
			const form=e.target;
			const roomId=form.room_id.value;
			const payload=new URLSearchParams(new FormData(form));
			const res=await fetch(`/api/reservations/create/${roomId}/`,{method:'POST',headers:{'X-Requested-With':'XMLHttpRequest','X-CSRFToken':getCookie('csrftoken')},body:payload});
			const data=await res.json();
			if(data.ok){
				alert(`Réservation confirmée. Code: ${data.code}`);
				modal.hide();
			}else{
				alert(data.error||'Erreur de réservation');
			}
		});
	}

	// Search available rooms
	const searchForm=document.getElementById('search-form');
	if(searchForm){
		searchForm.addEventListener('submit',async(e)=>{
			e.preventDefault();
			const params=new URLSearchParams(new FormData(searchForm));
			const res=await fetch(`/api/rooms/search/?${params.toString()}`);
			const data=await res.json();
			if(data.results?.length){
				alert(`${data.results.length} chambre(s) disponible(s).`);
			}else{
				alert('Aucune chambre disponible pour ces critères.');
			}
		});
	}
});

function getCookie(name){
	let cookieValue=null;
	if(document.cookie && document.cookie!==''){
		const cookies=document.cookie.split(';');
		for(let i=0;i<cookies.length;i++){
			const cookie=cookies[i].trim();
			if(cookie.substring(0,name.length+1)===name+'='){
				cookieValue=decodeURIComponent(cookie.substring(name.length+1));
				break;
			}
		}
	}
	return cookieValue;
}