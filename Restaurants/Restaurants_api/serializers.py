from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from decimal import Decimal
# from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User, Group
import bleach


"""  Category  """
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


"""  Menu Item and Category  """
class MenuItemSerializer(serializers.ModelSerializer):
    def validate_price(self, value):
        if value < 2:
            raise serializers.ValidationError("price less than 2.00")
        cleaned_value = bleach.clean(str(value))   
        return Decimal(cleaned_value)
    
    class Meta:
        model = MenuItem
        fields = ['id','title', 'price', 'featured', 'category']

   

"""  Cart  """
class CartSerializer(serializers.ModelSerializer):
    menuitem = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    price = serializers.SerializerMethodField(method_name='get_total')

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("quantity less than 0")
        cleaned_value = bleach.clean(str(value))    # Sanitises the data
        return int(cleaned_value)

    class Meta:
        model = Cart
        fields = ['id','menuitem','quantity','price']

    def get_total(self, product:Cart):
            return product.unit_price * product.quantity
    
    def create(self, validated_data):
        menuitem = validated_data['menuitem']  
        # if isinstance(menuitem, str):
        #     menuitem = MenuItem.objects.get(title=menuitem)
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = validated_data['unit_price'] * validated_data['quantity']
        validated_data['menuitem'] = menuitem
        return super().create(validated_data)


    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.unit_price = instance.menuitem.price
        instance.price = instance.unit_price * instance.quantity
        instance.save()
        return instance
        

"""  Order Item  """
class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = serializers.StringRelatedField()

    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity', 'unit_price', 'total_price']




"""  Order  """
class OrderSerializer(serializers.ModelSerializer):
    orderitems = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'orderitems']



     



