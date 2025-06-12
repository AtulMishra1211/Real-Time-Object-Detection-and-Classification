import cv2
import torch
import serial
import time
from ultralytics import YOLO

import os

# Specify the path to the directory you want to change to
new_directory = r"Location to the directory"

# Change the current working directory
os.chdir(new_directory)

# Print the current working directory to confirm the change
print("Current working directory:", os.getcwd())

# Load YOLOv8 model
model_path = 'yolov8m-final-2.pt'  # Path to your local YOLOv8 model
model = YOLO(model_path)  # Load the YOLOv8 model

# Define class names (ensure these are in the same order as the training data)
class_names = ['cat', 'dog', 'man', 'soldier', 'tank', 'woman']  # Replace with your actual class names

# Open the video capture
cap = cv2.VideoCapture(0)  # Change to the correct camera index if needed

# Setup serial communication with Arduino
try:
    ArduinoSerial = serial.Serial('COM6', 9600, timeout=0.1)
except AttributeError:
    print("Serial library not imported correctly. Check your installation.")
    exit()
except serial.SerialException:
    print("Serial port could not be opened. Check the port and permissions.")
    exit()

time.sleep(1)  # Wait for the connection to establish

confidence_threshold=0.6

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Perform inference with YOLOv8
    results = model(frame)

    # Extract bounding boxes and class information from results
    for result in results:
        boxes = result.boxes  # Get the boxes from the result
        for box in boxes:

            confidence = box.conf[0].item()  # Extract confidence

            if confidence < confidence_threshold:
                continue  # Skip this detection if confidence is below threshold

            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Extract bounding box coordinates

            class_id = int(box.cls[0].item())  # Extract class ID

            # Calculate center of the bounding box
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            # Sending coordinates to Arduino
            string = 'X{0:d}Y{1:d}'.format(center_x, center_y)
            print(string)
            ArduinoSerial.write(string.encode('utf-8'))

            # Get class name using class ID
            class_name = class_names[class_id]

            # Plot bounding box and label on the frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{class_name} {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Plot the center region of the screen
    cv2.rectangle(frame, (640 // 2 - 30, 480 // 2 - 30),
                  (640 // 2 + 30, 480 // 2 + 30), (255, 255, 255), 3)

    cv2.imshow('img', frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
