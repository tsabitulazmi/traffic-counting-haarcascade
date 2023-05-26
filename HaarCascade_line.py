import cv2
import time
import math

# Set Countline Posisition
countline_pos = 300 # y position
x1 = 0
x2 = 250
offset = 10

# Import haar cascade
cascade_src = 'Traffic Counting\Versi Haar Cascade\cars.xml'
video_src = 'E:\Akang\Cari kerja\GBO\Traffic Counting\Video\Live Streaming - Area Traffic Control System_23.ts'

# Initialize count
count = 0
center_points_prev_frame = []
center_points_cur_frame = []
tracking_objects = {}
track_id = 0
id_list = []

# Time frame
timeframe = time.time()
frame_id = 0

cap = cv2.VideoCapture(video_src)
car_cascade = cv2.CascadeClassifier(cascade_src)

while True:
    ret, frame = cap.read()
    frame_id +=1
    count +=1

    if (type(frame) == type(None)):
        break

    height, width, channels = frame.shape
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    cars = car_cascade.detectMultiScale(gray, 1.1, 1)
    detections = []

    for (x,y,w,h) in cars:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0)) 
        #cv2.putText(img, 'car', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0),2)
        xmid = int((x + x+w)/2)
        ymid = int((y + y+h)/2)
        cv2.circle(frame,(xmid,ymid),3,(0,0,255),-1)  
        center_points_cur_frame.append([xmid,ymid])

    # Only at the beginning we compare previous and current frame
    if count <= 2:
        for pt in center_points_cur_frame:
            for pt2 in center_points_prev_frame:
                distance = math.hypot(pt2[0] - pt[0], pt2[1] - pt[1])

                if distance < 20:
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
        cv2.circle(frame, pt, 3, (0, 0, 255), -1)
        cv2.putText(frame, str(object_id), (pt[0], pt[1]), 0, 0.5, (0, 0, 255))
        if pt[1]<(countline_pos + offset) and pt[1]>(countline_pos - offset) and pt[0]>(x1) and pt[0]<(x2):
            #count +=1
            cv2.line(frame, (x1, countline_pos), (x2, countline_pos), (255,0,0), 3)
            if object_id not in id_list:
                id_list.append(object_id)
        
    vehicle_count = len(id_list)
       
    # Counting fps
    elapsedtime = time.time() - timeframe
    fps = round(frame_id/ elapsedtime , 2)

    cv2.line(frame, (x1, countline_pos), (x2, countline_pos), (0,255,0), 1)
    #cv2.line(frame, (x1, countline_pos+offset), (x2, countline_pos+offset), (0,255,255), 1)
    #cv2.line(frame, (x1, countline_pos-offset), (x2, countline_pos-offset), (0,255,255), 1)
    cv2.rectangle(frame, (0,0), (width,30), (255,255,255), -1)
    cv2.putText(frame, 'Count: ' + str(vehicle_count) + '   FPS : ' + str(fps), (5,25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,0,0))
    cv2.imshow('Video', frame)


    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
