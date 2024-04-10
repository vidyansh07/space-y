from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # Import for authentication
from rest_framework.authtoken.models import Token  # Import for token authentication
from django.contrib.auth.hashers import make_password  # Import for password hashing
from .models import User, Product, Customer, Bill, BillItem
from .serializers import UserSerializer, ProductSerializer, CustomerSerializer, BillSerializer
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.authtoken.models import Token  # Import for token authentication
from django.contrib.auth import authenticate  # Import for authentication

class UserLoginView(APIView):
    @extend_schema(
        summary="User Login",
        request={"type": "object", "properties": {"username": {"type": "string"}, "password": {"type": "string"}}},
        responses={200: {"type": "object", "properties": {"token": {"type": "string"}}}, 401: {"type": "object", "properties": {"error": {"type": "string"}}}},
    )
    def post(self, request):
        """
        Authenticate user and generate token.
        """
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=401)

class UserLogoutView(APIView):
    @extend_schema(
        summary="User Logout",
        responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}},
    )
    def post(self, request):
        """
        Logout user and delete token.
        """
        user = request.user
        token, _ = Token.objects.get_or_create(user=user)
        token.delete()
        return Response({'message': 'Successfully logged out'})
class ProductListCreateView(APIView):
    # Add authentication permission class (IsAuthenticated) for protected access
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all products or create a new one",
        parameters=[OpenApiParameter(name='Authorization', location='header')],
        responses=ProductSerializer(many=True),
    )
    def get(self, request):
        """
        Retrieve a list of all products.
        """
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create a new product",
        parameters=[OpenApiParameter(name='Authorization', location='header')],
        request=ProductSerializer,
        responses=ProductSerializer,
    )
    def post(self, request):
        """
        Create a new product.
        """
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ProductRetrieveUpdateDeleteView(APIView):
    # Add authentication permission class (IsAuthenticated) for protected access
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({'error': 'Product not found'}, status=404)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({'error': 'Product not found'}, status=404)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({'error': 'Product not found'}, status=404)
        product.delete()
        return Response({'message': 'Product deleted successfully'})

class CustomerListCreateView(APIView):
    # Add authentication permission class (IsAuthenticated) for protected access
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all customers or create a new one",
        parameters=[OpenApiParameter(name='Authorization', location='header')],
        responses=CustomerSerializer(many=True),
    )
    def get(self, request):
        """
        Retrieve a list of all customers.
        """
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create a new customer",
        parameters=[OpenApiParameter(name='Authorization', location='header')],
        request=CustomerSerializer,
        responses=CustomerSerializer,
    )
    def post(self, request):
        """
        Create a new customer.
        """
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class CustomerRetrieveUpdateDeleteView(APIView):
    # Add authentication permission class (IsAuthenticated) for protected access
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve a customer details",
        parameters=[OpenApiParameter(name='Authorization', location='header')],
        responses=CustomerSerializer,
    )
    def get(self, request, pk):
        """
        Retrieve details of a customer.
        """
        customer = self.get_object(pk)
        if not customer:
            return Response({'error': 'Customer not found'}, status=404)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    @extend_schema(
        summary="Update a customer",
        parameters=[OpenApiParameter(name='Authorization', location='header')],
        request=CustomerSerializer,
        responses=CustomerSerializer,
    )
    def put(self, request, pk):
        """
        Update details of a customer.
        """
        customer = self.get_object(pk)
        if not customer:
            return Response({'error': 'Customer not found'}, status=404)
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @extend_schema(
        summary="Delete a customer",
        parameters=[OpenApiParameter(name='Authorization', location='header')],
        responses={204: None},
    )
    def delete(self, request, pk):
        """
        Delete a customer.
        """
        customer = self.get_object(pk)
        if not customer:
            return Response({'error': 'Customer not found'}, status=404)
        customer.delete()
        return Response(status=204)

class BillCreateView(APIView):
    permission_classes = [IsAuthenticated]  # Require authentication

    @extend_schema(
        summary="Create a new bill",
        parameters=[OpenApiParameter(name='Authorization', location='header')],
        request=BillSerializer,
        responses=BillSerializer,
    )

    def post(self, request):
        # Extract and validate bill data (including items)
        customer_id = request.data.get('customer', None)
        items_data = request.data.get('items', [])
        total_amount = request.data.get('total_amount', None)

        if not items_data or not total_amount:
            return Response({'error': 'Missing required fields'}, status=400)

        customer = None
        if customer_id:
            try:
                customer = Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                return Response({'error': 'Invalid customer ID'}, status=400)

        employee = request.user  # Get authenticated user

        bill = Bill.objects.create(customer=customer, employee=employee, total_amount=total_amount)

        for item_data in items_data:
            product_id = item_data.get('product', None)
            quantity = item_data.get('quantity', None)

            if not product_id or not quantity:
                return Response({'error': 'Invalid item data'}, status=400)

            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Invalid product ID'}, status=400)

            BillItem.objects.create(bill=bill, product=product, quantity=quantity)

        serializer = BillSerializer(bill)
        return Response(serializer.data, status=201)

class BillRetrieveUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve a bill details",
        parameters=[OpenApiParameter(name='Authorization', location='header')],
        responses=BillSerializer,
    )
    def get(self, request, pk):
        """
        Retrieve details of a bill.
        """
        bill = self.get_object(pk)
        if not bill:
            return Response({'error': 'Bill not found'}, status=404)
        serializer = BillSerializer(bill)
        return Response(serializer.data)

    @extend_schema(
        summary="Update a bill",
        parameters=[OpenApiParameter(name='Authorization', location='header')],
        request=BillSerializer,
        responses=BillSerializer,
    )
    def put(self, request, pk):
        """
        Update details of a bill.
        """
        bill = self.get_object(pk)
        if not bill:
            return Response({'error': 'Bill not found'}, status=404)
        serializer = BillSerializer(bill, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @extend_schema(
        summary="Delete a bill",
        parameters=[OpenApiParameter(name='Authorization', location='header')],
        responses={204: None},
    )
    def delete(self, request, pk):
        """
        Delete a bill.
        """
        bill = self.get_object(pk)
        if not bill:
            return Response({'error': 'Bill not found'}, status=404)
        bill.delete()
        return Response(status=204)
