# AIOHTTP Server Practice

## Run Dev Server
``` console
$ docker-compose up
```

## Init Database
``` console
$ docker-compose exec -T db psql -U postgres < schema.sql
```