#
# Makefile
#
# The objective of this is to provide a local execution environment that is as close to identical to the CI/CD platform
# as possible. It provides a number of targets that can be used locally by a developer to ensure that tests and builds
# behave consistently and gives the developer an increased amount of confidence that the their code is valid.
#
################################################################################################
#
SHELL  := /bin/bash
.DEFAULT_GOAL := help

################################################################################################
# Environment Variables
################################################################################################

# AWS settings
AWS_ACCOUNT_ID ?= 438954004210
AWS_REGION ?= ap-southeast-2

# Helm settings
CLUSTER_NAME ?= nasa-dev
NAMESPACE ?= or
RELEASE_NAME ?= simulation-service
HELM_CHART_VERSION ?= 0.0.1

# Environment Settings
ENVIRONMENT ?= nonprod


# workspace dependent settings
ifeq ($(shell echo $(TF_BUILD) | tr [:upper:] [:lower:]),true)
	IMAGE_NAME := $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/or/test/$(RELEASE_NAME)
ifdef IMAGE_TAG
	IMAGE_TAG := $(IMAGE_TAG)
else
	IMAGE_TAG ?= $(shell /usr/bin/jq -r '.version' pkg_info.json)
endif
else
	IMAGE_NAME := $(RELEASE_NAME)
	IMAGE_TAG := latest
endif


################################################################################################
# Usage
################################################################################################

define USAGE
The following targets are available:

  make build                # Build the image.
  make clean                # Clean the workspace.
  make deploy               # Deploy the service.
  make publish              # Publish the image.
  make security-test        # Reports the image scan findings.
  make help                 # Prints out this message.

endef
export USAGE

################################################################################################
# Common Targets
################################################################################################

# Build the image
.PHONY: build
build:
	@echo "Building $(CURDIR)"
	@docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@docker build -t $(IMAGE_NAME):latest .


# Remove containers and images
.PHONY: clean
clean: check-local-workspace
	@echo "Cleaning $(CURDIR)"
	@CONTAINERS=$(shell docker ps -a --filter ancestor=$(IMAGE_NAME) --format "{{.ID}}") && \
	if [ -n "$${CONTAINERS}" ]; then \
		docker rm $${CONTAINERS}; \
	fi
	@IMAGES=$(shell docker image ls $(IMAGE_NAME) --format "{{.ID}}") && \
	if [ -n "$${IMAGES}" ]; then \
		docker rmi $${IMAGES}; \
	fi

# Publish the image to ECR and also publish the chart to 
.PHONY: publish
publish: check-cicd-workspace docker-login
	@sudo docker push $(IMAGE_NAME)
	@sudo docker push $(IMAGE_NAME):$(IMAGE_TAG)
	@AWS_REGION=ap-southeast-2 HELM_S3_MODE=3 helm repo add or_charts s3://or-infra-manager/helm_charts/
	@AWS_REGION=ap-southeast-2 HELM_S3_MODE=3 helm s3 reindex or_charts
	@helm package ./chart
	@AWS_REGION=ap-southeast-2 HELM_S3_MODE=3 helm s3 push *.tgz or_charts


################################################################################################
# Helper Targets
################################################################################################

# Checks that it's a local development environment
.PHONY: check-cicd-workspace
check-cicd-workspace:
	@if [ -z "$(TF_BUILD)" ]; then \
		printf "\nERROR: This command is to be run in CI/CD only.\n\n"; \
		exit 1; \
	fi

# Checks that it's a local development environment
.PHONY: check-local-workspace
check-local-workspace:
	@if [ -n "$(TF_BUILD)" ]; then \
		printf "\nERROR: This command is to be run locally only.\n\n"; \
		exit 1; \
	fi

# Print out the usage information
help:
	@printf "\n$$USAGE\n\n"
	$(call generate_file,John Doe,101)

# Authenticates with a private docker registry
.PHONY: docker-login
docker-login: check-cicd-workspace
	@aws ecr get-login-password --region $(AWS_REGION) | \
	docker login --username AWS --password-stdin $(shell sed 's/\/.*//g'<<< $(IMAGE_NAME))


# Pull the image
.PHONY: pull
pull: check-cicd-workspace
	@docker pull $(IMAGE_NAME):$(IMAGE_TAG)

# Run the security test (report only)
.PHONY: security-test
security-test: check-cicd-workspace
	@echo "NOTICE: This is a work in progress and is for reporting only"
	@aws ecr wait image-scan-complete \
		--repository-name $(shell sed 's/^[^\/]*\///g' <<< $(IMAGE_NAME)) \
		--image-id imageTag=$(IMAGE_TAG) \
		--region $(AWS_REGION) && \
	aws ecr describe-image-scan-findings \
		--repository-name $(shell sed 's/^[^\/]*\///g' <<< $(IMAGE_NAME)) \
		--image-id imageTag=$(IMAGE_TAG) \
		--region $(AWS_REGION)

.PHONY: update-kubeconfig
update-kubeconfig:
	@aws sts get-caller-identity \
		--region $(AWS_REGION)
	@aws eks update-kubeconfig \
		--name $(CLUSTER_NAME) \
		--region $(AWS_REGION)
	@kubectl cluster-info

.PHONY: deploy-on-cluster
deploy-on-cluster:
	@set -euo pipefail && \
	helm install orcharts/$(RELEASE_NAME) --version HELM_CHART_VERSION  --set-string environment.client=DoT --set-string image.tag=$(IMAGE_TAG) --generate-name
