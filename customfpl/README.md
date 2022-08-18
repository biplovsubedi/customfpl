# Preparing for new season

Update anti league code in utils.url_endpoints.py

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
```


### Add new footballers
```sh
python manage.py add_new_footballers --settings=customfpl.settings.prod
```

### Add new entries to anti 
```sh
python manage.py add_new_entries_to_anti --settings=customfpl.settings.prod
```

### Initialize anit points table
```sh
python manage.py initialize_anti_points_table --settings=customfpl.settings.prod
```

