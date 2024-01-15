""" 
Usage: 
python manage.py complete_gameweek --settings=customfpl.settings.prod 1 true 
python manage.py complete_gameweek --settings=customfpl.settings.develop 2
"""


from django.core.management.base import BaseCommand, CommandError

from antifpl.lib import Antifpl
from antifpl.models import PointsTable

    
class Command(BaseCommand):
    help = "Update a desired gameweek or upto a gw"
    
    def add_arguments(self, parser):
        parser.add_argument('gameweek', type=int)
        parser.add_argument('recursive', type=bool)
    
    
    def handle(self, *args, **options):
        gameweek = options['gameweek']
        recursive = options['recursive']
        if recursive:
            return self.handle_recursive(gameweek)
        antifpl = Antifpl(gw=gameweek)
        antifpl.complete_gameweek()
        
    def handle_recursive(self, gw: int):
        print("Handling recursive calls for complete gw")
        for cur_gw in range(1, gw+1):
            print(f"current gw: {cur_gw}")
            antifpl = Antifpl(gw=cur_gw)
            # Delete Points data before creating new
            PointsTable.objects.filter(gw=cur_gw).delete()
            antifpl.start_gameweek()
            print("Completing gw")
            antifpl.complete_gameweek()
            
            
            
            
            
