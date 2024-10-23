# Database Connections

## How to connect

### Mariadb (via phpMyAdmin):
- URL: [http://localhost:2011/](http://localhost:2011/)
- Server: `MARIADB_HOST`
- Username: `MARIADB_USER`
- Password: `MARIADB_USER_PW`

### Mongodb (via Mongo-Express):
- URL: [http://localhost:2022/](http://localhost:2022/)
- Username: `ME_CONFIG_BASICAUTH_USERNAME`
- Password: `ME_CONFIG_BASICAUTH_PASSWORD`

### Qdrant (via dashboard):
- URL: [http://localhost:2003/dashboard](http://localhost:2003/dashboard)

### Couchdb (via Fauxton):
- URL: [http://localhost:2004/_utils/#](http://localhost:2004/_utils/#)
- Username: `COUCHDB_USER`
- Password: `COUCHDB_PASSWORD`

### Redis (via Redis Insight):
- URL: [http://localhost:2055/](http://localhost:2055/)
- Add Database Manually:
  - Host: `REDIS_HOST`
  - Port: `REDIS_PORT`
  - Database Alias: SDG (name does not matter)
  - Username: `REDIS_USER`
  - Password: `REDIS_USER-PW`
  - Timeout: 30
