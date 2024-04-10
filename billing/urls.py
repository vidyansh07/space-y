from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('products/', views.ProductListCreateView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductRetrieveUpdateDeleteView.as_view(), name='product-detail'),
    path('customers/', views.CustomerListCreateView.as_view(), name='customer-list'),
    path('customers/<int:pk>/', views.CustomerRetrieveUpdateDeleteView.as_view(), name='customer-detail'),
    path('bills/', views.BillCreateView.as_view(), name='bill-create'),  # Add this line for Bill creation view
    path('bills/<int:pk>/', views.BillRetrieveUpdateDeleteView.as_view(), name='bill-detail'),
]
