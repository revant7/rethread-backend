# from rest_framework import serializers
# from .models import (
#     User,
#     Customer,
#     Staff,
#     Product,
#     Address,
#     Order,
#     OrderItem,
#     Cart,
#     CartItem,
# )

# from django.contrib.auth import get_user_model
# from rest_framework import serializers
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# User = get_user_model()


# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         # Add custom claims to the token
#         token["email"] = user.email
#         token["first_name"] = user.first_name
#         token["last_name"] = user.last_name
#         token["is_staff"] = user.is_staff

#         return token

#     def validate(self, attrs):
#         # Use email and password for authentication
#         email = attrs.get("email")
#         password = attrs.get("password")

#         if email and password:
#             try:
#                 user = User.objects.get(email=email)
#             except User.DoesNotExist:
#                 raise serializers.ValidationError("Invalid email or password.")

#             if not user.check_password(password):
#                 raise serializers.ValidationError("Invalid email or password.")

#             data = super().validate(attrs)
#             data["email"] = user.email
#             data["first_name"] = user.first_name
#             data["last_name"] = user.last_name
#             return data

#         raise serializers.ValidationError('Both "email" and "password" are required.')


# class UserRegistrationSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(required=True)
#     last_name = serializers.CharField(required=False)
#     mobile_number = serializers.CharField(required=True)

#     def custom_signup(self, request, user):
#         user.first_name = self.validated_data.get("first_name", "")
#         user.last_name = self.validated_data.get("last_name", "")
#         user.mobile_number = self.validated_data.get("mobile_number", "")
#         user.save()
#         return user

#     class Meta:
#         model = User
#         fields = (
#             "email",
#             "first_name",
#             "last_name",
#             "mobile_number",
#             "is_active",
#             "date_joined",
#         )


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = (
#             "email",
#             "first_name",
#             "last_name",
#             "mobile_number",
#             "is_active",
#             "date_joined",
#         )


# class CustomerSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)
#     addresses = serializers.StringRelatedField(many=True, read_only=True)

#     class Meta:
#         model = Customer
#         fields = "__all__"


# class StaffSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True)

#     class Meta:
#         model = Staff
#         fields = "__all__"


# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = "__all__"


# class AddressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Address
#         fields = "__all__"


# class OrderItemSerializer(serializers.ModelSerializer):
#     product = ProductSerializer(read_only=True)

#     class Meta:
#         model = OrderItem
#         fields = ["product", "quantity"]


# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True, read_only=True)
#     customer = CustomerSerializer(read_only=True)

#     class Meta:
#         model = Order
#         fields = [
#             "order_id",
#             "customer",
#             "date",
#             "time",
#             "expected_shipping_time",
#             "order_items",
#         ]


# class CartItemSerializer(serializers.ModelSerializer):
#     product = ProductSerializer(read_only=True)

#     class Meta:
#         model = CartItem
#         fields = ["product", "quantity", "added_at"]


# class CartSerializer(serializers.ModelSerializer):
#     customer = CustomerSerializer(read_only=True)
#     items = CartItemSerializer(many=True, read_only=True)

#     class Meta:
#         model = Cart
#         fields = ["customer", "created_at", "items"]
