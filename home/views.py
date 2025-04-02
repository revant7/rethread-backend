from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from .models import Product, Customer, Address, Cart, CartItem
from . import models
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db import connection, OperationalError
from django.db.models import Q
import nltk, os
from nltk.corpus import stopwords


# Create your views here.
User = get_user_model()


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def create_customer_account(request):
    email = request.data.get("email")
    password = request.data.get("password")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name", "")
    mobile_number = request.data.get("mobile_number")
    print(email, password, first_name, last_name, mobile_number)
    if not email or not password or not first_name or not mobile_number:
        return JsonResponse(
            {
                "error": "All fields (email, password, first_name, mobile_number) are required."
            },
            status=400,
        )

    if User.objects.filter(email=email).exists():
        return JsonResponse(
            {"error": "A user with this email already exists."}, status=400
        )

    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        mobile_number=mobile_number,
    )
    customer = Customer(user=user)
    customer.save()
    Address(user=user).save()
    Cart(customer=customer).save()
    return JsonResponse(
        {
            "message": "User registered successfully.",
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "mobile_number": user.mobile_number,
        },
        status=201,
    )


# user login view


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def custom_token_obtain_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return JsonResponse(
            {"error": "Both email and password are required."}, status=400
        )

    user = authenticate(email=email, password=password)

    if not user:
        return JsonResponse({"error": "Invalid email or password."}, status=401)

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    return JsonResponse(
        {
            "refresh": str(refresh),
            "access": access_token,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
        }
    )


def fetch_products(request):

    unique_id = request.data.get("unique_id")
    name = request.data.get("name")
    brand = request.data.get("brand")
    price = request.data.get("price")
    mrp = request.data.get("mrp")
    product_category = request.data.get("product_category")
    description = request.data.get("description")
    image = request.FILES.get("image")
    quantity = request.data.get("quantity")
    product_rating = request.data.get("product_rating")
    product = Product(
        unique_id=unique_id,
        name=name,
        brand=brand,
        price=price,
        mrp=mrp,
        product_category=product_category,
        description=description,
        image=image,
        quantity=quantity,
        product_rating=product_rating,
    )
    product.save()
    return HttpResponse("Data Fetched and Saved Successfully")


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def get_products(request):
    page_no = request.GET.get("page", 1)
    products = Product.objects.all().order_by("unique_id")
    paginator = Paginator(products, 40)

    try:
        page_obj = paginator.page(page_no)
    except:
        return JsonResponse({"error": "Invalid page."}, status=400)

    products_data = [
        {
            "unique_id": product.unique_id,
            "name": product.name,
            "brand": product.brand,
            "price": product.price,
            "mrp": product.mrp,
            "product_category": product.product_category,  # Get category as a list
            "product_category_string": product.product_category_string,
            "description": product.description,
            "image": product.image,
            "quantity": product.quantity,
            "product_rating": product.product_rating,
        }
        for product in page_obj.object_list
    ]

    data = {
        "products": products_data,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
    }
    return JsonResponse(data, safe=False)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def get_product_by_id(request, unique_id):
    product = Product.objects.get(unique_id=unique_id)
    product_data = {
        "unique_id": product.unique_id,
        "name": product.name,
        "brand": product.brand,
        "price": product.price,
        "mrp": product.mrp,
        "product_category": product.product_category,  # Get category as a list
        "product_category_string": product.product_category_string,
        "description": product.description,
        "image": product.image,
        "quantity": product.quantity,
        "product_rating": product.product_rating,
    }
    return JsonResponse(product_data)


nltk.data.path.append(os.path.join(os.getcwd(), "nltk_data"))
# nltk.download("punkt", download_dir=os.path.join(os.getcwd(), "nltk_data"))
# nltk.download("punkt_tab", download_dir=os.path.join(os.getcwd(), "nltk_data"))
# nltk.download("stopwords", download_dir=os.path.join(os.getcwd(), "nltk_data"))


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def autocomplete(request):
    query = request.GET.get("q", "").lower()
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )[:5]

        stop_words = set(stopwords.words("english"))
        suggestions = []
        for product in products:
            words = nltk.word_tokenize(product.name.lower())
            filtered_words = [
                word for word in words if word.isalnum() and word not in stop_words
            ]
            suggestions.append(" ".join(filtered_words[:5]))
            # if len(filtered_words) > 3:
            #     suggestions.append(" ".join(filtered_words[:3]))
            # else:
            #     suggestions.append(" ".join(filtered_words))

        return JsonResponse(suggestions, safe=False)
    else:
        return JsonResponse([], safe=False)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def search_products(request):
    query = request.GET.get("q", "")
    page_no = int(request.GET.get("page", 1))
    if query:
        try:
            safe_query = query.strip().replace('"', '""')
            with connection.cursor() as cursor:

                sql_query = f"SELECT unique_id FROM product_search WHERE product_search MATCH '{safe_query.strip()}'"
                cursor.execute(sql_query)
                product_unique_ids = [row[0] for row in cursor.fetchall()]

            products = Product.objects.filter(unique_id__in=product_unique_ids)
        except OperationalError as e:
            if "no such table: home_product_fts" in str(e):
                return JsonResponse(
                    {"error": "FTS table not found. Ensure FTS is enabled."}, status=400
                )
            else:
                return JsonResponse({"error": str(e)}, status=500)
    else:
        products = Product.objects.all()

    paginator = Paginator(products, 40)
    page_obj = paginator.page(page_no)
    data = {
        "products": list(page_obj.object_list.values()),
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
    }
    return JsonResponse(data, safe=False)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_profile_details(request):
    user = request.user
    first_name = user.first_name
    last_name = user.last_name
    mobile_number = user.mobile_number
    date_joined = user.date_joined

    customer = Customer.objects.get(user=user)

    loyalty_points = customer.loyalty_points
    profile_picture = request.build_absolute_uri(customer.profile_picture.url)

    address_query = Address.objects.get(user=user)

    address_name = address_query.address_name
    address = address_query.address
    city = address_query.city
    state = address_query.state
    pincode = address_query.pincode

    data = {
        "email": user.email,
        "first_name": first_name,
        "last_name": last_name,
        "mobile_number": mobile_number,
        "date_joined": date_joined,
        "loyalty_points": loyalty_points,
        "profile_picture": profile_picture,
        "address": {
            "address_name": address_name,
            "address": address,
            "city": city,
            "state": state,
            "pincode": pincode,
        },
    }
    return JsonResponse(data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_address_details(request):
    user = request.user

    address_query = Address.objects.get(user=user)

    address_name = address_query.address_name
    address = address_query.address
    city = address_query.city
    state = address_query.state
    pincode = address_query.pincode

    data = {
        "address_name": address_name,
        "address": address,
        "city": city,
        "state": state,
        "pincode": pincode,
    }
    print(data)
    return JsonResponse(data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def update_address_details(request):
    user = request.user
    address_name = request.POST.get("address_name")
    address = request.POST.get("address")
    city = request.POST.get("city")
    state = request.POST.get("state")
    pincode = request.POST.get("pincode")
    print(user, address_name, address, city, state, pincode)


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_profile_details(request):
    user = models.User.objects.get(email=request.user.email)
    customer = Customer.objects.get(user=request.user)
    address = Address.objects.get(user=request.user)

    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    profile_picture = request.FILES.get("profile_picture")
    address_name = request.data.get("address_name")
    c_address = request.data.get("address")
    city = request.data.get("city")
    state = request.data.get("state")
    pincode = request.data.get("pincode")

    user.first_name = first_name
    user.last_name = last_name
    if profile_picture:
        customer.profile_picture = profile_picture
    address.address_name = address_name
    address.address = c_address
    address.city = city
    address.state = state
    address.pincode = pincode

    user.save()
    customer.save()
    address.save()

    return JsonResponse({"status": "success"})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def post_orders(request):
    order = models.Order(customer=request.user.customer_profile)
    order.save()
    order_data = request.data.get("order_data")
    for i in order_data:
        order_item = models.OrderItem(
            order=order,
            product=models.Product.objects.get(unique_id=i.get("prod_unique_id")),
            quantity=i.get("prod_quantity"),
        )
        order_item.save()
    return JsonResponse({"status": "success"})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_orders(request):
    orders = models.Order.objects.filter(customer=request.user.customer_profile)
    data = []
    for order in orders:
        order_items = models.OrderItem.objects.filter(order=order)
        temp_items = []
        for i in order_items:
            temp_items.append(
                {
                    "product_id": i.product.unique_id,
                    "product_name": i.product.name,
                    "product_price": i.product.price,
                    "product_brand": i.product.brand,
                    "product_image": i.product.image,
                    "product_category": i.product.product_category,
                    "product_quantity": i.quantity,
                }
            )
        temp = {
            "order_id": order.order_id,
            "order_date": order.date,
            "order_time": order.time,
            "order_status": order.expected_shipping_time,
            "order_items": temp_items,
        }
        data.append(temp)
    return JsonResponse(
        {"data": data},
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def add_item_to_cart(request):
    user = request.user
    customer = Customer.objects.get(user=user)
    added_item_unique_id = request.data.get("unique_id")
    quantity = request.data.get("quantity")
    product = Product.objects.get(unique_id=added_item_unique_id)
    try:
        customer_cart = Cart.objects.get(customer=customer)
    except Cart.DoesNotExist:
        Cart.objects.create(customer=customer)
        customer_cart = Cart.objects.get(customer=customer)

    CartItem.objects.create(cart=customer_cart, product=product, quantity=quantity)
    return HttpResponse("Success!")


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_cart_items(request):
    user = request.user
    customer = Customer.objects.get(user=user)
    customer_cart = Cart.objects.get(customer=customer)
    try:
        data = []
        cart_items = CartItem.objects.filter(cart=customer_cart)
        for i in cart_items:
            temp_data = {}
            prod_unique_id = i.product.unique_id
            prod_name = i.product.name
            prod_category = i.product.product_category
            prod_price = i.product.price
            prod_mrp = i.product.mrp
            prod_image = i.product.image
            quantity = i.quantity

            temp_data["prod_unique_id"] = prod_unique_id
            temp_data["prod_name"] = prod_name
            temp_data["prod_category"] = prod_category
            temp_data["prod_price"] = prod_price
            temp_data["prod_mrp"] = prod_mrp
            temp_data["prod_image"] = prod_image
            temp_data["prod_quantity"] = quantity
            data.append(temp_data)

    except CartItem.DoesNotExist:
        print("Empty")
    return JsonResponse(data, safe=False)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_cart_items_count(request):
    user = request.user
    customer = Customer.objects.get(user=user)
    customer_cart = Cart.objects.get(customer=customer)
    try:
        cart_items = CartItem.objects.filter(cart=customer_cart)
        data = {"count": len(cart_items)}

    except Exception as e:
        print(e)
        data = {"count": 0}

    return JsonResponse(data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def remove_item_from_cart(request):
    unique_id_to_delete = request.data.get("unique_id")
    user = request.user
    product = Product.objects.get(unique_id=unique_id_to_delete)
    customer = Customer.objects.get(user=user)
    cart = Cart.objects.get(customer=customer)
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    cart_item.delete()

    return HttpResponse("Deleted!")
