from django.contrib.auth import get_user_model
from rest_framework import serializers
from cinema.models import MovieHall
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

