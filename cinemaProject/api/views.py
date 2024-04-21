from datetime import date, datetime, timedelta
from rest_framework import generics
from api.serializers import (
    UserSerializer,
    EmptySerializer,
    UserLoginSerializer,
    LogoutUserSerializer,
    AuthUserSerializer,
    MovieHallSerializer,
    SessionSerializer,
    UserOrdersSerializer,
    SessionSeatSerializer,
    SessionSeatListSerializer
)
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from rest_framework import viewsets, permissions, status, serializers
from django.contrib.auth import get_user_model, authenticate, logout
from api.custom_permissions import IsOwnerOrAdminOnly, IsStaffOnly
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from cinema.models import MovieHall, Session, SessionSeat
from django.http import JsonResponse
from api.filters import CustomSessionSortingFilter

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [permissions.AllowAny]
        elif self.action == "list":
            self.permission_classes = [permissions.IsAdminUser]
        else:
            self.permission_classes = [IsOwnerOrAdminOnly]

        return [permission() for permission in self.permission_classes]

    @action(methods=["GET"], detail=True)
    def orders(self, request, pk=None):
        user = self.get_object()
        serializer = UserOrdersSerializer(user)
        return Response(serializer.data)


class AuthViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = EmptySerializer
    serializer_classes = {
        'login': UserLoginSerializer,
        'logout': LogoutUserSerializer,
    }

    @action(methods=['POST', ], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self._get_and_authenticate_user(**serializer.validated_data)
        user.update_last_request()
        data = AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)

    @staticmethod
    def _get_and_authenticate_user(username, password):
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid username/password. Please try again!")
        return user

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()

    @action(methods=['POST', ], detail=False)
    def logout(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = self._delete_token(request=request, **serializer.validated_data)
        if token:
            data = {'success': 'Successfully logged out'}
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            data = {"message": "Invalid token"}
            return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def _delete_token(request, key):
        try:
            logout(request)
            token = Token.objects.get(key=key)
            token.delete()
            return True
        except ObjectDoesNotExist:
            return False


class MovieHallViewSet(viewsets.ModelViewSet):
    queryset = MovieHall.objects.all()
    serializer_class = MovieHallSerializer
    permission_classes = [IsStaffOnly]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_updateble_hall() is False:
            return self.http_method_not_allowed(request, *args, **kwargs)

        return super().update(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        message = "Method PUT is not available for that hall"
        return Response({"message": message}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    filter_backends = [CustomSessionSortingFilter]
    ordering_fields = ['price', '-price', "time_start", "-time_start"]

    def ordering(self, queryset):
        ordering = self.request.query_params.get('ordering')
        if ordering in self.ordering_fields:
            queryset = queryset.order_by(ordering)
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            session_date=date.today(),
            time_start__gte=datetime.now().time()
        )
        return self.ordering(queryset)

    @action(methods=["GET"], detail=False)
    def tomorrow(self, request):
        tomorrow = date.today() + timedelta(days=1)
        queryset = self.queryset.filter(session_date=tomorrow)
        queryset = self.ordering(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_session_seats_booked() is False:
            return self.http_method_not_allowed(request, *args, **kwargs)

        return super().update(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        message = "Method PUT is not available for that session"
        return Response({"message": message}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve" or self.action == "tomorrow":
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [IsStaffOnly]

        return [permission() for permission in self.permission_classes]


class SessionSeatDetail(generics.RetrieveUpdateAPIView):
    queryset = SessionSeat.objects.all()
    serializer_class = SessionSeatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        session_pk = self.kwargs.get('session_pk')
        session_seats = self.queryset.filter(session_id=session_pk, is_booked=False)
        serializer = self.get_serializer(session_seats, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        session_pk = self.kwargs.get('session_pk')
        session_seats = self.queryset.filter(session_id=session_pk, is_booked=False)
        serializer = self.get_serializer(session_seats, data=request.data, many=True)
        if self.is_booked(validated_data=serializer.initial_data) is False:
            if self.is_buying(user=request.user, data=serializer.initial_data) is False:
                return Response(data={"error": "you have not enough money"})
            else:
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            return Response(data={"error": "Seats that you chose already have chosen or dont exist"})

    def is_buying(self, user, data):
        count_seats = len(data)
        try:
            session = Session.objects.get(pk=data[0]["session"])
            session_price = session.price
            return count_seats * session_price <= user.money
        except Exception as e:
            return Response(data={"error": "error"})

    def is_booked(self, validated_data):
        for data in validated_data:
            try:
                session_seat = SessionSeat.objects.get(pk=data["id"], is_booked=False)
            except Exception as e:
                return True
        return False

    def dispatch(self, request, *args, **kwargs):
        session_pk = self.kwargs.get('session_pk')
        try:
            session = Session.objects.get(pk=session_pk)
            if session.date_check():
                return JsonResponse({"error": "This session is unavailable"}, status=400)
            if session.get_available_seats == 0:
                return JsonResponse({"error": "Seats on that session are sold"}, status=400)
        except ObjectDoesNotExist as e:
            return JsonResponse({"error": "No session"}, status=400)

        return super().dispatch(request, *args, **kwargs)
