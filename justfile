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
  jq -n 'env | {CDN_HEADER, ORIGIN_HEADER, ORIGIN_FQDN, ORIGIN_PATH}'

# Setup minikube
minikube:
  which k9s || just prereqs
  kubectl get nodes || minikube status || minikube start # if kube configured use that cluster, otherwise start minikube

fastapi:
  ORIGIN_FQDN=httpbin.org ORIGIN_PATH=get uv run fastapi dev