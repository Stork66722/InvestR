import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from decimal import Decimal, InvalidOperation
from .utils import is_market_open, get_market_status
from django.core.management import call_command
import io
import sys

from .models import BrokerageAccount, CustomUser, Transaction, Stock, Order, Trade, Position
from .serializers import (
    BrokerageAccountSerializer, TransactionSerializer, StockSerializer, 
    OrderSerializer, TradeSerializer
)
from .forms import UserRegistrationForm


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('portfolio')
    return render(request, 'landing.html')


# ViewSets for API endpoints
class BrokerageAccountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BrokerageAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BrokerageAccount.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def trade(self, request):
        # Check if market is open FIRST
        market_open, message = is_market_open()
        if not market_open:
            return Response({
                "error": f"Trading not allowed: {message}"
            }, status=400)
        
        account = self.get_queryset().first()
        if not account:
            return Response({"error": "Account not found"}, status=400)
        
        ticker = request.data.get('ticker')
        trade_type = request.data.get('type', '').upper()
        quantity = request.data.get('quantity')
        
        try:
            stock = Stock.objects.get(ticker=ticker)
            quantity = int(quantity)
        except (Stock.DoesNotExist, ValueError):
            return Response({"error": "Invalid stock or quantity"}, status=400)
        
        if quantity <= 0:
            return Response({"error": "Quantity must be positive"}, status=400)
        
        price = stock.current_price
        total = price * quantity
        
        try:
            with transaction.atomic():
                if trade_type == 'BUY':
                    return self._handle_buy(account, stock, quantity, price, total)
                elif trade_type == 'SELL':
                    return self._handle_sell(account, stock, quantity, price, total)
                else:
                    return Response({"error": "Invalid trade type"}, status=400)
        except Exception as e:
            return Response({"error": "Trade failed"}, status=500)
    
    def _handle_buy(self, account, stock, qty, price, total):
        if account.cash_balance < total:
            return Response({"error": "Insufficient funds"}, status=400)
        
        account.cash_balance -= total
        account.save()
        
        position, _ = Position.objects.get_or_create(
            account=account,
            stock=stock,
            defaults={'quantity': 0}
        )
        position.quantity += qty
        position.save()
        
        order = Order.objects.create(
            account=account,
            stock=stock,
            action='BUY',
            quantity=qty,
            status='Filled',
            executed_at=timezone.now()
        )
        
        Trade.objects.create(
            order=order,
            executed_price=price,
            executed_qty=qty
        )
        
        Transaction.objects.create(
            account=account,
            transaction_type='STOCK_TRADE',
            amount=total
        )
        try:
            create_portfolio_snapshot(account)
        except Exception as e:
            print(f"Failed to create snapshot: {e}")
    
        return Response({
            "message": f"Bought {qty} shares of {stock.ticker} at ${price}",
            "new_cash": str(account.cash_balance)
        })
    
    def _handle_sell(self, account, stock, qty, price, total):
        try:
            position = Position.objects.get(account=account, stock=stock)
        except Position.DoesNotExist:
            return Response({"error": f"You don't own {stock.ticker}"}, status=400)
        
        if position.quantity < qty:
            return Response({"error": "Not enough shares"}, status=400)
        
        account.cash_balance += total
        account.save()
        
        position.quantity -= qty
        if position.quantity == 0:
            position.delete()
        else:
            position.save()
        
        order = Order.objects.create(
            account=account,
            stock=stock,
            action='SELL',
            quantity=qty,
            status='Filled',
            executed_at=timezone.now()
        )
        
        Trade.objects.create(
            order=order,
            executed_price=price,
            executed_qty=qty
        )
        
        Transaction.objects.create(
            account=account,
            transaction_type='SELL',
            amount=total
        )
        try:
            create_portfolio_snapshot(account)
        except Exception as e:
            print(f"Failed to create snapshot: {e}")
            
        return Response({
            "message": f"Sold {qty} shares of {stock.ticker} at ${price}",
            "new_cash": str(account.cash_balance)
        })
    
    @action(detail=False, methods=['post'])
    def deposit(self, request):
        account = self.get_queryset().first()
        if not account:
            return Response({"error": "Account not found"}, status=404)
        
        amount_str = request.data.get('amount') or request.POST.get('amount')
        
        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                return Response({'error': 'Amount must be greater than $0'}, status=400)
        except (InvalidOperation, TypeError, ValueError):
            return Response({'error': 'Invalid amount'}, status=400)
        
        try:
            with transaction.atomic():
                account.cash_balance += amount
                account.save()
                
                Transaction.objects.create(
                    account=account,
                    transaction_type='DEPOSIT',
                    amount=amount
                )
                
                new_balance = account.cash_balance.quantize(Decimal('0.01'))
                
                return Response({
                    "message": f"Deposited ${amount:.2f}",
                    "new_cash": str(new_balance)
                })
        except Exception as e:
            return Response({"error": f"Deposit failed: {str(e)}"}, status=500)
    
    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        account = self.get_queryset().first()
        if not account:
            return Response({"error": "Account not found"}, status=404)
        
        amount_str = request.data.get('amount') or request.POST.get('amount')
        
        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                return Response({'error': 'Amount must be greater than $0'}, status=400)
        except (InvalidOperation, TypeError, ValueError):
            return Response({'error': 'Invalid amount'}, status=400)
        
        if account.cash_balance < amount:
            return Response({"error": "Insufficient funds"}, status=400)
        
        try:
            with transaction.atomic():
                account.cash_balance -= amount
                account.save()
                
                Transaction.objects.create(
                    account=account,
                    transaction_type='WITHDRAW',
                    amount=amount
                )
                
                new_balance = account.cash_balance.quantize(Decimal('0.01'))
                
                return Response({
                    "message": f"Withdrew ${amount:.2f}",
                    "new_cash": str(new_balance)
                })
        except Exception as e:
            return Response({"error": f"Withdrawal failed: {str(e)}"}, status=500)

class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(account__user=self.request.user).order_by('-created_at')


class TradeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TradeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Trade.objects.filter(order__account__user=self.request.user).order_by('-executed_time')


# Admin helper
def is_admin(user):
    return user.is_staff or user.is_superuser


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def admin_create_stock_api(request):
    data = {
        'name': request.data.get('company_name'),
        'ticker': request.data.get('ticker'),
        'current_price': request.data.get('current_price'),
        'float_shares': request.data.get('float_shares'),
    }
    
    serializer = StockSerializer(data=data)
    if not serializer.is_valid():
        first_error = next(iter(serializer.errors))
        error_msg = serializer.errors[first_error][0]
        return Response({"error": f"{first_error}: {error_msg}"}, status=400)
    
    try:
        price = data['current_price']
        # No manual ID needed!
        stock = serializer.save(
            initial_price=price,
            opening_price=price,
            day_high=price,
            day_low=price
        )
        
        return Response({
            "success": True,
            "message": f"Stock {stock.ticker} created",
            "ticker": stock.ticker
        }, status=201)
    except Exception as e:
        return Response({"error": f"Failed to create stock: {str(e)}"}, status=400)


# Admin views
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    return render(request, 'admin/admin_dashboard.html')


@user_passes_test(is_admin)
def admin_change_market_hours_view(request):
    return render(request, 'admin/admin_change_market_hours.html')


@user_passes_test(is_admin)
def admin_create_stock_view(request):
    return render(request, 'admin/admin_create_stock.html')


# User registration
def register_user(request):
    if request.method == 'POST':
        # Handle JSON API requests
        if 'application/json' in request.content_type:
            try:
                data = json.loads(request.body)
                username = data.get('UserName')
                email = data.get('email')
                full_name = data.get('FullName')
                role = data.get('Role', 'CUSTOMER')
                password = data.get('password')
                
                if not all([username, email, full_name, password]):
                    return JsonResponse({"error": "Missing required fields"}, status=400)
                
                with transaction.atomic():
                    CustomUser.objects.create_user(
                        UserName=username,
                        email=email,
                        FullName=full_name,
                        Role=role,
                        password=password
                    )
                    return JsonResponse({"message": f"User {username} created"}, status=201)
            
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)
        
        # Handle form submission
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                CustomUser.objects.create_user(
                    UserName=form.cleaned_data['UserName'],
                    email=form.cleaned_data['email'],
                    FullName=form.cleaned_data['FullName'],
                    Role='CUSTOMER',
                    password=form.cleaned_data['password']
                )
                messages.success(request, 'Account created! You can sign in now.')
                return redirect('sign_in')
            except Exception:
                messages.error(request, 'Username or email already exists.')
        
        return render(request, 'customer/sign_up.html', {'form': form})
    
    # GET request
    form = UserRegistrationForm()
    return render(request, 'customer/sign_up.html', {'form': form})


# Customer views
@login_required
def portfolio_view(request):
    user_account = BrokerageAccount.objects.filter(user=request.user).first()
    
    if not user_account:
        return render(request, 'customer/portfolio.html', {
            'account': None,
            'positions': [],
            'total_market_value': Decimal('0.00'),
            'total_equity': Decimal('0.00'),
            'recent_orders': [],
        })
    
    # Calculate portfolio value
    positions = Position.objects.filter(account=user_account).select_related('stock')
    total_market_value = Decimal('0.00')
    positions_with_value = []
    
    for p in positions:
        p.market_value = Decimal(p.quantity) * p.stock.current_price
        total_market_value += p.market_value
        positions_with_value.append(p)
    
    total_equity = user_account.cash_balance + total_market_value
    
    # Get recent activity - NOW WITH REAL TIMESTAMPS!
    activity = []
    
    # Get trades
    orders = Order.objects.filter(
        account=user_account
    ).select_related('stock').order_by('-created_at')[:20]
    
    for order in orders:
        trade = Trade.objects.filter(order=order).first()
        activity.append({
            'date': order.created_at,
            'type': order.action,
            'stock': order.stock.ticker,
            'quantity': order.quantity,
            'price': trade.executed_price if trade else Decimal('0.00'),
        })
    
    # Get cash transactions - NOW HAVE REAL TIMESTAMPS!
    transactions = Transaction.objects.filter(
        account=user_account,
        transaction_type__in=['DEPOSIT', 'WITHDRAW']
    ).order_by('-created_at')[:20]
    
    for txn in transactions:
        activity.append({
            'date': txn.created_at,  # Real timestamp!
            'type': txn.transaction_type,
            'stock': '-',
            'quantity': '-',
            'price': txn.amount,
        })
    
    # Sort by actual date (most recent first)
    activity.sort(key=lambda x: x['date'], reverse=True)
    
    return render(request, 'customer/portfolio.html', {
        'account': user_account,
        'positions': positions_with_value,
        'total_market_value': total_market_value,
        'total_equity': total_equity,
        'recent_orders': activity[:15],
    })


@login_required
def buy_stock_view(request):
    user_account = BrokerageAccount.objects.filter(user=request.user).first()
    stocks = Stock.objects.all().order_by('ticker')
    market_status = get_market_status()
    
    return render(request, 'customer/buy_stock.html', {
        'stocks': stocks,
        'account': user_account,
        'market_status': market_status
    })


@login_required
def sell_stock_view(request):
    user_account = BrokerageAccount.objects.filter(user=request.user).first()
    positions = Position.objects.filter(account=user_account).select_related('stock') if user_account else []
    market_status = get_market_status()
    
    return render(request, 'customer/sell_stock.html', {
        'account': user_account,
        'positions': positions,
        'market_status': market_status
    })


@login_required
def deposit_cash_view(request):
    user_account = BrokerageAccount.objects.filter(user=request.user).first()
    return render(request, 'customer/deposit_cash.html', {'account': user_account})


@login_required
def withdraw_cash_view(request):
    user_account = BrokerageAccount.objects.filter(user=request.user).first()
    return render(request, 'customer/withdraw_cash.html', {'account': user_account})


@login_required
def role_based_redirect(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
    return redirect('portfolio')


@login_required
def sign_out_user(request):
    logout(request)
    messages.success(request, 'You have been signed out successfully. Come back soon!')
    return redirect('home')


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def admin_update_market_hours(request):

    try:
        # Get the data from the request
        open_hour = int(request.data.get('open_hour'))
        open_minute = int(request.data.get('open_minute'))
        close_hour = int(request.data.get('close_hour'))
        close_minute = int(request.data.get('close_minute'))
        
        # Make sure hours are valid (0-23)
        if not (0 <= open_hour <= 23 and 0 <= close_hour <= 23):
            return Response({"error": "Hours must be between 0-23"}, status=400)
        
        # Make sure minutes are valid (0-59)
        if not (0 <= open_minute <= 59 and 0 <= close_minute <= 59):
            return Response({"error": "Minutes must be between 0-59"}, status=400)
        
        # Check that market closes after it opens
        open_total_minutes = open_hour * 60 + open_minute
        close_total_minutes = close_hour * 60 + close_minute
        
        if close_total_minutes <= open_total_minutes:
            return Response({"error": "Close time must be after open time"}, status=400)
        
        # Try to get existing schedule, or create a new one
        from .models import MarketSchedule
        schedule, created = MarketSchedule.objects.get_or_create(
            ScheduleID=1,
            defaults={
                'Status': 'OPEN',
                'OpenHour': open_hour,
                'OpenMinute': open_minute,
                'CloseHour': close_hour,
                'CloseMinute': close_minute,
                'Holiday': False
            }
        )
        
        # If schedule already exists, update it
        if not created:
            schedule.OpenHour = open_hour
            schedule.OpenMinute = open_minute
            schedule.CloseHour = close_hour
            schedule.CloseMinute = close_minute
            schedule.save()
        
        # Send success message back
        return Response({
            "success": True,
            "message": f"Market hours updated to {open_hour:02d}:{open_minute:02d} - {close_hour:02d}:{close_minute:02d}",
            "schedule": {
                "open_time": f"{open_hour:02d}:{open_minute:02d}",
                "close_time": f"{close_hour:02d}:{close_minute:02d}",
                "status": schedule.Status
            }
        }, status=200)
        
    except (ValueError, TypeError):
        return Response({"error": "Invalid input format"}, status=400)
    except Exception as e:
        return Response({"error": f"Failed to update: {str(e)}"}, status=500)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_market_status_api(request):
    status_data = get_market_status()
    return Response(status_data)

@login_required
@require_http_methods(["POST"])
def admin_generate_prices(request):
    
    if request.user.Role != 'ADMIN':
        return JsonResponse({
            'error': 'Unauthorized. Admin access required.'
        }, status=403)
    
    try:
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        call_command('generate_prices')

        sys.stdout = old_stdout
        output = buffer.getvalue()
        
        stock_count = Stock.objects.count()
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully updated prices for {stock_count} stocks',
            'details': output
        })
        
    except Exception as e:
        sys.stdout = old_stdout
        return JsonResponse({
            'error': f'Failed to generate prices: {str(e)}'
        }, status=500)
    
def create_portfolio_snapshot(account):
    """Helper to create portfolio snapshot"""
    from customer.models import PortfolioSnapshot
    from decimal import Decimal
    
    trades = Trade.objects.filter(order__account=account)
    holdings = {}
    
    for trade in trades:
        ticker = trade.order.stock.ticker
        if ticker not in holdings:
            holdings[ticker] = {'shares': 0, 'current_price': trade.order.stock.current_price}
        
        if trade.order.action == 'BUY':
            holdings[ticker]['shares'] += trade.executed_qty
        else:  # SELL
            holdings[ticker]['shares'] -= trade.executed_qty
    
    holdings_value = Decimal('0')
    for ticker, data in holdings.items():
        if data['shares'] > 0:
            holdings_value += data['shares'] * data['current_price']
    
    account.refresh_from_db()
    total_value = account.cash_balance + holdings_value
    
    snapshot = PortfolioSnapshot.objects.create(
        account=account,
        total_value=total_value,
        cash_balance=account.cash_balance,
        holdings_value=holdings_value
    )
    
    return snapshot


@login_required
def portfolio_chart_data(request):
    """API endpoint for portfolio chart data"""
    from customer.models import PortfolioSnapshot
    from datetime import datetime, timedelta
    from decimal import Decimal
    
    user = request.user
    
    try:
        account = BrokerageAccount.objects.get(user=user)
    except BrokerageAccount.DoesNotExist:
        return JsonResponse({'error': 'Account not found'}, status=404)
    
    days = int(request.GET.get('days', 30))
    start_date = datetime.now() - timedelta(days=days)
    
    snapshots = PortfolioSnapshot.objects.filter(
        account=account,
        snapshot_date__gte=start_date
    ).order_by('snapshot_date')
    
    portfolio_history = {
        'labels': [s.snapshot_date.strftime('%b %d, %H:%M') for s in snapshots],
        'values': [float(s.total_value) for s in snapshots],
        'cash': [float(s.cash_balance) for s in snapshots],
        'holdings': [float(s.holdings_value) for s in snapshots],
    }
    
    trades = Trade.objects.filter(order__account=account)
    holdings = {}
    
    for trade in trades:
        ticker = trade.order.stock.ticker
        if ticker not in holdings:
            holdings[ticker] = {
                'shares': 0,
                'total_cost': Decimal('0'),
                'current_price': trade.order.stock.current_price,
                'stock_name': trade.order.stock.name,
            }
        
        if trade.order.action == 'BUY':
            holdings[ticker]['shares'] += trade.executed_qty
            holdings[ticker]['total_cost'] += trade.executed_qty * trade.executed_price
        else:  # SELL
            holdings[ticker]['shares'] -= trade.executed_qty
            holdings[ticker]['total_cost'] -= trade.executed_qty * trade.executed_price
    
    holdings = {k: v for k, v in holdings.items() if v['shares'] > 0}
    
    stock_performance = []
    stock_allocation = []
    
    for ticker, data in holdings.items():
        current_value = data['shares'] * data['current_price']
        cost_basis = data['total_cost']
        gain_loss = current_value - cost_basis
        gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
        
        stock_performance.append({
            'ticker': ticker,
            'name': data['stock_name'],
            'shares': int(data['shares']),
            'current_value': float(current_value),
            'cost_basis': float(cost_basis),
            'gain_loss': float(gain_loss),
            'gain_loss_pct': float(gain_loss_pct),
        })
        
        stock_allocation.append({
            'ticker': ticker,
            'name': data['stock_name'],
            'value': float(current_value),
        })
    
    total_holdings_value = sum(s['value'] for s in stock_allocation)
    
    if account.cash_balance > 0:
        stock_allocation.append({
            'ticker': 'CASH',
            'name': 'Cash',
            'value': float(account.cash_balance),
        })
    
    total_portfolio_value = total_holdings_value + float(account.cash_balance)
    
    return JsonResponse({
        'portfolio_history': portfolio_history,
        'stock_performance': stock_performance,
        'stock_allocation': stock_allocation,
        'total_value': float(total_portfolio_value),
        'total_holdings': float(total_holdings_value),
        'cash_balance': float(account.cash_balance),
        'has_data': len(snapshots) > 0,
    })