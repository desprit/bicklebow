SHELL := /bin/bash
.DEFAULT_GOAL := help
.PHONY: help test prepare
include configs/.${ENVIRONMENT}.env
CURRENTPATH := $(shell pwd)
PYTHONPATH := $(PYTHONPATH):$(CURRENTPATH)
PROJECT_NAME := bicklebow

test: ## Run only unit tests
	@$(eval export ENVIRONMENT=testing)
	@$(eval export PYTHONPATH=$(PYTHONPATH))
	@venv/bin/python -m coverage erase
	@venv/bin/python -m coverage run -m pytest tests/api
	@venv/bin/python -m coverage html \
		--rcfile .coveragerc \
		--directory coverage_html
	@rm -f .coverage.*

prepare: ## Create log folders
	@sudo mkdir -p /var/log/$(PROJECT_NAME)
	@sudo touch /var/log/$(PROJECT_NAME)/err.log
	@sudo touch /var/log/$(PROJECT_NAME)/out.log
	@sudo chown -R root:$(USER) /var/log/$(PROJECT_NAME)
	@sudo chmod 2775 /var/log/$(PROJECT_NAME)
	@find /var/log/$(PROJECT_NAME) -type d -exec sudo chmod 2775 {} +
	@find /var/log/$(PROJECT_NAME) -type f -exec sudo chmod 0664 {} +

help: ## This help dialog
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%-30s %s\n" "target" "help" ; \
	printf "%-30s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-30s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done