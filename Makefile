.PHONY: dev test extract validate-agent lint

dev:
	@echo "Start API on :8090 and UI on :5173 manually:"
	@echo "  cd backend && uvicorn main:app --port 8090 --reload"
	@echo "  cd frontend && npm run dev"

test:
	pytest tests/ -v

extract:
	python scripts/extract_catalog.py
	python scripts/extract_keywords.py

validate-agent:
	@python scripts/validate_against_agent.py $(TEMPLATE)

lint:
	ruff check backend/ tests/ scripts/
	black --check backend/ tests/ scripts/
