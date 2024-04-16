from datetime import date, time

from django.contrib.auth import get_user_model
from rest_framework import serializers
from cinema.models import MovieHall, Session
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    email = serializers.EmailField()
    url = serializers.HyperlinkedIdentityField(read_only=True, view_name="user-detail")
    password = serializers.CharField(write_only=True, max_length=200)
    first_name = serializers.CharField(required=False, max_length=200)
    last_name = serializers.CharField(required=False, max_length=200)
    money = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)

    class Meta:
        model = User
        fields = ["id", "url", "email", "username", "password", "first_name", "last_name", "money"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists")
        return email


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True, write_only=True)


class AuthUserSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'auth_token',)
        read_only_fields = ('id', 'is_active', 'is_staff')

    def get_auth_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key


class EmptySerializer(serializers.Serializer):
    pass


class LogoutUserSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=50, write_only=True)


class MovieHallSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(read_only=True, view_name="moviehall-detail")

    class Meta:
        model = MovieHall
        fields = ["id", "url", "name", "rows", "seats_per_row"]

    def create(self, validated_data):
        hall = MovieHall.objects.create(**validated_data)
        hall.create_seats_for_hall()
        return hall

    def update(self, instance, validated_data):
        instance.delete_seats_and_session_seats()
        instance = super().update(instance, validated_data)
        instance.update_seats_for_hall()
        return instance

    def validate_rows(self, rows):
        if rows <= 0:
            raise serializers.ValidationError("Count should be bigger than 0")
        return rows

    def validate_seats_per_row(self, seats_per_row):
        if seats_per_row <= 0:
            raise serializers.ValidationError("Count should be bigger than 0")
        return seats_per_row

    def validate_name(self, name):
        if self.context['view'].action == "create":
            if MovieHall.objects.filter(name__iexact=name).exists():
                raise serializers.ValidationError("Hall with that name already exists")
            return name
        if self.context['view'].action == "update":
            if MovieHall.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Hall with that name already exists")
            return name
        return name


class SessionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(read_only=True, view_name="session-detail")
    available_seats = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "url",
            "movie",
            "time_start",
            "time_end",
            "date_start",
            "date_end",
            "session_date",
            "price",
            "hall",
            "available_seats"
        ]

    default_error_messages = {
        "invalid_date": "session date should be between start date and end date",
        "invalid_session": "session on this time in that hall already exists",
        "invalid_price": "price should be bigger than 0",
        "invalid_time": "invalid format time"
    }

    def get_available_seats(self, obj):
        return obj.get_available_seats

    def create(self, validated_data):
        session = Session.objects.create(**validated_data)
        session.create_session_seats()
        return session

    def update(self, instance, validated_data):
        instance.delete_session_seats()
        instance = super().update(instance, validated_data)
        instance.create_session_seats()
        return instance

    def validate_price(self, price):
        if price <= 0:
            raise serializers.ValidationError(
                self.error_messages['invalid_price'],
                code='invalid_price'
            )
        return price

    def is_session_date_between(self, session_date, date_start, date_end):
        if isinstance(session_date, date) and isinstance(date_start, date) and isinstance(date_end, date):
            if not (date_start <= session_date <= date_end):
                raise serializers.ValidationError(
                    self.default_error_messages['invalid_date'],
                    code='invalid_date'
                )
            return True

    def validate_time(self, time_start, time_end, session_date, hall, session_pk=None):
        if isinstance(time_start, time) and isinstance(time_end, time):
            if (Session.objects.exists_session_by_time(time_end, session_date, hall)
                    or Session.objects.exists_session_by_time(time_start, session_date, hall, session_pk)):
                raise serializers.ValidationError(
                    self.default_error_messages['invalid_session'],
                    code=["invalid_session"]
                )

    def validate(self, data):
        session_date = data.get('session_date')
        date_start = data.get('date_start')
        date_end = data.get('date_end')
        time_start = data.get('time_start')
        time_end = data.get('time_end')
        hall = data['hall']
        instance = self.instance
        if self.is_session_date_between(session_date, date_start, date_end):
            if self.context['view'].action == "create":
                self.validate_time(time_start, time_end, session_date, hall)
            if self.context['view'].action == "update":
                if isinstance(time_start, time) and isinstance(time_end, time):
                    self.validate_time(time_start, time_end, session_date, hall, session_pk=instance.pk)
                else:
                    raise serializers.ValidationError(
                        self.default_error_messages['invalid_time'],
                        code="invalid_time"
                    )
        return data
