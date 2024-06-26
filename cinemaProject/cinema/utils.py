from .models import SessionSeat, Order
from django.contrib import messages


def create_order(request, selected_seats, session):
    user = request.user
    if not is_booked(request, selected_seats):
        session_seats_update = []
        order = Order.objects.create(user=user, purchase_price=session.price)
        for session_seat_id in selected_seats:
            session_seats_update.append(SessionSeat(pk=session_seat_id, order=order, is_booked=True))
            user.buy_ticket(price=session.price)
        SessionSeat.objects.bulk_update(session_seats_update, ['order', 'is_booked'])

        messages.success(request, f"Seats were successfully booked ")


def is_booked(request, selected_seats):
    for session_seat_id in selected_seats:
        session_seat = SessionSeat.objects.get(pk=session_seat_id)
        if session_seat.is_booked:
            messages.error(
                request,
                f"Seat - {session_seat.seat.seat_number}, in Row - {session_seat.seat.row_number} \
                            was already booked, choose another place"
            )
            return True
    return False


def is_buying(request, selected_seats, session):
    count_seats = len(selected_seats)
    session_price = session.price
    return count_seats * session_price <= request.user.money


def ordering(request, queryset):
    sort_by = request.GET.get('sort_by')
    if sort_by:
        queryset = queryset.order_by(sort_by)
    return queryset
