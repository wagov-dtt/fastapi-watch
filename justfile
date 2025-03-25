set dotenv-load

# Choose a task to run
default:
  just --choose

# Install project tools
prereqs:
  brew bundle install
  minikube config set memory no-limit
  minikube config set cpus no-limit

# Show local/env secrets for injecting into other tools
@show-secrets:
  jq -n 'env | {CDN_HEADER, ORIGIN_HEADER, ORIGIN_BASE, ORIGIN_PATH}'

# Setup minikube
minikube:
  which k9s || just prereqs
  kubectl get nodes || minikube status || minikube start # if kube configured use that cluster, otherwise start minikube

build: minikube
  minikube image build -t ghcr.io/wagov-dtt/fastapi-watch:dev .

lint:
  uvx ruff format .

ipython:
  uvx ipython

loadtest URL:
  wrk -c 400 -d 10 {{URL}}

fastapi:
  ORIGIN_BASE=http://127.0.0.1:8000 ORIGIN_PATH=mock_auth uv run uvicorn main:app --no-access-log

traefik:
  traefik --entryPoints.web.address=:8001 --providers.http.endpoint=http://127.0.0.1:8000/traefik_dynamic_conf.json

clean:
  kubectl delete ns fastapi-watch || yes
  kubectl create ns fastapi-watch

deploy FOLDER: minikube build
  kubectl apply -k kustomize/minikube/{{FOLDER}}