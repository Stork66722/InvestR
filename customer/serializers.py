from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import BrokerageAccount, Transaction, Stock, Position, Order, Trade, MarketSchedule

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('UserID', 'UserName', 'email', 'FullName')

class StockSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ['id', 'initial_price', 'opening_price', 'day_high', 'day_low']

class PositionSerializer(serializers.ModelSerializer):
    stock_ticker = serializers.CharField(source='stock.ticker') 

    class Meta:
        model = Position
        fields = ['id', 'stock_ticker', 'quantity']

class BrokerageAccountSerializer(serializers.ModelSerializer):
    positions = PositionSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = BrokerageAccount
        fields = ['user', 'cash_balance', 'positions']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'transaction_type', 'amount']
        
class OrderSerializer(serializers.ModelSerializer):
    stock_ticker = serializers.CharField(source='stock.ticker')
    class Meta:
        model = Order
        fields = ['id', 'account', 'stock_ticker', 'action', 'quantity', 'status', 'created_at', 'executed_at']

class TradeSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id')
    stock_ticker = serializers.CharField(source='order.stock.ticker')
    
    class Meta:
        model = Trade
        fields = ['id', 'order_id', 'stock_ticker', 'executed_price', 'executed_qty', 'executed_time']

class MarketScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketSchedule
        fields = ['schedule_id','status', 'open_hour', 'open_minute', 'close_hour', 'close_minute', 'holiday']