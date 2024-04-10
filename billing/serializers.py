from rest_framework import serializers
from .models import User, Product, Customer, Bill, BillItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock')

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'name', 'phone_number')

class BillItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    price = serializers.ReadOnlyField(source='product.price')  # Use ReadOnlyField instead

    class Meta:
        model = BillItem
        fields = ('id', 'product', 'quantity', 'price')

class BillSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    employee = UserSerializer(read_only=True)
    items = BillItemSerializer(many=True)

    class Meta:
        model = Bill
        fields = ('id', 'customer', 'employee', 'created_at', 'total_amount', 'items')
