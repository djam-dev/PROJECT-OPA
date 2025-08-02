BACKUP_FILE=backup.sql
DB_CONTAINER=project-opa-postgres-1
DB_USER=VALDML
DB_NAME=binance_data

backup:
	docker exec -t $(DB_CONTAINER) pg_dump -U $(DB_USER) -d $(DB_NAME) > $(BACKUP_FILE)

restore:
	cat $(BACKUP_FILE) | docker exec -i $(DB_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME)
