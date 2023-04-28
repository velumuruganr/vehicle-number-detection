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
        
        # annotated_frame = results[0].plot()
        
        boxes = results[0].boxes
        
        # Looping through the bounding boxes to process each vehicle
        for i in range(len(boxes)):
            for *xyxy, conf, cls in boxes[i].data:
                if cls in classes and conf > 0.5:
                    x1, y1, x2, y2 = map(int, xyxy)
                    
                    # Finding the region of a vehicle in the frame
                    # vehicle_region = frame[y1:y2, x1:x2]
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
                    
                    # # Number plate localization from the vehicle region using Edge Detection
                    # gray = cv2.cvtColor(vehicle_region, cv2.COLOR_BGR2GRAY)
                    # gray = cv2.GaussianBlur(gray, (5, 5), 0)
                    # edges = cv2.Canny(gray, 50, 150, apertureSize=3)
                    # thresh = cv2.threshold(edges, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                    # thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                    
                    # contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    # for contour in contours:
                    #     # Compute the area of the contour
                    #     # area = cv2.contourArea(contour)
                    #     x, y, w, h = cv2.boundingRect(contour)
                    #     # Ignore small contours
                    #     aspect_ratio = w / float(h)
                    #     if aspect_ratio > 1.5 and aspect_ratio < 4 and w > 100 and h > 20:
                    #         #contour = max(contours, key=cv2.contourArea)
                    #         plate = vehicle_region[y:y+h, x:x+w]
                    #         cv2.imwrite(f'temp/{frame_count}_plate_{i}.jpg', plate)
                    
                    
                            # # Detecting the License number in the License Plate using Tesseract OCR
                            # gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
                            # blur = cv2.GaussianBlur(gray, (3, 3), 0)
                            # thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                            # number = pytesseract.image_to_string(thresh,lang='eng', config=config)
                            
                            # print(number)
                            
                            # cv2.rectangle(frame, (x+x1, y+y1), (x1+x+w, y1+y+h), (0, 0, 255), 2)
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break
        
        frame_count += 1

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()



app = Flask(__name__)
app.secret_key = b'Q!W@E#R$T%Y^U&I*O(P)'


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
    
    
@app.route('/result')
def result():
    # Rendering the result page
    return render_template('result.html')
    
    
if __name__ == "__main__":
    # Running the application at port 5000 in debug mode
    app.run(port=5000, debug=True)