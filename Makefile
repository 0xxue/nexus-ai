.PHONY: dev test build deploy clean

dev:
	docker compose up -d db redis
	cd backend && uvicorn app.main:app --reload --port 8000

dev-all:
	docker compose up -d

test:
	cd backend && python -m pytest tests/ -v

test-cov:
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=html

build:
	docker compose build --no-cache

deploy:
	docker compose up -d --build
	@sleep 10 && make health

health:
	@curl -sf http://localhost:8000/api/v1/health && echo " ✅ API" || echo " ❌ API"

logs:
	docker compose logs -f --tail=50

clean:
	docker compose down -v

help:
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
