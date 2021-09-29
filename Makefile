include .env

.PHONY: up

up:
	docker-compose up -d

.PHONY: down

down:
	docker-compose down
	docker volume prune -f

.PHONY: logs

logs:
	docker-compose logs -f
