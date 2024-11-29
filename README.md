PostgreSQL Database Cluster with Replication on Kubernetes
A production-ready PostgreSQL deployment with async replication using Kubernetes and Helm.

Architecture Overview
- Main PostgreSQL cluster with load balancer
- Standalone replica with async replication
- Two related tables (employees and departments)
- 100,000 sample records
- Kubernetes deployment on Minikube

Tech Stack
- Kubernetes (Minikube)
- PostgreSQL 17.2
- Helm Charts (Bitnami)
- Python with Faker library
- Async replication

Files Structure

.
├── kubernetes/
│   ├── postgres-main-values.yaml
│   └── standalone-values.yaml
├── scripts/
│   ├── generate_and_insert_data.py
│   └── replication-setup.sql
└── README.md


Quick Start
1. Start Minikube:

minikube start --cpus 2 --memory 2048 --disk-size 20g


2. Deploy main PostgreSQL cluster:

helm install postgres-main bitnami/postgresql -f postgres-main-values.yaml


3. Deploy standalone replica:

helm install postgres-standalone bitnami/postgresql -f standalone-values.yaml


4. Generate sample data:

python scripts/generate_and_insert_data.py


5. Setup replication:

psql -f scripts/replication-setup.sql

Database Schema
- Departments table: id, name, location, created_at
- Employees table: id, first_name, last_name, email, hire_date, salary, department_id, created_at
- Foreign key relationship between employees.department_id and departments.id

Verification Steps
1. Check main cluster:

SELECT COUNT(*) FROM employees;  -- Should show 100,000
SELECT COUNT(*) FROM departments;  -- Should show 10


2. Check replication:

-- On standalone database
SELECT COUNT(*) FROM employees;  -- Should match main cluster


Resources
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Bitnami Helm Charts](https://github.com/bitnami/charts)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
