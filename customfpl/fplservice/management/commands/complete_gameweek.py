""" 
Usage: 
python manage.py complete_gameweek --settings=customfpl.settings.prod 20 true 
python manage.py complete_gameweek --settings=customfpl.settings.develop 2
"""


from django.core.management.base import BaseCommand, CommandError

from antifpl.lib import Antifpl
from antifpl.models import PointsTable

    
class Command(BaseCommand):
    help = "Update a desired gameweek or upto a gw"
    
    def add_arguments(self, parser):
        parser.add_argument('start_gameweek', type=int)
        parser.add_argument('end_gameweek', type=int)
    
    
    def handle(self, *args, **options):
        start_gameweek = options['gameweek']
        end_gameweek = options['recursive']
        print(f"Completing gameweeks in range {start_gameweek} - {end_gameweek}")
        for cur_gw in range(start_gameweek, end_gameweek+1):
            print(f"current gw: {cur_gw}")
            antifpl = Antifpl(gw=cur_gw)
            # Delete Points data before creating new
            PointsTable.objects.filter(gw=cur_gw).delete()
            antifpl.start_gameweek()
            print("Completing gw")
            antifpl.complete_gameweek()
            
            
            
            
            
