from rest_framework import serializers
from .models import Customer, Product, Transaction

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

# Serializer for recommendation response
class RecommendationSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    purchase_probability_7d = serializers.FloatField()
    purchase_probability_14d = serializers.FloatField()
    recommended_quantity = serializers.FloatField()
    surplus_flag = serializers.BooleanField()