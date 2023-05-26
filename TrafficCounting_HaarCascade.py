from tkinter import *
from tkinter import filedialog
import cv2
import math
import time
import numpy as np

def event_run():

    # Set Countline Position
    countline_pos = int(e_linepos.get())
    offset = int(e_offset.get())
    x1 = int(e_x1.get())
    x2 = int(e_x2.get())

    # Video Source
    src = video_src

    # Import haar cascade
    cascade_src = xml_src

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

    cap = cv2.VideoCapture(src)
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

        time_output.configure(text=int(elapsedtime))
        fps_output.configure(text=str(fps))
        car_output.configure(text=vehicle_count)
        total_output.configure(text=vehicle_count)
        root.update()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

def event_videosrc():
    videosrc = filedialog.askopenfilename(filetypes=[("all video format",".mp4"),("all video format",".avi"),("all video format",".ts")])
    global video_src
    video_src = videosrc
    if len(videosrc) > 0:
        e_videosrc.configure(text=videosrc)

def event_xml():
    xml = filedialog.askopenfilename(filetypes=[("all format",".xml")])
    global xml_src
    xml_src = xml
    if len(xml) > 0:
        e_xml.configure(text=xml)

root=Tk()
root.title("GBO Traffic Counting Software")
root.geometry("800x600")
root.grid_columnconfigure((0,1), weight=1, uniform="column")

welcome_text = Label(root, text="Welcome in GBO Traffic Counting Software!", font=("times new roman",20,"bold"))

#Input text
input_text = Label(root, text="INPUT", font=("times new roman", 15, "bold"))
videosrc_text = Label(root, text="Video directory:")
xml_text = Label(root, text="xml file directory:")
linepos_text = Label(root, text="Input countline position(y):")
x1_text = Label(root,text="Input x1:")
x2_text = Label(root,text="Input x2:")
offset_text = Label(root,text="Input offset value:")

#Output text
output_text = Label(root, text="OUTPUT", font=("times new roman", 15, "bold"))
time_text = Label(root, text="Time :")
fps_text = Label(root, text="FPS :")
car_text = Label(root, text="Car :")
truck_text = Label(root, text="Truck :")
bus_text = Label(root, text="Bus :")
motorcycle_text = Label(root, text="Motorcycle :")
total_text = Label(root, text="Total :")

#Input Entry
e_videosrc = Label(root, text="Choose a video...", wraplength=350)
e_xml = Label(root, text="Choose a xml file...",wraplength=350)
e_linepos = Entry(root, width=10)
e_x1 = Entry(root, width=10)
e_x2 = Entry(root, width=10)
e_offset = Entry(root, width=10)

#Output
time_output = Label(root, text="")
fps_output = Label(root, text="")
car_output = Label(root, text="")
truck_output = Label(root, text="")
bus_output = Label(root, text="")
motorcycle_output = Label(root, text="")
total_output = Label(root, text="")

btn_video = Button(root, text="Browse", command=event_videosrc)
btn_xml = Button(root, text="Browse", command=event_xml)
btn_run = Button(root, text="Run", command= event_run, width=40)

#Input text position
welcome_text.pack()
input_text.place(x=150, y=50)
videosrc_text.place(x=20, y=80)
xml_text.place(x=20, y=160)
linepos_text.place(x=20, y=240)
x1_text.place(x=20, y=270)
x2_text.place(x=20, y=300)
offset_text.place(x=20, y=330)

#Output text Position
output_text.place(x=550, y=50)
time_text.place(x=460, y=100)
fps_text.place(x=460, y=130)
car_text.place(x=460, y=160)
truck_text.place(x=460, y=190)
bus_text.place(x=460, y=220)
motorcycle_text.place(x=460, y=250)
total_text.place(x=460, y=280)

#Input entry position
e_videosrc.place(x=80, y=105)
e_xml.place(x=80, y=185)
e_linepos.place(x=200, y=240)
e_x1.place(x=200, y=270)
e_x2.place(x=200, y=300)
e_offset.place(x=200, y=330)

#Output position
time_output.place(x=560, y=100)
fps_output.place(x=560, y=130)
car_output.place(x=560, y=160)
truck_output.place(x=560, y=190)
bus_output.place(x=560, y=220)
motorcycle_output.place(x=560, y=250)
total_output.place(x=560, y=280)

btn_video.place(x=20, y=100)
btn_xml.place(x=20, y=180)
btn_run.place(x=470, y=530)



root.mainloop()