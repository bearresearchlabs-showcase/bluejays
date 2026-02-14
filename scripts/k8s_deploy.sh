#!/bin/bash
# Deploy DB validation infrastructure to Kubernetes.
# Usage: ./scripts/k8s_deploy.sh [namespace]
# Requires: kubectl, KUBECONFIG or ~/.kube/config

set -e
NAMESPACE="${1:-db-validation}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
K8S_DIR="$ROOT_DIR/k8s"

echo "Deploying to namespace: $NAMESPACE"

# Create namespace if not exists
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Create secret first (required by postgres-deployment)
if ! kubectl get secret db-validation-secret -n "$NAMESPACE" 2>/dev/null; then
  echo "Creating default secret (change PG_PASSWORD in production)"
  kubectl create secret generic db-validation-secret \
    --from-literal=PG_PASSWORD=postgres \
    -n "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
fi

# Apply manifests (use kustomize if available for namespace override)
if command -v kubectl &>/dev/null && kubectl kustomize "$K8S_DIR" &>/dev/null; then
  kubectl apply -k "$K8S_DIR" -n "$NAMESPACE" 2>/dev/null || true
fi
# Fallback: apply raw manifests
for f in namespace configmap postgres-deployment; do
  if [[ -f "$K8S_DIR/${f}.yaml" ]]; then
    kubectl apply -f "$K8S_DIR/${f}.yaml" -n "$NAMESPACE"
  fi
done

# Deploy PostgreSQL
kubectl apply -f "$K8S_DIR/postgres-deployment.yaml" -n "$NAMESPACE"

echo "Waiting for PostgreSQL..."
kubectl rollout status deployment/postgres-validation -n "$NAMESPACE" --timeout=120s 2>/dev/null || true

echo "Deploy complete. Run validation: ./scripts/k8s_run_validation.sh $NAMESPACE"
