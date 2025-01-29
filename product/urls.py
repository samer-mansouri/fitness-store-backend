
from django.urls import path
from .views import ProductListView, ProductCreateView, ProductDetailView, ProductUpdateView, ProductDeleteView, CreateCheckoutSessionView, PaymentSuccessView, UserOrdersView, CheckoutSpecificOrderView

app_name = 'product'
urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),  
    path('create/', ProductCreateView.as_view(), name='product-create'),  
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),  
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),  
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),  
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('payment-success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('user-orders/', UserOrdersView.as_view(), name='user_orders'),  # New endpoint to get user orders
    path('checkout-specific-order/', CheckoutSpecificOrderView.as_view(), name='checkout_specific_order'),  # New endpoint to checkout a specific order
]