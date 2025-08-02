# Variables
BACKUP_DIR=backups
BACKUP_FILE=$(BACKUP_DIR)/backup_$(shell date +%Y%m%d_%H%M%S).sql
RESTORE_FILE ?= $(BACKUP_DIR)/backup.sql  # par défaut, sauf si défini manuellement
DB_CONTAINER=project-opa-postgres-1
DB_USER=VALDML
DB_NAME=binance_data

# Créer un dossier de backup s’il n’existe pas
backup:
	@mkdir -p $(BACKUP_DIR)
	docker exec -t $(DB_CONTAINER) pg_dump -U $(DB_USER) -d $(DB_NAME) > $(BACKUP_FILE)
	@echo "Sauvegarde terminée : $(BACKUP_FILE)"

# Restaurer à partir d’un fichier donné
restore:
	@test -f $(RESTORE_FILE) || (echo "Fichier $(RESTORE_FILE) introuvable." && exit 1)
	cat $(RESTORE_FILE) | docker exec -i $(DB_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME)
	@echo "Restauration terminée à partir de : $(RESTORE_FILE)"

