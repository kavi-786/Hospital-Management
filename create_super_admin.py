from werkzeug.security import generate_password_hash
from app import app, get_db_connection

def create_super_admin():
    with app.app_context():

        username = "admin"
        name = "Super Admin"
        password = "admin123"

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check if table exists issue protection
            cursor.execute("SHOW TABLES LIKE 'users'")
            if not cursor.fetchone():
                print("❌ ERROR: 'users' table does not exist")
                return

            # Check existing admin
            cursor.execute(
                "SELECT id FROM users WHERE username=%s",
                (username,)
            )
            existing = cursor.fetchone()

            if existing:
                print("⚠️ Admin already exists")

                # update password
                cursor.execute("""
                    UPDATE users 
                    SET password_hash=%s, name=%s, role=%s
                    WHERE username=%s
                """, (hashed_password, name, "Admin", username))

                conn.commit()
                print("🔄 Admin password updated to: admin123")
                return

            # create admin
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, name)
                VALUES (%s, %s, %s, %s)
            """, (username, hashed_password, "Admin", name))

            conn.commit()
            print("✅ Super Admin created successfully!")

        except Exception as e:
            print("❌ Error occurred:", str(e))

        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    create_super_admin()