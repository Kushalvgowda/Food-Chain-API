from django.urls import path 
from . import views 
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.views import TokenBlacklistView
  
urlpatterns = [ 
    path('menu-items/', views.MenuItemView.as_view()), 
    path('menu-item/<int:pk>', views.SingleMenuItemView.as_view()),
    path('groups/manager/users', views.ManagerView.as_view()),
    path('groups/manager/users/<int:pk>', views.ManagerViewDelete.as_view()),
    path('groups/delivery-crew/users', views.DeliveryCrewView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.DeliveryCrewViewDelete.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('cart/menu-items/<int:pk>', views.ClearCartView.as_view()),
    path('orders/', views.OrderViewPost.as_view()),
    path('orders/<int:order_id>', views.OrderViewUpdate.as_view()),
    path('category/', views.CategoryView.as_view()),
    path('itemofday/', views.ItemOfDayView.as_view()),
    path('api-token-auth/', obtain_auth_token),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
] 