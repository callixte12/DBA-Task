#!/bin/bash

# Deploy main PostgreSQL cluster
echo "Deploying main PostgreSQL cluster..."
helm upgrade --install postgres-cluster bitnami/postgresql \
  -f postgres-main-values.yaml \
  --wait

# Wait for the main cluster to be ready
echo "Waiting for main cluster to be ready..."
kubectl wait --for=condition=ready pod/postgres-cluster-postgresql-0 --timeout=300s

# Deploy standalone replica
echo "Deploying standalone replica..."
helm upgrade --install postgres-replica bitnami/postgresql \
  -f postgres-replica-values.yaml \
  --wait

# Wait for the replica to be ready
echo "Waiting for replica to be ready..."
kubectl wait --for=condition=ready pod/postgres-replica-postgresql-0 --timeout=300s

# Get the service IP
echo "Getting service information..."
kubectl get svc postgres-cluster-postgresql -o wide

# Port-forward for local access
echo "Setting up port-forward..."
kubectl port-forward svc/postgres-cluster-postgresql 5432:5432 &

# Install Python requirements
echo "Installing Python requirements..."
pip install psycopg2-binary faker tqdm

# Run data generation script
echo "Running data generation script..."
python data_generator.py

echo "Setup complete!"