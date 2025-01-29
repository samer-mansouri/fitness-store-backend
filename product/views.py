import stripe
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer, OrderItemSerializer
from rest_framework.permissions import AllowAny
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters


stripe.api_key = settings.STRIPE_SECRET_KEY
frontend_url = settings.FRONTEND_URL

class ProductListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# List Products
class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

# Create a Product
class ProductCreateView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Retrieve a Product
class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Update a Product
class ProductUpdateView(UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# Delete a Product
class ProductDeleteView(DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class PaginatedAndSearchProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at']
    pagination_class = ProductListPagination


class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Require authentication

    def post(self, request):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        print(request.data)
        if serializer.is_valid():
            order = serializer.save()

            ##populate or
            line_items = []
            for item in order.items.all():
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': item.product.name},
                        'unit_amount': int(item.product.price * 100),
                    },
                    'quantity': item.quantity,
                })

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{frontend_url}/payment-success/?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{frontend_url}/cart/",
            )

            order.stripe_session_id = checkout_session.id
            order.save()

            return Response({"sessionId": checkout_session.id}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckoutSpecificOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Require authentication

    def post(self, request):
        order_id = request.data.get("order_id")
        order = get_object_or_404(Order, id=order_id, user=request.user)

        line_items = []
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': item.product.name},
                    'unit_amount': int(item.product.price * 100),
                },
                'quantity': item.quantity,
            })

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f"{frontend_url}/payment-success/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/cart/",
        )

        order.stripe_session_id = checkout_session.id
        order.save()

        return Response({"sessionId": checkout_session.id}, status=status.HTTP_201_CREATED)

class PaymentSuccessView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Require authentication

    def post(self, request):
        session_id = request.data.get("session_id")
        order = get_object_or_404(Order, stripe_session_id=session_id, user=request.user)
        order.paid = True
        order.save()
        return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)
    
class UserOrdersView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)