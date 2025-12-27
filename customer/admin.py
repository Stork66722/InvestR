from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, BrokerageAccount, Stock, Order, Trade, 
    Transaction, Position, PriceTick, MarketSchedule, PortfolioSnapshot
)

# CUSTOM USER ADMIN 
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('UserName', 'email', 'FullName', 'Role', 'is_active', 'is_staff')
    list_filter = ('Role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('UserName', 'email', 'FullName')
    ordering = ('UserName',)
    
    fieldsets = (
        (None, {'fields': ('UserName', 'password')}),
        ('Personal Info', {'fields': ('FullName', 'email')}),
        ('Permissions', {'fields': ('Role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('UserName', 'email', 'FullName', 'Role', 'password1', 'password2'),
        }),
    )

#   BROKERAGE ACCOUNT ADMIN  
@admin.register(BrokerageAccount)
class BrokerageAccountAdmin(admin.ModelAdmin):
    list_display = ('AccountID', 'user', 'cash_balance')
    search_fields = ('user__UserName', 'user__email')
    readonly_fields = ('AccountID',)

#   STOCK ADMIN  
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'name', 'current_price', 'opening_price', 'day_high', 'day_low', 'float_shares')
    search_fields = ('ticker', 'name')
    list_filter = ('ticker',)
    ordering = ('ticker',)

#   POSITION ADMIN  
@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('account', 'stock', 'quantity')
    search_fields = ('account__user__UserName', 'stock__ticker')
    list_filter = ('stock',)

#   ORDER ADMIN  
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('OrderID', 'account', 'stock', 'action', 'quantity', 'status', 'created_at')
    list_filter = ('action', 'status', 'created_at')
    search_fields = ('account__user__UserName', 'stock__ticker')
    readonly_fields = ('OrderID', 'created_at', 'executed_at')
    ordering = ('-created_at',)

#   TRADE ADMIN  
@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('TradeID', 'order', 'executed_price', 'executed_qty', 'executed_time')
    search_fields = ('order__account__user__UserName', 'order__stock__ticker')
    readonly_fields = ('TradeID', 'executed_time')
    ordering = ('-executed_time',)

#   TRANSACTION ADMIN  
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('TransactionID', 'account', 'transaction_type', 'amount', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('account__user__UserName',)
    readonly_fields = ('TransactionID', 'created_at')
    ordering = ('-created_at',)

#   PRICE TICK ADMIN  
@admin.register(PriceTick)
class PriceTickAdmin(admin.ModelAdmin):
    list_display = ('stock', 'price', 'timestamp')
    list_filter = ('stock', 'timestamp')
    search_fields = ('stock__ticker',)
    readonly_fields = ('TickID', 'timestamp')
    ordering = ('-timestamp',)

#   MARKET SCHEDULE ADMIN  
@admin.register(MarketSchedule)
class MarketScheduleAdmin(admin.ModelAdmin):
    list_display = ('ScheduleID', 'Status', 'OpenHour', 'OpenMinute', 'CloseHour', 'CloseMinute', 'Holiday')
    list_filter = ('Status', 'Holiday')

#   PORTFOLIO SNAPSHOT ADMIN  
@admin.register(PortfolioSnapshot)
class PortfolioSnapshotAdmin(admin.ModelAdmin):
    list_display = ('account', 'snapshot_date', 'total_value', 'cash_balance', 'holdings_value')
    search_fields = ('account__user__UserName',)
    readonly_fields = ('snapshot_date',)
    ordering = ('-snapshot_date',)
    list_filter = ('snapshot_date',)