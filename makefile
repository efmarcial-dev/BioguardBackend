.PHONY: up down build logs shell migrate makemigrations seed superuser reset-db
freeze:
	pip freeze > requirements.txt
local-up:
	docker-compose up
local-build:
	docker-compose up --build
local-down:
	docker-compose down
local-log:
	docker-compose logs -f
local-shell:
	docker-compose exec web python manage.py shell
local-makemigrations:
	docker-compose exec web python manage.py makemigrations
local-migrate:
	docker-compose exec web python manage.py migrate