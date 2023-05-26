import cv2
import numpy as np
import math
import time

# Set region of interest
x1 = 0
x2 = 300
y1 = 80
y2 = 150
reg_ids = set()

# Import haar cascade
cascade_src = 'Traffic Counting\Versi Haar Cascade\cars.xml'
video_src = 'Traffic Counting\Video 1.avi'

# Initialize count
count = 0
center_points_prev_frame = []
tracking_objects = {}
track_id = 0

# Time frame
timeframe = time.time()
frame_id = 0



cap = cv2.VideoCapture(video_src)
car_cascade = cv2.CascadeClassifier(cascade_src)

while True:
    ret, frame = cap.read()
    count += 1
    frame_id += 1
    if (type(frame) == type(None)):
        break

    # Extract Region of interest
    height, width, channels = frame.shape
    roi = frame[y1:y2, x1:x2]
    reg = [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]

    # Point current frame
    center_points_cur_frame = []
    
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    cars = car_cascade.detectMultiScale(roi, 1.1, 1)
    detections = []

    for (x,y,w,h) in cars:
        cv2.rectangle(roi,(x,y),(x+w,y+h),(255,0,0)) 
        #cv2.putText(img, 'car', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0),2)
        xmid = int((x + x+w)/2)
        ymid = int((y + y+h)/2)
        #cv2.circle(roi,(xmid,ymid),3,(0,0,255),-1) 
        center_points_cur_frame.append((xmid, ymid))
       
     # Only at the beginning we compare previous and current frame
    if count <= 2:
        for pt in center_points_cur_frame:
            for pt2 in center_points_prev_frame:
                distance = math.hypot(pt2[0] - pt[0], pt2[1] - pt[1])

                if distance < 25:
                    tracking_objects[track_id] = pt
                    track_id += 1
    else:

        tracking_objects_copy = tracking_objects.copy()
        center_points_cur_frame_copy = center_points_cur_frame.copy()

        for object_id, pt2 in tracking_objects_copy.items():
            object_exists = False
            for pt in center_points_cur_frame_copy:
                distance = math.hypot(pt2[0] - pt[0], pt2[1] - pt[1])

                # Update IDs position
                if distance < 20:
                    tracking_objects[object_id] = pt
                    object_exists = True
                    if pt in center_points_cur_frame:
                        center_points_cur_frame.remove(pt)
                    continue

            # Remove IDs lost
            if not object_exists:
                tracking_objects.pop(object_id)

        # Add new IDs found
        for pt in center_points_cur_frame:
            tracking_objects[track_id] = pt
            track_id += 1

    for object_id, pt in tracking_objects.items():
        cv2.circle(roi, pt, 3, (0, 0, 255), -1)
        cv2.putText(roi, str(object_id), (pt[0], pt[1]), 0, 0.5, (0, 0, 255))
        inside_region = cv2.pointPolygonTest(np.array(reg), (pt[0],pt[1]), False)
        if(inside_region < 0):
            reg_ids.add(object_id)

    vehicle_count = len(reg_ids)

    # Counting fps
    elapsedtime = time.time() - timeframe
    fps = round(frame_id/ elapsedtime , 2)

    cv2.polylines(frame, [np.array(reg)], True, (0,255,0))
    cv2.rectangle(frame, (0,0), (width,30), (255,255,255), -1)
    cv2.putText(frame, 'Count: ' + str(vehicle_count) + '   FPS : ' + str(fps), (5,25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,0,0))
    cv2.imshow('Video', frame)

    if cv2.waitKey(50) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
