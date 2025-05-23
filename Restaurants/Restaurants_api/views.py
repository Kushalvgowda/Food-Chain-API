from .models import MenuItem, Cart, OrderItem, Order, Category
from .serializers import MenuItemSerializer, CartSerializer, OrderItemSerializer, OrderSerializer, CategorySerializer
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets, filters, serializers
from rest_framework import status
from rest_framework.decorators import api_view, APIView, permission_classes, renderer_classes, throttle_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import UserRateThrottle
# from .throttles import TenCallsperMinute
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from decimal import Decimal
from datetime import date
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi




"""  Creating Permisiions  """
class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()

class IsDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='DeliveryCrew').exists()

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.count() == 0 
    
class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.groups.filter(name='Manager').exists()))




"""  Add/View a user to Manager group by Admin  """
class ManagerView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_description="Add a user to the Manager group",
        operation_summary="Add User to Manager Group",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username'],
            properties={
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Username of the user to add to Manager group',
                    example='john_doe'
                )
            }
        ),
        responses={
            201: openapi.Response(
                description="User successfully added to Manager group",
                examples={
                    "application/json": {
                        "message": "john_doe added to Manager group."
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Admin permission required",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            ),
            404: openapi.Response(
                description="User not found",
                examples={"application/json": {"detail": "Not found."}}
            )
        },
        tags=['Manager Management'],
        security=[{'Bearer': []}]
    )
    def post(self, request):
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        manager_group, created = Group.objects.get_or_create(name='Manager')
        manager_group.user_set.add(user)
        return Response({"message": f"{username} added to Manager group."}, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_description="Get all users in the Manager group",
        operation_summary="List Manager Group Users",
        responses={
            200: openapi.Response(
                description="List of users in Manager group",
                examples={
                    "application/json": {
                        "Group": "Manager",
                        "Users": [
                            {"id": 1, "username": "john_doe", "email": "john@example.com"},
                            {"id": 2, "username": "jane_smith", "email": "jane@example.com"}
                        ]
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Admin permission required",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            ),
            404: openapi.Response(
                description="Manager group not found",
                examples={"application/json": {"detail": "Not found."}}
            )
        },
        tags=['Manager Management'],
        security=[{'Bearer': []}]
    )
    def get(self, request):
        manager_group = get_object_or_404(Group, name='Manager')
        managers = manager_group.user_set.all()
        manager_list = [{'id': manager.id, 'username': manager.username, 'email': manager.email} for manager in managers]
        return Response({'Group': 'Manager', 'Users': manager_list})
    


"""  Delete/Remove a Manager from Group """
class ManagerViewDelete(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Remove a user from the Manager group",
        operation_summary="Remove Manager",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="User ID to remove from Manager group",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="User successfully removed from Manager group",
                examples={
                    "application/json": {
                        "message": "john_doe of id 5 has been removed from Manager Group"
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Admin permission required",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            ),
            404: openapi.Response(
                description="User not found in Manager group",
                examples={"application/json": {"detail": "Not found."}}
            )
        },
        tags=['Manager Management'],
        security=[{'Bearer': []}]
    )
    def delete(self, request, pk):
        manager_group = get_object_or_404(Group, name='Manager')
        user = get_object_or_404(manager_group.user_set, id=pk)
        manager_group.user_set.remove(user)
        return Response({'message': f'{user.username} of id {user.id} has been removed from Manager Group'}, status=status.HTTP_200_OK)


"""  Add a user to Delivery crew by Manager  """
class DeliveryCrewView(APIView):
    permission_classes = [IsAdminOrManager]

    @swagger_auto_schema(
        operation_description="Add a user to the Delivery Crew group",
        operation_summary="Add User to Delivery Crew",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username'],
            properties={
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Username of the user to add to Delivery Crew',
                    example='delivery_user'
                )
            }
        ),
        responses={
            201: openapi.Response(
                description="User successfully added to Delivery Crew",
                examples={
                    "application/json": {
                        "message": "delivery_user added to Delivery Crew."
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Manager or Admin permission required",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            ),
            404: openapi.Response(
                description="User not found",
                examples={"application/json": {"detail": "Not found."}}
            )
        },
        tags=['Delivery Crew Management'],
        security=[{'Bearer': []}]
    )
    def post(self, request):
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        crew_group, created = Group.objects.get_or_create(name='DeliveryCrew')
        crew_group.user_set.add(user)
        return Response({"message": f"{username} added to Delivery Crew."}, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_description="Get all users in the Delivery Crew group",
        operation_summary="List Delivery Crew Users",
        responses={
            200: openapi.Response(
                description="List of users in Delivery Crew",
                examples={
                    "application/json": {
                        "Group": "Delivery Crews",
                        "Users": [
                            {"id": 3, "username": "crew_member1", "email": "crew1@example.com"},
                            {"id": 4, "username": "crew_member2", "email": "crew2@example.com"}
                        ]
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Manager or Admin permission required",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            ),
            404: openapi.Response(
                description="Delivery Crew group not found",
                examples={"application/json": {"detail": "Not found."}}
            )
        },
        tags=['Delivery Crew Management'],
        security=[{'Bearer': []}]
    )
    def get(self, request):
        delivery_group = get_object_or_404(Group, name='DeliveryCrew')
        delivery_crew = delivery_group.user_set.all()
        crew_list = [{'id': crews.id, 'username': crews.username, 'email': crews.email} for crews in delivery_crew]
        return Response({'Group': 'Delivery Crews', 'Users': crew_list})
    

"""  Remove a Crew from Delivery  """
class DeliveryCrewViewDelete(APIView):
    permission_classes = [IsAdminOrManager]

    @swagger_auto_schema(
        operation_description="Remove a user from the Delivery Crew group",
        operation_summary="Remove Delivery Crew Member",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="User ID to remove from Delivery Crew",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="User successfully removed from Delivery Crew",
                examples={
                    "application/json": {
                        "message": "crew_member1 of id 3 has been removed from Delivery Crew Group"
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Manager or Admin permission required",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            ),
            404: openapi.Response(
                description="User not found in Delivery Crew",
                examples={"application/json": {"detail": "Not found."}}
            )
        },
        tags=['Delivery Crew Management'],
        security=[{'Bearer': []}]
    )
    def delete(self, request, pk):
        crew_group = get_object_or_404(Group, name='DeliveryCrew')
        user = get_object_or_404(crew_group.user_set, id=pk)
        crew_group.user_set.remove(user)
        return Response({'message': f'{user.username} of id {user.id} has been removed from Delivery Crew Group'}, status=status.HTTP_200_OK)



"""  Item of the Day  """
class ItemOfDayView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdminOrManager()]
    
   
    @swagger_auto_schema(
        operation_description="Set a menu item as the featured item of the day",
        operation_summary="Set Item of the Day",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['item_id'],
            properties={
                'item_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Menu item ID to set as featured',
                    example=1
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Item successfully set as item of the day",
                examples={
                    "application/json": {
                        "message": "Burger is set as item of the day"
                    }
                }
            ),
            400: openapi.Response(
                description="Menu item ID is required",
                examples={"application/json": {"error": "Menu item ID is required"}}
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Manager or Admin permission required",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            ),
            404: openapi.Response(
                description="Menu item not found",
                examples={"application/json": {"error": "Menu item not found"}}
            )
        },
        tags=['Featured Items'],
        security=[{'Bearer': []}]
    )
    def post(self, request):
        item_id = request.data.get('item_id')     
        if not item_id:
            return Response({"error": "Menu item ID is required"}, status=status.HTTP_400_BAD_REQUEST)      
        MenuItem.objects.filter(featured=True).update(featured=False)
        
        try:
            menu_item = MenuItem.objects.get(id=item_id)
            menu_item.featured = True
            menu_item.save()
            return Response({"message": f"{menu_item.title} is set as item of the day"}, status=status.HTTP_200_OK)
        except MenuItem.DoesNotExist:
            return Response({"error": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e: # Catch other potential errors during DB interaction
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
    @swagger_auto_schema(
        operation_description="Get the current featured item of the day",
        operation_summary="Get Item of the Day",
        responses={
            200: openapi.Response(
                description="Featured item details",
                schema=MenuItemSerializer
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Manager or Admin permission required",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            ),
            404: openapi.Response(
                description="No featured item set",
                examples={"application/json": {"message": "No item of the day set"}}
            )
        },
        tags=['Featured Items'],
        security=[{'Bearer': []}]
    )
    def get(self, request):
        try:
            item = MenuItem.objects.get(featured=True)
            serializer = MenuItemSerializer(item)
            return Response(serializer.data)
        except MenuItem.DoesNotExist:
            return Response({"message": "No item of the day set"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e: # Catch other potential errors
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




"""  CRUD Categories for Admin and View Categories for users  """
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @swagger_auto_schema(
        operation_description="Get list of all categories",
        operation_summary="List Categories",
        responses={
            200: openapi.Response(
                description="List of categories",
                schema=CategorySerializer(many=True)
            )
        },
        tags=['Categories']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new category (Admin only)",
        operation_summary="Create Category",
        request_body=CategorySerializer,
        responses={
            201: openapi.Response(
                description="Category created successfully",
                schema=CategorySerializer
            ),
            400: openapi.Response(
                description="Invalid data",
                examples={"application/json": {"field": ["This field is required."]}}
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Admin permission required",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            )
        },
        tags=['Categories'],
        security=[{'Bearer': []}]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    


"""  CRUD Menu items for Admin and View Menu items for users  """
class MenuItemPagination(PageNumberPagination):
    page_size = 5  
    page_size_query_param = 'perpage'  
    max_page_size = 100  

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    pagination_class = MenuItemPagination  

    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['category', 'price']
    ordering_fields = ['price']

    @swagger_auto_schema(
        operation_description="Get list of menu items with pagination, filtering and ordering",
        operation_summary="List Menu Items", 
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('perpage', openapi.IN_QUERY, description="Items per page (max 100)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('category_slug', openapi.IN_QUERY, description="Filter by category slug", type=openapi.TYPE_STRING),
            openapi.Parameter('price', openapi.IN_QUERY, description="Filter by exact price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by price (use -price for descending)", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(
                description="Paginated list of menu items",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                ref='#/definitions/MenuItem'
                            )
                        )
                    }
                )
            )
        },
        tags=['Menu Items']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new menu item (Admin/Manager only)",
        operation_summary="Create Menu Item",
        request_body=MenuItemSerializer,
        responses={
            201: openapi.Response(
                description="Menu item created successfully",
                schema=MenuItemSerializer
            ),
            400: openapi.Response(
                description="Invalid data",
                examples={"application/json": {"field": ["This field is required."]}}
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Admin or Manager permission required",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            )
        },
        tags=['Menu Items'],
        security=[{'Bearer': []}]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        queryset = MenuItem.objects.all()
        to_price = self.request.query_params.get('price')
        category_slug = self.request.query_params.get('category_slug')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if to_price:
            queryset = queryset.filter(price=to_price)
        return queryset

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrManager()]
        return [permissions.AllowAny()]
    


"""  View Single Item  """    
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    @swagger_auto_schema(
        operation_description="Get details of a specific menu item",
        operation_summary="Get Menu Item",
        responses={
            200: openapi.Response(
                description="Menu item details",
                schema=MenuItemSerializer
            ),
            404: openapi.Response(
                description="Menu item not found",
                examples={"application/json": {"detail": "Not found."}}
            )
        },
        tags=['Menu Items']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update a menu item (Admin/Manager only)",
        operation_summary="Update Menu Item",
        request_body=MenuItemSerializer,
        responses={
            200: openapi.Response(
                description="Menu item updated successfully",
                schema=MenuItemSerializer
            ),
            400: openapi.Response(
                description="Invalid data",
                examples={"application/json": {"field": ["This field is required."]}}
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Admin or Manager permission required",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            ),
            404: openapi.Response(
                description="Menu item not found",
                examples={"application/json": {"detail": "Not found."}}
            )
        },
        tags=['Menu Items'],
        security=[{'Bearer': []}]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update a menu item (Admin/Manager only)",
        operation_summary="Partially Update Menu Item",
        request_body=MenuItemSerializer,
        responses={
            200: openapi.Response(
                description="Menu item updated successfully",
                schema=MenuItemSerializer
            ),
            400: openapi.Response(
                description="Invalid data",
                examples={"application/json": {"field": ["This field is required."]}}
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Admin or Manager permission required",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            ),
            404: openapi.Response(
                description="Menu item not found",
                examples={"application/json": {"detail": "Not found."}}
            )
        },
        tags=['Menu Items'],
        security=[{'Bearer': []}]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a menu item (Admin/Manager only)",
        operation_summary="Delete Menu Item",
        responses={
            204: openapi.Response(description="Menu item deleted successfully"),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Admin or Manager permission required",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            ),
            404: openapi.Response(
                description="Menu item not found",
                examples={"application/json": {"detail": "Not found."}}
            )
        },
        tags=['Menu Items'],
        security=[{'Bearer': []}]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_object(self):
        return get_object_or_404(MenuItem, pk=self.kwargs['pk'])
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdminOrManager()]



"""  Cart View & Post  """
class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    @swagger_auto_schema(
        operation_description="Get current user's cart items",
        operation_summary="Get Cart Items",
        responses={
            200: openapi.Response(
                description="List of cart items",
                schema=CartSerializer(many=True)
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Customer access only",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            )
        },
        tags=['Cart'],
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Add item to cart",
        operation_summary="Add to Cart",
        request_body=CartSerializer,
        responses={
            201: openapi.Response(
                description="Item added to cart",
                schema=CartSerializer
            ),
            400: openapi.Response(
                description="Invalid data",
                examples={"application/json": {"field": ["This field is required."]}}
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Customer access only",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            )
        },
        tags=['Cart'],
        security=[{'Bearer': []}]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Clear all items from user's cart",
        operation_summary="Clear Cart",
        responses={
            204: openapi.Response(description="Cart cleared successfully"),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Customer access only",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            )
        },
        tags=['Cart'],
        security=[{'Bearer': []}]
    )
    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    


"""  Clear specific item in Cart  """
class ClearCartView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    @swagger_auto_schema(
        operation_description="Remove a specific item from cart",
        operation_summary="Remove Cart Item",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Cart item ID to remove",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: openapi.Response(description="Cart item removed successfully"),
            401: openapi.Response(
                description="Authentication required",
                examples={"application/json": {"detail": "Authentication credentials were not provided."}}
            ),
            403: openapi.Response(
                description="Customer access only",
                examples={"application/json": {"detail": "You do not have permission to perform this action."}}
            ),
            404: openapi.Response(
                description="Cart item not found",
                examples={"application/json": {"detail": "Not found."}}
            )
        },
        tags=['Cart'],
        security=[{'Bearer': []}]
    )
    def delete(self, request, pk):
        cart_item = get_object_or_404(Cart, id=pk, user=request.user)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





"""  Order view for Customer, all order view for Manager, assigned view for Crew. Place order by Customer  """
class OrderViewPost(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    @swagger_auto_schema(
        operation_description="""
        Retrieve orders based on user role:
            - **Customer**: Only their own orders
            - **Manager/Admin**: All orders in the system  
            - **Delivery Crew**: Orders assigned to them
        """,        
        operation_summary="Get Order Items",
        tags=['Orders'],
        responses={
            200: openapi.Response(
                description="Successfully retrieved orders",
                schema=OrderSerializer(many=True),
                examples={
                    "application/json": {
                        "customer_orders": [
                            {
                                "id": 1,
                                "user": "john_doe",
                                "total": "29.99",
                                "date": "2024-01-15",
                                "status": "pending",
                                "delivery_crew": None,
                                "items": [
                                    {
                                        "id": 1,
                                        "menuitem": "Pizza Margherita",
                                        "quantity": 2,
                                        "unit_price": "12.99",
                                        "total_price": "25.98"
                                    }
                                ]
                            }
                        ],
                        "manager_orders": [
                            {
                                "id": 1,
                                "user": "john_doe", 
                                "total": "29.99",
                                "date": "2024-01-15",
                                "status": "pending",
                                "delivery_crew": None
                            },
                            {
                                "id": 2,
                                "user": "jane_smith",
                                "total": "45.50", 
                                "date": "2024-01-15",
                                "status": "out_for_delivery",
                                "delivery_crew": "crew_member_1"
                            }
                        ],
                        "crew_orders": [
                            {
                                "id": 2,
                                "user": "jane_smith",
                                "total": "45.50",
                                "date": "2024-01-15", 
                                "status": "out_for_delivery",
                                "delivery_crew": "crew_member_1"
                            }
                        ]
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Authentication credentials were not provided."
                        )
                    }
                )
            )
        },
        security=[{'Bearer': []}]
    )
    def get(self, request):
        if request.user.groups.filter(name='Manager').exists():
            queryset = Order.objects.all()
        elif request.user.groups.filter(name='DeliveryCrew').exists():
            queryset = Order.objects.filter(delivery_crew=request.user)
        else:
            queryset = Order.objects.filter(user=request.user)
        
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)
            
    
    @swagger_auto_schema(
        operation_summary="Place Order",
        operation_description="""
        Create a new order from cart items. 
        
        **Requirements:**
        - Only customers can place orders
        - Cart must contain items
        - Cart will be cleared after successful order creation
        
        **Process:**
        1. Validates that cart is not empty
        2. Calculates total from cart items
        3. Creates order with current date
        4. Creates order items from cart items
        5. Clears the cart
        """,
        tags=['Orders'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description="No request body needed - order created from cart items automatically"
        ),
        responses={
            201: openapi.Response(
                description="Order placed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Order placed successfully"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "message": "Order placed successfully"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request - Cart is empty",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Cart is empty"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "error": "Cart is empty"
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Authentication credentials were not provided."
                        )
                    }
                )
            ),
            403: openapi.Response(
                description="Permission denied - Only customers can place orders",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="You do not have permission to perform this action."
                        )
                    }
                )
            )
        },
        security=[{'Bearer': []}]
    )
    def post(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(item.price for item in cart_items)
        order = Order.objects.create(user=user, total=total, date=date.today())

        order_items = [
            OrderItem(order=order, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, total_price=item.price)
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()
        return Response({"message": "Order placed successfully"}, status=status.HTTP_201_CREATED)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsCustomer()]
        return [IsAuthenticated()]


"""  Order Status Update by Crew & Manager and View by Customer  """
class OrderViewUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    lookup_url_kwarg = 'order_id'
    
    def get_queryset(self):
        return Order.objects.all()
    
    def get_object(self):
        order_id = self.kwargs['order_id']
        if self.request.method == 'GET':
            if not self.request.user.groups.filter(name__in=['Manager', 'DeliveryCrew']).exists():
                return get_object_or_404(Order, id=order_id, user=self.request.user)
        return get_object_or_404(Order, id=order_id)
    
    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsDeliveryCrew()]
        elif self.request.method == 'POST':
            return [IsManager()]
        return [IsAuthenticated()]   
    
    @swagger_auto_schema(
        operation_summary="Get Order Details",
        operation_description="""
        Retrieve specific order details based on user role:
        
        - **Customer**: Can only view their own orders
        - **Manager**: Can view any order
        - **Delivery Crew**: Can view any order
        
        Returns complete order information including items and status.
        """,
        tags=['Orders'],
        manual_parameters=[
            openapi.Parameter(
                'order_id',
                openapi.IN_PATH,
                description="Order ID to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True,
                example=1
            )
        ],
        responses={
            200: openapi.Response(
                description="Order details retrieved successfully",
                schema=OrderSerializer(),
                examples={
                    "application/json": {
                        "customer_view": {
                            "id": 1,
                            "user": "john_doe",
                            "total": "29.99",
                            "date": "2024-01-15",
                            "status": False,
                            "delivery_crew": "crew_member_1",
                            "items": [
                                {
                                    "id": 1,
                                    "menuitem": "Pizza Margherita",
                                    "quantity": 2,
                                    "unit_price": "12.99",
                                    "total_price": "25.98"
                                }
                            ]
                        },
                        "manager_crew_view": {
                            "id": 1,
                            "user": "john_doe",
                            "total": "29.99",
                            "date": "2024-01-15",
                            "status": False,
                            "delivery_crew": "crew_member_1"
                        }
                    }
                }
            ),
            403: openapi.Response(
                description="Permission denied - Customer trying to view other's order",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="You do not have permission to perform this action."
                        )
                    }
                )
            ),
            404: openapi.Response(
                description="Order not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Not found."
                        )
                    }
                )
            ),
            401: openapi.Response(
                description="Authentication required",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Authentication credentials were not provided."
                        )
                    }
                )
            )
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, order_id):
        order = self.get_object()
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Mark Order as Delivered",
        operation_description="""
        Update order status to delivered by delivery crew.
        
        **Requirements:**
        - Only delivery crew members can mark orders as delivered
        - Crew member can only update orders assigned to them
        - Sets order status to True (delivered)
        
        **Business Logic:**
        1. Validates that user is delivery crew
        2. Checks if order is assigned to the requesting crew member
        3. Updates order status to delivered (True)
        """,
        tags=['Orders'],
        manual_parameters=[
            openapi.Parameter(
                'order_id',
                openapi.IN_PATH,
                description="Order ID to update",
                type=openapi.TYPE_INTEGER,
                required=True,
                example=1
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description="No request body needed for status update"
        ),
        responses={
            200: openapi.Response(
                description="Order marked as delivered successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Order marked as delivered"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "message": "Order marked as delivered"
                    }
                }
            ),
            403: openapi.Response(
                description="Permission denied - Not authorized to update this order",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="You can only update orders assigned to you"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "forbidden_crew": {
                            "error": "You can only update orders assigned to you"
                        },
                        "not_crew": {
                            "detail": "You do not have permission to perform this action."
                        }
                    }
                }
            ),
            404: openapi.Response(
                description="Order not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Not found."
                        )
                    }
                )
            ),
            401: openapi.Response(
                description="Authentication required",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Authentication credentials were not provided."
                        )
                    }
                )
            )
        },
        security=[{'Bearer': []}]
    )   
    def patch(self, request, order_id):
        order = self.get_object()
        
        if request.user.groups.filter(name='DeliveryCrew').exists() and order.delivery_crew != request.user:
            return Response({"error": "You can only update orders assigned to you"}, status=status.HTTP_403_FORBIDDEN)
            
        order.status = True
        order.save()
        return Response({"message": "Order marked as delivered"}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="Assign Delivery Crew to Order",
        operation_description="""
        Assign a delivery crew member to an order (Manager only).
        
        **Requirements:**
        - Only managers can assign delivery crew
        - Username must be provided in request body
        - User must exist in the system
        
        **Process:**
        1. Validates manager permissions
        2. Checks if provided username exists
        3. Assigns the user as delivery crew for the order
        """,
        tags=['Orders'],
        manual_parameters=[
            openapi.Parameter(
                'order_id',
                openapi.IN_PATH,
                description="Order ID to assign crew to",
                type=openapi.TYPE_INTEGER,
                required=True,
                example=1
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username'],
            properties={
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Username of delivery crew member to assign",
                    example="crew_member_1"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Order assigned successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Order assigned successfully"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "message": "Order assigned successfully"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request - Username not provided",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Username is required"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "error": "Username is required"
                    }
                }
            ),
            403: openapi.Response(
                description="Permission denied - Only managers can assign crew",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="You do not have permission to perform this action."
                        )
                    }
                )
            ),
            404: openapi.Response(
                description="User or Order not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="User not found"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "user_not_found": {
                            "error": "User not found"
                        },
                        "order_not_found": {
                            "detail": "Not found."
                        }
                    }
                }
            ),
            401: openapi.Response(
                description="Authentication required",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Authentication credentials were not provided."
                        )
                    }
                )
            )
        },
        security=[{'Bearer': []}]
    )
    def post(self, request, order_id):
        username = request.data.get('username')
        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
        order = self.get_object()
        order.delivery_crew = user
        order.save()
        return Response({"message": "Order assigned successfully"}, status=status.HTTP_200_OK)