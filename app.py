import sqlite3
from time import sleep
import cv2
from ultralytics import YOLO
from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename
import pytesseract

#Initializing Tesseract for Character Recognition
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
config = r'--oem 3 --psm 6'




def detect_vehicles(video_path):
    # Loading the YOLOv8 model
    model = YOLO('models/yolov8n.pt')
    
    #Capturing the video by frames
    cap = cv2.VideoCapture(video_path)
    
    classes = [2,3,5,7]
    frame_count = 1
    
    # Looping through the video frames
    while cap.isOpened():
        success, frame = cap.read()

        #Stopping the loop at the end of video
        if not success:
            break
        
        # Running YOLOv8 inference on the frame to find the vehicles
        results = model(frame)
        
        #Getting the region of vehicles from the results
        
        boxes = results[0].boxes
        
        # annotated_frame = results[0].plot()
        
        # Looping through the bounding boxes to process each vehicle
        for i in range(len(boxes)):
            for *xyxy, conf, cls in boxes[i].data:
                if cls in classes and conf > 0.5:
                    x1, y1, x2, y2 = map(int, xyxy)
                    
                    # Finding the region of a vehicle in the frame
                    vehicle_region = frame[y1:y2, x1:x2]
                    
                    # Number plate localization from the vehicle region using Edge Detection
                    gray = cv2.cvtColor(vehicle_region, cv2.COLOR_BGR2GRAY)
                    gray = cv2.GaussianBlur(gray, (5, 5), 0)
                    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                    edges = cv2.Canny(thresh, 50, 150, apertureSize=3)
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                    thresh = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
                    
                    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                    for contour in contours:
                        # Compute the area of the contour
                        x, y, w, h = cv2.boundingRect(contour)

                        # Filter based on aspect ratio and area
                        aspect_ratio = w/float(h)
                        if aspect_ratio > 1.5 and aspect_ratio < 4 and w > 100 and h>30 :
                            plate = vehicle_region[y:y+h, x:x+w]
                            # cv2.rectangle(frame, (x+x1, y+y1), (x1+x+w, y1+y+h), (0, 0, 255), 1)
                            # cv2.imwrite(f'temp/{frame_count}_plate_{i}.jpg', plate)
                    
                            # Detecting the License number in the License Plate using Tesseract OCR
                            # gray2 = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
                            # blur2 = cv2.GaussianBlur(gray2, (3, 3), 0)
                            # thresh2 = cv2.threshold(blur2, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                            # 
                            number = pytesseract.image_to_string(plate,lang='eng', config=config).replace(" ","").replace("\n","")
                            
                            if len(number)>6:
                                print(number)
                                cv2.rectangle(frame, (x+x1, y+y1), (x1+x+w, y1+y+h), (0, 0, 255), 2)
                                break

        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break
        
        frame_count += 1

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()



app = Flask(__name__)
app.secret_key = b'Q!W@E#R$T%Y^U&I*O(P)'


@app.route('/license_plate_list')
def license_plate_list():
    # Connect to the database
    conn = sqlite3.connect('license_plates.db')
    c = conn.cursor()

    # Retrieve the license plate numbers from the database
    c.execute("SELECT * FROM license_plates")
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
    conn = sqlite3.connect('license_plates.db')
    c = conn.cursor()

    # Retrieve the license plate numbers that match the search query
    c.execute("SELECT * FROM license_plates WHERE plate_number LIKE ?", ('%' + search_query + '%',))
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