from rest_framework import serializers
from .models import Product, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='product')

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'total_price', 'created_at', 'updated_at', 'product_id', 'product']


class OrderSerializer(serializers.ModelSerializer):
    
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'paid', 'created_at', 'updated_at', 'items']
        read_only_fields = ['user']


    def create(self, validated_data):
        # print('self.context:', self.context['request'].data['items'])   
        # print('validated_data:', validated_data)
        # items_data = validated_data.pop('items')
        items_data = self.context['request'].data['items']
        user = self.context['request'].user
        order = Order.objects.create(user=user, **validated_data)

        for item in items_data:
            OrderItem.objects.create(order=order, **item)

        return order