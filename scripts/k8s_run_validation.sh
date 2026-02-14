#!/bin/bash
# Run db validation Job in Kubernetes.
# Usage: ./scripts/k8s_run_validation.sh [namespace]
# Requires: kubectl

set -e
NAMESPACE="${1:-db-validation}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
K8S_DIR="$ROOT_DIR/k8s"

# Delete previous job if exists (to allow re-run)
kubectl delete job db-validation-job -n "$NAMESPACE" 2>/dev/null || true

# Apply and run job
kubectl apply -f "$K8S_DIR/validation-job.yaml" -n "$NAMESPACE"

echo "Waiting for validation job..."
kubectl wait --for=condition=complete job/db-validation-job -n "$NAMESPACE" --timeout=300s 2>/dev/null || true

echo "Job logs:"
kubectl logs job/db-validation-job -n "$NAMESPACE" -c validator --tail=100
