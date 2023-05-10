import sqlite3
from time import sleep
from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename
import pytesseract

from detect_vehicles import detect_vehicles

#Initializing Tesseract for Character Recognition
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
config = r'--oem 3 --psm 6'




app = Flask(__name__)
app.secret_key = b'Q!W@E#R$T%Y^U&I*O(P)'


@app.route('/license_plate_list')
def license_plate_list():
    # Connect to the database
    conn = sqlite3.connect('vehicles.db')
    c = conn.cursor()

    # Retrieve the license plate numbers from the database
    c.execute("SELECT * FROM vehicle_numbers")
    rows = c.fetchall()

    # Close the database connection
    conn.close()

    # Render the license plate list template with the license plate data
    return render_template('license_plate_list.html', license_plates=rows)


# Define a route to search for a specific license plate number
@app.route('/license_plate_list', methods=['POST'])
def license_plate_search():
    # Get the search query from the form data
    search_query = request.form['search_query']

    # Connect to the database
    conn = sqlite3.connect('vehicles.db')
    c = conn.cursor()

    # Retrieve the license plate numbers that match the search query
    c.execute("SELECT * FROM vehicle_numbers WHERE plate_number LIKE ?", ('%' + search_query + '%',))
    rows = c.fetchall()

    # Close the database connection
    conn.close()

    # Render the search results template with the license plate data and search query
    return render_template('license_plate_list.html', license_plates=rows, search_query=search_query)


@app.route('/')
def index():
    # Render the index page
    return render_template('index.html')


@app.get('/detect')
def detect_page():
    # Render the detection loading page
    return render_template('detect.html')


@app.post('/detect')
def detect():
    # Processing the video file
    video_file = request.files['videoFile']
    video_path = f"temp/{secure_filename(video_file.filename)}"
    video_file.save(video_path)
    
    detect_vehicles(video_path)
    
    return redirect(url_for('detect_page'))
    

    
    
if __name__ == "__main__":
    # Running the application at port 5000 in debug mode
    app.run(port=5000, debug=True)