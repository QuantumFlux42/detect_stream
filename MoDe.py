#####
# Detects Motion in a YouTube strem
# $ ./python motion_detect.py https://www.youtube.com/watch?v=<ID>
#
# Sensitivity is VERY HIGH. increase 15,15 to something higher (25,25) if needed
##### 
import cv2
import sys
import pafy

font = cv2.FONT_HERSHEY_DUPLEX
# org
g_org = (1, 100)
c_org = (1, 170)
d_org = (1, 140)
# fontScale
fontScale = 1
# Blue color in BGR
color = (255, 0, 0)
# Line thickness of 2 px
thickness = 2

# GaussianBlur -- Larger is bigger kernel
gnum = 11
#contourArea -- Larger is bigger boxes
cnum = 201
# delta number
dnum = 25

show_status = 1
if 'http' in sys.argv[1]:
    url = sys.argv[1]
    video = pafy.new(url)
    best = video.getbest(preftype="mp4")

    baseline_image=None
    status_list=[None,None]
    video=cv2.VideoCapture(best.url)
else:
    baseline_image=None
    status_list=[None,None]
    video=cv2.VideoCapture(sys.argv[1])

while True:
    check, frame = video.read()
    status=0
    gray_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray_frame=cv2.GaussianBlur(gray_frame,(gnum,gnum),0)

    if baseline_image is None:
        baseline_image=gray_frame
        continue

    delta=cv2.absdiff(baseline_image,gray_frame)
    threshold=cv2.threshold(delta, dnum, 255, cv2.THRESH_BINARY)[1]
    (contours,_)=cv2.findContours(threshold,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < cnum:
            continue
        status=1
        (x, y, w, h)=cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 1)
    status_list.append(status)

    if show_status==1:
        # Using cv2.putText() method
        frame = cv2.putText(frame, "( g|G )aussianBlur:" + str(gnum), g_org, font,
                           fontScale, color, thickness, cv2.LINE_AA)
        frame = cv2.putText(frame, "(<c|C>)ontourArea:" + str(cnum), c_org, font,
                           fontScale, color, thickness, cv2.LINE_AA)
        frame = cv2.putText(frame, "( d|D )elta:" + str(dnum), d_org, font,
                           fontScale, color, thickness, cv2.LINE_AA)

    #cv2.imshow("gray_frame Frame",gray_frame)
    #cv2.imshow("Delta Frame",delta)
    #cv2.imshow("Threshold Frame",threshold)
    cv2.imshow("Color Frame",frame)

    key=cv2.waitKey(1)

    if key==ord('q'):
        if status==1:
            break
    if key==ord('h'):
        if status==1:
            if show_status==0:
                show_status=1
            else:
                show_status=0
    if key==ord('G'):
        if status==1:
            gnum = (gnum + 2)
            print("GaussianBlur:", gnum)
    if key==ord('g'):
        if status==1:
            if gnum == 1:
                gnum = 1
            else:
                gnum = (gnum - 2)
    if key==ord('C'):
        if status==1:
            cnum = (cnum + 1)
            print("contourArea:", cnum)
    if key==ord('c'):
        if status==1:
            if cnum == 1:
                cnum = 1
            else:
                cnum = (cnum - 1)
    if key==ord('>'):
        if status==1:
            cnum = (cnum + 200)
            print("contourArea:", cnum)
    if key==ord('<'):
        if status==1:
            if cnum < 201:
                cnum = 1
            else:
                cnum = (cnum - 200)
    if key==ord('D'):
        if status==1:
            dnum = (dnum + 1)
            print("Delta:", dnum)
    if key==ord('d'):
        if status==1:
            if dnum == 1:
                dnum = 1
            else:
                dnum = (dnum - 1)
    if key==ord('r'):
        if status==1:
            # Reset settings
            gnum = 25
            cnum = 10000 
            dnum = 5

#Clean up, Free memory
video.release()
cv2.destroyAllWindows
