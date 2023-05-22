import os
import re
import colorama
from time import sleep
import cv2
from flask import Flask, redirect, render_template, request, url_for
from ultralytics import YOLO
from werkzeug.utils import secure_filename
import pytesseract
import numpy as np
from database import get_vehicle_numbers, search_vehicle, insert_vehicle_number, get_number

#Initializing Tesseract for Character Recognition
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
config = r'--oem 3 --psm 6'


app = Flask(__name__)
app.secret_key = b'Q!W@E#R$T%Y^U&I*O(P)'

colorama.init()

class PlateFinder:
    def __init__(self):
        self.min_area = 4500  
        self.max_area = 30000  


    def preprocess(self, input_img):
        gray = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
        imgBlurred = cv2.GaussianBlur(gray, (7, 7), 0) 
        sobelx = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=3) 
        ret2, threshold_img = cv2.threshold(sobelx, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        edges = cv2.Canny(threshold_img, 250, 255, apertureSize=3)
        element = cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=(3, 3))
        morph_n_thresholded_img = threshold_img.copy()
        morph_n_thresholded_img = cv2.morphologyEx(src=edges, op=cv2.MORPH_CLOSE, kernel=element, dst=morph_n_thresholded_img)
        return morph_n_thresholded_img

    def extract_contours(self, after_preprocess):
        contours, _ = cv2.findContours(after_preprocess, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        return contours

    def clean_plate(self, plate):
        gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if contours:
            areas = [cv2.contourArea(c) for c in contours]
            max_index = np.argmax(areas)

            max_cntArea = areas[max_index]
            rotatedPlate = plate
            if not self.ratioCheck(max_cntArea, rotatedPlate.shape[1], rotatedPlate.shape[0]):    
                return plate, False
            return rotatedPlate, True
        
        else:
            return plate, False



    def check_plate(self, input_img, contour):
        min_rect = cv2.minAreaRect(contour)
        
        if self.validateRatio(min_rect):
            x, y, w, h = cv2.boundingRect(contour)
            after_validation_img = input_img[y:y + h, x:x + w]
            after_clean_plate_img, plateFound = self.clean_plate(after_validation_img)
            if plateFound:
                return after_clean_plate_img
        return None



    def find_possible_plates(self, input_img):
        plates = []

        self.after_preprocess = self.preprocess(input_img)
        
        possible_plate_contours = self.extract_contours(self.after_preprocess)

        for cnts in possible_plate_contours:
            plate = self.check_plate(input_img, cnts)
            if plate is not None:
                plates.append(plate)

        if (len(plates) > 0):
            return plates
        else:
            return None


    # PLATE FEATURES
    def ratioCheck(self, area, width, height):
        min = self.min_area
        max = self.max_area

        ratioMin = 2
        ratioMax = 6

        ratio = float(width) / float(height)
        if ratio < 1:
            ratio = 1 / ratio

        if (area < min or area > max) or (ratio < ratioMin or ratio > ratioMax):
            return False
        return True

    def preRatioCheck(self, area, width, height):
        min = self.min_area
        max = self.max_area

        ratioMin = 2.5
        ratioMax = 7

        ratio = float(width) / float(height)
        if ratio < 1:
            ratio = 1 / ratio

        if (area < min or area > max) or (ratio < ratioMin or ratio > ratioMax):
            return False
        return True

    def validateRatio(self, rect):
        (x, y), (width, height), rect_angle = rect

        if (width > height):
            angle = -rect_angle
        else:
            angle = 90 + rect_angle

        if angle > 15:
            return False
        if (height == 0 or width == 0):
            return False

        area = width * height
        if not self.preRatioCheck(area, width, height):
            return False
        else:
            return True
        
def detect_vehicles(video_path):
    # Loading the YOLOv8 model
    model = YOLO('models/best.pt')
    
    #Capturing the video by frames
    cap = cv2.VideoCapture(video_path)
    
    classes = [2,3,5,7]
    
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
        # findPlate = PlateFinder()
        
        # annotated_frame = results[0].plot()
        
        # Looping through the bounding boxes to process each vehicle
        for i in range(len(boxes)):
            for *xyxy, conf, cls in boxes[i].data:
                if conf > 0:#cls in classes and conf > 0.5:
                    x1, y1, x2, y2 = map(int, xyxy)
                    
                    number_plate = frame[y1:y2, x1:x2]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    count = len([name for name in os.listdir('./static/plates/')])
                    file_path = f"static/plates/plate_{count+1}.jpg"
                    cv2.imwrite(file_path, number_plate)
                    # possible_plates = findPlate.find_possible_plates(number_plate)
                    # if possible_plates is not None:
                    #     for j, p in enumerate(possible_plates):
                    #         cv2.imwrite(f'temp/plates/{frame_count}_{j}.jpg',p)                    

                    # Detecting the License number in the License Plate using Tesseract OCR
                    gray = cv2.cvtColor(number_plate, cv2.COLOR_BGR2GRAY)
                    # blur = cv2.GaussianBlur(gray, (5, 5), 0)
                    # thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

                    number = pytesseract.image_to_string(gray,lang='eng', config=config)
                    number = process_output(number)
                    if number is not None:
                        cv2.putText(frame, number, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        result = get_number(number)
                        if not len(result) > 0:
                            insert_vehicle_number(number, file_path)
                        print(colorama.Back.GREEN + number + colorama.Back.RESET)

        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break
        

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()


def process_output(number: str):
    special_chars = '~`!@#‘”$%^&*()_+=-“\n°— {:;\'"<,>.?/}[|\\]'
    pattern = r'^[A-Za-z]+\d+$'  # Pattern to match at least one letter followed by one or more digits

    for n in number:
        if n in special_chars:
            number = number.replace(n,'')
    if len(number)> 4 and len(number)< 13 and re.match(pattern, number):
        return number.upper()
    return None


    
@app.route('/license_plate_list', methods=['GET'])
def license_plate_list():
    search_query = request.args.get('search_query')
    if not search_query:
        search_query = '' 

    rows = search_vehicle(search_query.upper())

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
    # Storing the video file in the server
    video_file = request.files['videoFile']
    video_path = f"temp/{secure_filename(video_file.filename)}"
    if not os.path.exists(video_path):
        video_file.save(video_path)
        print("File Saved")
    
    # detecting the vehicle numbers in the video
    detect_vehicles(video_path)
    
    return redirect(url_for('detect_page'))
    

    
    
if __name__ == "__main__":
    # Running the application at port 5000 in debug mode
    app.run(port=5000, debug=True)