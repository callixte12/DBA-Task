import psycopg2
from faker import Faker
from tqdm import tqdm
import random

def get_db_connection():
    # Get password from Kubernetes secret
    from subprocess import check_output
    password = check_output(
        "kubectl get secret postgres-cluster-postgresql -o jsonpath='{.data.postgres-password}' | base64 --decode",
        shell=True
    ).decode().strip()
    
    return psycopg2.connect(
        dbname="testdb",
        user="postgres",
        password=password,
        host="localhost",
        port="5432"
    )

def create_tables(conn):
    with conn.cursor() as cur:
        # Create departments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                location VARCHAR(100) NOT NULL
            );
        """)
        
        # Create employees table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY,
                department_id INTEGER REFERENCES departments(id),
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL,
                salary NUMERIC(10,2) NOT NULL
            );
        """)
        conn.commit()

def insert_data(conn):
    fake = Faker()
    
    # Insert departments
    with conn.cursor() as cur:
        print("Creating departments...")
        departments = []
        for _ in range(10):
            name = fake.company_suffix()
            location = fake.city()
            cur.execute(
                "INSERT INTO departments (name, location) VALUES (%s, %s) RETURNING id",
                (name, location)
            )
            departments.append(cur.fetchone()[0])
        conn.commit()
    
        # Insert employees
        print("Inserting 100,000 employees...")
        for _ in tqdm(range(100000)):
            cur.execute("""
                INSERT INTO employees (department_id, first_name, last_name, email, salary)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                random.choice(departments),
                fake.first_name(),
                fake.last_name(),
                fake.email(),
                random.uniform(30000, 120000)
            ))
        conn.commit()

def main():
    print("Starting data loading process...")
    
    # Forward the port first
    import os
    os.system("kubectl port-forward svc/postgres-cluster-postgresql-primary 5432:5432 &")
    
    # Wait a bit for port forwarding
    import time
    time.sleep(5)
    
    try:
        conn = get_db_connection()
        print("Connected to database!")
        
        create_tables(conn)
        print("Tables created successfully!")
        
        insert_data(conn)
        print("Data insertion completed!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()