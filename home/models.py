from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from django.core.validators import MinValueValidator
from datetime import timedelta
import json
from django.db import connection
import uuid


def shipping_default():
    return timezone.now().date() + timedelta(days=2)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            raise ValueError("The Password field must be set.")
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(primary_key=True, unique=True)
    first_name = models.CharField(max_length=256, null=False, blank=False)
    last_name = models.CharField(max_length=256, null=True, blank=True)
    mobile_number = models.CharField(
        max_length=15, unique=True, null=False, blank=False
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "mobile_number"]

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Customer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        primary_key=True,
    )
    profile_picture = models.ImageField(
        upload_to="customer/profile/",
        blank=True,
        null=True,
        default="default/Profile.png",
    )
    loyalty_points = models.IntegerField(default=0)

    def __str__(self):
        return f"Customer: {self.user.email}"


class Staff(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="staff_profile", primary_key=True
    )
    department = models.CharField(max_length=256)
    salary = models.IntegerField()

    def __str__(self):
        return f"Staff: {self.user.email} - {self.department}"


class Product(models.Model):
    unique_id = models.CharField(max_length=50, primary_key=True)
    name = models.TextField()
    brand = models.CharField(max_length=255, null=True, blank=True, default="Havells")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_category = models.JSONField(null=True, blank=True, default=list)
    product_category_string = models.TextField(default="")
    description = models.TextField(default="")
    image = models.JSONField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True, default=50)
    product_rating = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True, default=4.5
    )

    def __str__(self):
        return f"{self.unique_id} - {self.name}"

    def save(self, *args, **kwargs):
        if self.product_category and isinstance(self.product_category, list):
            self.product_category = json.dumps(self.product_category)
        super().save(*args, **kwargs)

    def get_product_category_list(self):
        if self.product_category:
            return json.loads(self.product_category)
        return []

    def update_search_index(self):
        """Updates the FTS table with the latest product data"""
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO product_search (rowid, unique_id, name, description, product_category_string) 
                VALUES (?, ?, ?, ?, ?) 
                ON CONFLICT(unique_id) DO UPDATE 
                SET name=excluded.name, description=excluded.description, product_category_string=excluded.product_category_string
            """,
                [
                    self.pk,
                    self.unique_id,
                    self.name,
                    self.description,
                    self.product_category_string,
                ],
            )


# Created a virtual table for product search using sqlite fts5
# CREATE VIRTUAL TABLE IF NOT EXISTS product_search USING fts5(
#     unique_id UNINDEXED,
#     name,
#     description,
#     product_category_string
# );


def create_fts_table():
    with connection.cursor() as cursor:
        cursor.executescript(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS product_search USING fts5(
                unique_id UNINDEXED, 
                name, 
                description, 
                product_category_string
            );
            
            CREATE TRIGGER IF NOT EXISTS product_ai AFTER INSERT ON home_product 
            BEGIN
                INSERT INTO product_search(rowid, unique_id, name, description, product_category_string) 
                VALUES (new.unique_id, new.unique_id, new.name, new.description, new.product_category_string);
            END;

            CREATE TRIGGER IF NOT EXISTS product_ad AFTER DELETE ON home_product 
            BEGIN
                DELETE FROM product_search WHERE unique_id = old.unique_id;
            END;

            CREATE TRIGGER IF NOT EXISTS product_au AFTER UPDATE ON home_product 
            BEGIN
                DELETE FROM product_search WHERE unique_id = old.unique_id;
                INSERT INTO product_search(rowid, unique_id, name, description, product_category_string) 
                VALUES (new.unique_id, new.unique_id, new.name, new.description, new.product_category_string);
            END;
        """
        )


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address_name = models.CharField(max_length=256, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=72, null=True, blank=True)
    state = models.CharField(max_length=72, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.address_name} - {self.city}"


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders"
    )
    order_id = models.CharField(max_length=32, primary_key=True)
    alternate_mobile_number = models.CharField(max_length=15, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    expected_shipping_time = models.DateField(default=shipping_default)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_order_id()
        super(Order, self).save(*args, **kwargs)

    def generate_order_id(self):
        while True:
            unique_id = str(uuid.uuid4().hex[:12]).upper()
            if not Order.objects.filter(order_id=unique_id).exists():
                return unique_id

    def __str__(self):
        return f"Order {self.order_id} by {self.customer.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_items"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.product.name} x {self.quantity} in {self.order.order_id}"


class Cart(models.Model):
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, related_name="cart", primary_key=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.customer.user.email}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_product"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} in {self.cart.customer.user.email}'s Cart"
