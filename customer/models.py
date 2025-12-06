from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, UserName, email, FullName, Role, password=None, **extra_fields):
        if not UserName:
            raise ValueError('UserName field cannot be empty.')
        if not email:
            raise ValueError('Email is required.')
        
        user = self.model(
            UserName=UserName,
            email=self.normalize_email(email),
            FullName=FullName,
            Role=Role.upper(),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        
        # Auto-create brokerage account
        BrokerageAccount.objects.create(user=user, cash_balance=0.00)
        return user
    
    def create_superuser(self, UserName, email, FullName, Role, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(UserName, email, FullName, Role, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [('CUSTOMER', 'Customer'), ('ADMIN', 'Admin')]
    
    USERNAME_FIELD = 'UserName'
    REQUIRED_FIELDS = ['FullName', 'Role', 'email']
    
    UserID = models.BigAutoField(primary_key=True, db_column='UserID')
    FullName = models.CharField(max_length=100, blank=True, null=True, db_column='FullName')
    UserName = models.CharField(unique=True, max_length=50, db_column='UserName')
    email = models.EmailField(unique=True, max_length=100, db_column='Email')
    password = models.CharField(max_length=255, db_column='PasswordHash')
    Role = models.CharField(max_length=20, default='CUSTOMER', db_column='Role')
    last_login = models.DateTimeField('last login', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    @property
    def is_admin(self):
        return self.Role == 'ADMIN'
    
    @property
    def is_customer(self):
        return self.Role == 'CUSTOMER'
    
    class Meta:
        db_table = 'User'
    
    def __str__(self):
        return self.UserName or str(self.UserID)


class Stock(models.Model):
    StockID = models.BigAutoField(primary_key=True, db_column='StockID')
    ticker = models.CharField(max_length=10, unique=True, db_column='Ticker')
    name = models.CharField(max_length=100, db_column='CompanyName')
    initial_price = models.DecimalField(max_digits=12, decimal_places=2, db_column='InitialPrice')
    current_price = models.DecimalField(max_digits=12, decimal_places=2, db_column='CurrentPrice')
    opening_price = models.DecimalField(max_digits=12, decimal_places=2, db_column='OpeningPrice')
    day_high = models.DecimalField(max_digits=12, decimal_places=2, db_column='DayHigh')
    day_low = models.DecimalField(max_digits=12, decimal_places=2, db_column='DayLow')
    float_shares = models.BigIntegerField(db_column='FloatShares')
    
    class Meta:
        db_table = 'Stock'
    
    def __str__(self):
        return self.ticker


class BrokerageAccount(models.Model):
    AccountID = models.BigAutoField(primary_key=True, db_column='AccountID')
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='account', db_column='UserID')
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, db_column='Balance')
    
    class Meta:
        db_table = 'BrokerageAccount'


class Position(models.Model):
    PositionID = models.BigAutoField(primary_key=True, db_column='PositionID')
    account = models.ForeignKey(BrokerageAccount, on_delete=models.CASCADE, related_name='positions', db_column='AccountID')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, db_column='StockID')
    quantity = models.BigIntegerField(db_column='Quantity')
    
    class Meta:
        db_table = 'Position'
        unique_together = ('account', 'stock')


class Order(models.Model):
    ORDER_ACTIONS = [('BUY', 'Buy'), ('SELL', 'Sell')]
    
    OrderID = models.BigAutoField(primary_key=True, db_column='OrderID')
    account = models.ForeignKey(BrokerageAccount, on_delete=models.CASCADE, related_name='orders', db_column='AccountID')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, db_column='StockID')
    action = models.CharField(max_length=10, choices=ORDER_ACTIONS, db_column='Action')
    quantity = models.BigIntegerField(db_column='Quantity')
    status = models.CharField(max_length=20, db_column='Status')
    created_at = models.DateTimeField(auto_now_add=True, db_column='CreatedAt')
    executed_at = models.DateTimeField(null=True, blank=True, db_column='ExecutedAt')
    
    class Meta:
        db_table = 'Order'


class Trade(models.Model):
    TradeID = models.BigAutoField(primary_key=True, db_column='TradeID')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='trades', db_column='OrderID')
    executed_price = models.DecimalField(max_digits=12, decimal_places=2, db_column='ExecutedPrice')
    executed_qty = models.BigIntegerField(db_column='ExecutedQty')
    executed_time = models.DateTimeField(auto_now_add=True, db_column='ExecutedTime')
    
    class Meta:
        db_table = 'Trade'


class Transaction(models.Model):
    TRANSACTION_TYPES = [('DEPOSIT', 'Deposit'), ('WITHDRAW', 'Withdraw'), ('STOCK_TRADE', 'Stock Trade')]
    
    TransactionID = models.BigAutoField(primary_key=True, db_column='TransactionID')
    account = models.ForeignKey(BrokerageAccount, on_delete=models.CASCADE, related_name='transactions', db_column='AccountID')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, db_column='TransType')
    amount = models.DecimalField(max_digits=12, decimal_places=2, db_column='Amount')
    created_at = models.DateTimeField(auto_now_add=True, db_column='CreatedAt')  # NEW!
    
    class Meta:
        db_table = 'Transaction'


class PriceTick(models.Model):
    TickID = models.BigAutoField(primary_key=True, db_column='TickID')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='price_ticks', db_column='StockID')
    timestamp = models.DateTimeField(auto_now_add=True, db_column='Timestamp')
    price = models.DecimalField(max_digits=12, decimal_places=2, db_column='Price')
    
    class Meta:
        db_table = 'PriceTick'
        ordering = ['-timestamp']


class MarketSchedule(models.Model):
    ScheduleID = models.BigAutoField(primary_key=True, db_column='ScheduleID')
    Status = models.CharField(max_length=10, db_column='Status')           
    OpenHour = models.IntegerField(db_column='OpenHour')                   
    OpenMinute = models.IntegerField(db_column='OpenMinute')               
    CloseHour = models.IntegerField(db_column='CloseHour')                 
    CloseMinute = models.IntegerField(db_column='CloseMinute')             
    Holiday = models.BooleanField(default=False, db_column='Holiday')      
    
    class Meta:
        db_table = 'MarketSchedule'
    
    def __str__(self):
        return f"Market {self.Status} ({self.OpenHour}:{self.OpenMinute:02d} - {self.CloseHour}:{self.CloseMinute:02d})"