""" 
Usage: 
python manage.py delete_managers --settings=customfpl.settings.develop --managers
python manage.py delete_managers --settings=customfpl.settings.prod --managers
  
"""


from django.core.management.base import BaseCommand

from antifpl.lib import Antifpl
from antifpl.models import Manager
    
class Command(BaseCommand):
    help = "Update a desired gameweek or upto a gw"
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--managers",
            nargs="*",
            help="managers list",
            default=[],
            type=int,
        )
    
    
    def handle(self, *args, **options):
        managers = options['managers']
        for m_id in managers:
            manager = Manager.objects.get(team_id=m_id)
            try:
               manager.delete()
               print(f"deleted manager - {manager}")
            except:
                print(f"Error deleting manager - {m_id}")

