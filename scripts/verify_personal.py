import sys
import os

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.base_datos import GestorDB

def verify_personal():
    db = GestorDB()
    conn = db._conectar()
    try:
        cursor = conn.execute("SELECT * FROM personal")
        rows = cursor.fetchall()
        print(f"Total records in 'personal' table: {len(rows)}")
        print("-" * 40)
        print(f"{'ID':<5} {'Nombre':<40} {'Puesto':<30}")
        print("-" * 40)
        for row in rows:
            print(f"{row['id']:<5} {row['nombre']:<40} {row['puesto']:<30}")
        
        expected_count = 32
        if len(rows) == expected_count:
            print(f"\nSUCCESS: Found {len(rows)} records, matching expectation.")
        else:
            print(f"\nWARNING: Found {len(rows)} records, but expected {expected_count}.")
            
    except Exception as e:
        print(f"Error querying 'personal' table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_personal()
