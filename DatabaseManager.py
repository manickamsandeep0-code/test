import configparser
import hashlib
import mysql.connector
from mysql.connector import Error
from datetime import date

class DatabaseManager:
    def __init__(self):
        self.url = None
        self.user = None
        self.password = None
        self.load_configuration()

    def load_configuration(self):
        config = configparser.ConfigParser()
        try:
            config.read('config.properties')
            self.url = config['DATABASE']['url']
            self.user = config['DATABASE']['user']
            self.password = config['DATABASE']['password']
            print("Database configuration loaded successfully.")
        except Exception as e:
            print(f"Error loading config.properties: {e}")
            self.url = "jdbc:mysql://localhost:3306/mydb"
            self.user = "root"
            self.password = ""

    def get_url(self):
        return self.url

    def set_url(self, url):
        self.url = url

    def get_user(self):
        return self.user

    def set_user(self, user):
        self.user = user

    def get_password(self):
        return self.password

    def set_password(self, password):
        self.password = password

    def get_connection(self):
        try:
            conn = mysql.connector.connect(host=self.url, user=self.user, password=self.password)
            return conn
        except Error as e:
            print(f"Database connection error: {e}")
            return None

    def log_habit(self, habit_id, habit_date, completed):
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                check_sql = "SELECT id FROM habit_logs WHERE habit_id = %s AND date = %s"
                cursor.execute(check_sql, (habit_id, habit_date))
                if cursor.fetchone():
                    update_sql = "UPDATE habit_logs SET completed = %s WHERE habit_id = %s AND date = %s"
                    cursor.execute(update_sql, (completed, habit_id, habit_date))
                else:
                    insert_sql = "INSERT INTO habit_logs (habit_id, date, completed) VALUES (%s, %s, %s)"
                    cursor.execute(insert_sql, (habit_id, habit_date, completed))
                conn.commit()
            except Error as e:
                print(f"Error logging habit: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    def delete_habit_log(self, habit_id, habit_date):
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                delete_sql = "DELETE FROM habit_logs WHERE habit_id = %s AND date = %s"
                cursor.execute(delete_sql, (habit_id, habit_date))
                conn.commit()
            except Error as e:
                print(f"Error deleting habit log: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    def get_logs_for_habit(self, habit_id):
        logs = {}
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                sql = "SELECT date, completed FROM habit_logs WHERE habit_id = %s"
                cursor.execute(sql, (habit_id,))
                records = cursor.fetchall()
                for record in records:
                    logs[record[0]] = record[1]
            except Error as e:
                print(f"Error retrieving logs: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        return logs

    def hash_password(self, password):
        try:
            return hashlib.sha256(password.encode()).hexdigest()
        except Exception as e:
            print(f"Error hashing password: {e}")
            return None

    def register_user(self, name, username, email, password):
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                check_sql = "SELECT id FROM users WHERE username = %s"
                cursor.execute(check_sql, (username,))
                if cursor.fetchone():
                    print("Username already exists!")
                    return -1
                insert_sql = "INSERT INTO users (name, username, email, password_hash) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_sql, (name, username, email, self.hash_password(password)))
                conn.commit()
                return cursor.lastrowid
            except Error as e:
                print(f"Error registering user: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        return -1

    def login_user(self, username, password):
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                sql = "SELECT id, name, username, email, password_hash FROM users WHERE username = %s"
                cursor.execute(sql, (username,))
                record = cursor.fetchone()
                if record:
                    stored_hash = record[4]
                    input_hash = self.hash_password(password)
                    if stored_hash == input_hash:
                        return {
                            'id': record[0],
                            'name': record[1],
                            'username': record[2],
                            'email': record[3]
                        }
                    else:
                        print("Invalid password!")
                else:
                    print("User not found!")
            except Error as e:
                print(f"Error during login: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        return None

    def add_habit_for_user(self, habit_name, user_id):
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                insert_sql = "INSERT INTO habits (name, user_id) VALUES (%s, %s)"
                cursor.execute(insert_sql, (habit_name, user_id))
                conn.commit()
                return cursor.lastrowid
            except Error as e:
                print(f"Error adding habit: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        return -1

    def get_habits_for_user(self, user_id):
        habits = []
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                sql = "SELECT id, name FROM habits WHERE user_id = %s ORDER BY name"
                cursor.execute(sql, (user_id,))
                records = cursor.fetchall()
                for record in records:
                    habits.append({
                        'id': record[0],
                        'name': record[1]
                    })
            except Error as e:
                print(f"Error retrieving habits: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        return habits