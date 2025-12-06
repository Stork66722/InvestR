from django.utils import timezone
from datetime import time
from .models import MarketSchedule

def is_market_open():
    """Check if market is open right now"""
    now = timezone.now()
    current_time = now.time()
    current_weekday = now.weekday()  # 0=Monday, 6=Sunday
    
    try:
        # Get the market schedule from database
        schedule = MarketSchedule.objects.first()
        
        if not schedule:
            return False, "Market schedule not configured"
        
        # REMOVED HARDCODED WEEKEND CHECK
        # Weekend trading is now allowed for 24/7 demo operation , add back in the future. 
        #if current_weekday >= 5:
        #      return False, "Market is closed on weekends"
        
        # for holiday, can be added later
        #if schedule.Holiday:
        #    return False, "Market is closed for holiday"
        
        # Check if admin manually closed the market
        if schedule.Status.upper() == 'CLOSED': 
            return False, "Market is currently closed"
        
        market_open = time(schedule.OpenHour, schedule.OpenMinute)
        market_close = time(schedule.CloseHour, schedule.CloseMinute)
        
        if current_time < market_open:
            return False, f"Market opens at {market_open.strftime('%I:%M %p')}"
        
        if current_time > market_close:
            return False, f"Market closed at {market_close.strftime('%I:%M %p')}"
        
        return True, "Market is open"
        
    except Exception as e:
        return False, f"Error checking market hours: {str(e)}"


def get_market_status():
    """Get market status info for display on frontend pages"""
    is_open, message = is_market_open()
    
    try:
        schedule = MarketSchedule.objects.first()
        if schedule:
            return {
                'is_open': is_open,
                'message': message,
                'open_time': f"{schedule.OpenHour:02d}:{schedule.OpenMinute:02d}",
                'close_time': f"{schedule.CloseHour:02d}:{schedule.CloseMinute:02d}",
                'status': schedule.Status,
                'is_holiday': schedule.Holiday
            }
        else:
            return {
                'is_open': False,
                'message': 'Market schedule not configured',
                'open_time': None,
                'close_time': None,
                'status': 'UNKNOWN',
                'is_holiday': False
            }
    except Exception as e:
        return {
            'is_open': False,
            'message': f'Error: {str(e)}',
            'open_time': None,
            'close_time': None,
            'status': 'ERROR',
            'is_holiday': False
        }