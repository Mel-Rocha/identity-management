runserver:
	python manage.py runserver 8000
test:
	pytest --verbose
coverage:
	pytest --cov=apps/users --cov-report=html
makemigrations:
	python manage.py makemigrations
migrate:
	python manage.py migrate
superuser:
	python manage.py createsuperuser
shell:
	python manage.py shell
validate-quality:
	./dev_helpers/scripts/validate_quality.sh
lint:
	pylint $$(find . -name "*.py" \
		! -path "*/migrations/*" \
		! -path "*/.venv/*" \
		! -path "*/infra/*" \
		! -path "*/__pycache__/*" \
		! -name "manage.py")
