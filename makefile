first_run:
	@echo "Hello world!"
	cp .env.example app/.env
	cp .env.example postgres_to_es/.env
	docker-compose up --build -d
	docker-compose run django python app/manage.py migrate
	cat pg/movies_db_dump.sql | docker-compose exec -T pg_db psql -U app -d movies_database
	docker-compose run django python app/manage.py createsuperuser --noinput --username admin --email example@example.com

run:
	docker-compose up --build -d

stop:
	docker-compose down
