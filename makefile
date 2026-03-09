.PHONY: run migrations migrate test format lint check superuser shell

run:
	python manage.py runserver

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

test:
	docker-compose -f docker-compose.local.yml exec django sh resources/scripts/test.sh

format:
	bash resources/scripts/code_formatting.sh


superuser:
	python manage.py createsuperuser

shell:
	python manage.py shell