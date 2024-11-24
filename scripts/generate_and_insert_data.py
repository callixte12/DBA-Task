import psycopg2
from faker import Faker
from tqdm import tqdm
import time

fake = Faker()

def get_unique_email():
    return f"{fake.user_name()}_{int(time.time())}@{fake.domain_name()}"

def create_tables(conn):
    with conn.cursor() as cur:
        # Drop existing tables if they exist
        cur.execute("DROP TABLE IF EXISTS employees CASCADE")
        cur.execute("DROP TABLE IF EXISTS departments CASCADE")
        
        # Create departments table
        cur.execute("""
            CREATE TABLE departments (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                location VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create employees table
        cur.execute("""
            CREATE TABLE employees (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                hire_date DATE NOT NULL,
                salary NUMERIC(10,2) NOT NULL,
                department_id INTEGER REFERENCES departments(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

def generate_test_data(conn, num_departments=10, num_employees=100000):
    with conn.cursor() as cur:
        print("Generating departments...")
        departments = []
        for _ in tqdm(range(num_departments)):
            name = fake.company() + " Department"
            location = fake.city()
            cur.execute(
                "INSERT INTO departments (name, location) VALUES (%s, %s) RETURNING id",
                (name, location)
            )
            departments.append(cur.fetchone()[0])
        conn.commit()

        print(f"\nGenerating {num_employees} employees...")
        batch_size = 1000
        for i in tqdm(range(0, num_employees, batch_size)):
            values = []
            for _ in range(min(batch_size, num_employees - i)):
                values.append((
                    fake.first_name(),
                    fake.last_name(),
                    get_unique_email(),  # Using our unique email generator
                    fake.date_between(start_date='-5y'),
                    fake.random_int(min=30000, max=120000),
                    fake.random_element(departments)
                ))
            
            args_str = ','.join(cur.mogrify(
                "(%s,%s,%s,%s,%s,%s)", x).decode('utf-8') for x in values)
            cur.execute("""
                INSERT INTO employees (
                    first_name, last_name, email, hire_date, 
                    salary, department_id
                )
                VALUES """ + args_str)
            conn.commit()

def main():
    print("Connecting to database...")
    conn = psycopg2.connect(
        dbname="testdb",
        user="testuser",
        password="test123",
        host="localhost",
        port=5433
    )
    
    try:
        print("Creating tables...")
        create_tables(conn)
        print("Generating test data...")
        generate_test_data(conn)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()