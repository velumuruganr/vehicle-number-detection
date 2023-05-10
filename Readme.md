# Vehicle Number Detection and Tracking Using Deep Learning
This system is built using python with YOLOv8 - a state-of-the-art object detection algorithm from ultralytics ,Tesseract OCR and uses the coco model which is a pretrained model of various object.

### Description:
The system gets a video as input and detects the license number of the vehicles that are passed through in the video. The detected numbers are stored in a sqlite database which can be retrieved later for finding a vehicle in the video with its number.

### System Architecture:
The system works based on the following architecture:
    
                       Video Input
                            |
                    Frame Preprocessing
                            |
                     Vehicle Detection
                            |
                 Number Plate Localization
                            |
                  License Number Detecton
                            |
                   Output Vehicles Data


### Authors:
1. Velmurugan R
2. Yogesh R

