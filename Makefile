include .env

.PHONY: up

up:
	docker-compose up -d
	echo Waiting for api initialize
	timeout 6
	py config_initial_data.py -p "initial_data.json" -u "localhost:3000"
	lt --port 3000 --subdomain emptio

.PHONY: down

down:
	docker-compose down
	docker volume prune -f

.PHONY: logs

logs:
	docker-compose logs -f
