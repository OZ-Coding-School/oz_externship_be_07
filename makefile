.PHONY: run migrations migrate test format superuser shell

run:
	docker-compose -f docker-compose.local.yml exec django python manage.py runserver

migrations:
	docker-compose -f docker-compose.local.yml exec django python manage.py makemigrations

migrate:
	docker-compose -f docker-compose.local.yml exec django python manage.py migrate

test:
	docker-compose -f docker-compose.local.yml exec django sh resources/scripts/test.sh

format:
	docker-compose -f docker-compose.local.yml exec django bash resources/scripts/code_formatting.sh


superuser:
	docker-compose -f docker-compose.local.yml exec django python manage.py createsuperuser

shell:
	docker-compose -f docker-compose.local.yml exec django python manage.py shell