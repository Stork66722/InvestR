from decimal import Decimal, ROUND_HALF_UP
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max
from customer.models import Stock, PriceTick
import random

class Command(BaseCommand):
    help = "Update stock prices with random fluctuations"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--volatility',
            type=float,
            default=0.5,
            help='Price change percentage (default: 0.5%)'
        )
    
    def handle(self, *args, **options):
        volatility = options['volatility'] / 100
        
        stocks = Stock.objects.all()
        if not stocks:
            self.stdout.write("No stocks to update")
            return
        
        with transaction.atomic():
            # Figure out next PriceTick ID - start at 5 billion if none exist
            last_tick_id = PriceTick.objects.aggregate(Max('TickID'))['TickID__max']
            next_tick_id = (last_tick_id or 5_000_000_000) + 1
            
            ticks = []
            updated = 0
            
            for stock in stocks:
                change = Decimal(str(random.uniform(-volatility, volatility)))
                new_price = stock.current_price * (1 + change)
                
                new_price = max(new_price, Decimal("0.01"))
                new_price = new_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                
                if new_price > stock.day_high:
                    stock.day_high = new_price
                if new_price < stock.day_low:
                    stock.day_low = new_price
                
                stock.current_price = new_price
                stock.save(update_fields=['current_price', 'day_high', 'day_low'])
                
                ticks.append(PriceTick(
                    TickID=next_tick_id,  # CHANGED FROM id
                    stock=stock,
                    price=new_price
                ))
                next_tick_id += 1
                updated += 1
            
            PriceTick.objects.bulk_create(ticks)
            
            self.stdout.write(
                self.style.SUCCESS(f"Updated {updated} stocks")
            )