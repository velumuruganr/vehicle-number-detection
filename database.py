import sqlite3

def get_connection():
    try:
        conn = sqlite3.connect('vehicles.db')
        return conn
    except Exception as e:
        print("Error connecting to the database: %s" % e)


def create_table():
    
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE vehicle_numbers
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_number TEXT,
                file_path TEXT)''')
    print("Table created")
    conn.commit()
    conn.close()


def insert_vehicle_number(vehicle_number: str, file_path: str):
    
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO vehicle_numbers (vehicle_number, file_path) VALUES (?, ?)",(vehicle_number,file_path))
    except sqlite3.OperationalError:
        print("Table not found, Creating new table")
        try:
            create_table()
            c.execute("INSERT INTO vehicle_numbers (vehicle_number, file_path) VALUES (?, ?)",(vehicle_number,file_path))
        except sqlite3.Error as e:
            print("Error creating table: %s" % e)
    conn.commit()
    conn.close()


def get_vehicle_numbers():

    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM vehicle_numbers")
    except sqlite3.OperationalError:
        print("Table not found, Creating new table")
        try:
            create_table()
            c.execute("SELECT * FROM vehicle_numbers")
        except sqlite3.Error as e:
            print("Error creating table: %s" % e)
            
            
    rows = c.fetchall()
    conn.close()
    
    return rows


def get_number(vehicle_number: str):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM vehicle_numbers WHERE vehicle_number=?",(vehicle_number,))
    except sqlite3.OperationalError:
        print("Table not found, Creating new table")
        try:
            create_table()
            c.execute("SELECT * FROM vehicle_numbers WHERE vehicle_number=?",(vehicle_number,))
        except sqlite3.Error as e:
            print("Error creating table: %s" % e)
            
            
    rows = c.fetchall()
    conn.close()
    
    return rows

def search_vehicle(search_query:str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM vehicle_numbers WHERE vehicle_number LIKE ?", ('%' + search_query + '%',))
    rows = c.fetchall()
    conn.close()
    
    return rows