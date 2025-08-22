# Preparing for new season
- Delete the jsondata files 
- Update anti league code in utils.url_endpoints.py

## Remove the old db and init new db
```sh
python manage.py makemigrations --settings=customfpl.settings.prod
python manage.py migrate --settings=customfpl.settings.prod
```

### Create superuser with same creds as last year
```sh
python manage.py createsuperuser --settings=customfpl.settings.prod
```

### Create fixtures - Remove jsondata/fixtures.json
```sh
python manage.py add_update_fixtures --settings=customfpl.settings.prod
```

### Add new EPL teams
```sh
python manage.py add_new_teams --settings=customfpl.settings.prod
```


### Add new entries for postions 
```sh
python manage.py shell --settings=customfpl.settings.prod
```
Inside of a session 

```sh
from fplservice.models import Position
gk = Position(id=1, name="Goalkeeper", squad_max_play=1, squad_min_play=1, squad_max_select=2)
gk.save()
df = Position(id=2, name="Defender", squad_max_play=5, squad_min_play=3, squad_max_select=5)
df.save()
mid = Position(id=3, name="Midfielder", squad_max_play=5, squad_min_play=2, squad_max_select=5)
mid.save()
fwd = Position(id=4, name="Forward", squad_max_play=3, squad_min_play=1, squad_max_select=3)
fwd.save()
mgr = Position(id=5, name="Manager", squad_max_play=1, squad_min_play=0, squad_max_select=1)
mgr.save()
exit()
```


### Add new footballers
```sh
python manage.py add_new_footballers --settings=customfpl.settings.prod
```

### Add new entries to anti 
```sh
python manage.py add_new_entries_to_anti --settings=customfpl.settings.prod
```

### Initialize anti points table
```sh
python manage.py initialize_anti_points_table --settings=customfpl.settings.prod
```

### Complete gameweeks in range
```sh
python manage.py complete_gameweek --settings=customfpl.settings.prod 20 24 # completes all gw in this range
```

### Run the server and validate
```sh
python manage.py runserver --settings=customfpl.settings.prod
```
