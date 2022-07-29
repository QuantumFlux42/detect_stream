################################################################################
#                                                                              #
#  (Mo)tion (De)tect                                                           #
#  Detects Motion in a YouTube streams or video files                          #
#                                                                              #
#  Usage:                                                                      #
#    $ ./python MoDe.py https://www.youtube.com/watch?v=<ID>                   #
#    $ ./python MoDe.py file.mp4                                               #
#                                                                              #
#  Notes:                                                                      #
#    Sensitivity is VERY HIGH.                                                 #
#    increase 15,15 to something higher (25,25) if needed                      #
#                                                                              #
#  Dependencies:                                                               #
#    pip install pafy                                                          #
#    pip install youtube-dl                                                    #
#    pip install opencv-python                                                 #
#                                                                              #
################################################################################

from modules.video_stream import VideoStream
from modules.key_clip_writer import KeyClipWriter
import cv2
import datetime
import os
import pafy
import sys
import time

verbose = False
use_threading = False
show_quadrants = False

if verbose: print("(Mo)tion (De)tect Started...")

buffer_size = 684

kcw = KeyClipWriter(bufSize = buffer_size)
consecFrames = 0

out_dir = './saved'

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
count = 0
show_status = 1

if len(sys.argv) < 2:
    print("Usage: $ ./python MoDe.py https://www.youtube.com/watch?v=<ID>")
    print("Usage: $ ./python MoDe.py file.mp4")
    quit()

if 'http' in sys.argv[1]:
    url = sys.argv[1]
    video = pafy.new(url)
    if verbose:
        for stream in video.streams:
            print(stream)
    v_title = video.title
    best = video.getbest(preftype="mp4")
    if verbose: print("Selected:", best)
    path = best.url
else:
    path = sys.argv[1]
    v_title = os.path.basename(path)

baseline_image = None
status_list = [None,None]

if use_threading:
    vs = VideoStream(path).start()
    time.sleep(5) # Get a chance to buffer some frames
else:
    video = cv2.VideoCapture(path)
if verbose: print("Video Capture Started")

# while vs.more():
while True:
    if use_threading:
        frame = vs.read()
    else:
        check, frame = video.read()

    (frameHeight, frameWidth) = frame.shape[:2]
    (frameHalfHeight, frameHalfWidth) = (frameHeight // 2, frameWidth // 2)

    status=0
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.GaussianBlur(gray_frame, (gnum, gnum), 0)
    updateConsecFrames = True

    if baseline_image is None:
        baseline_image = gray_frame
        continue

    delta = cv2.absdiff(baseline_image, gray_frame)
    threshold = cv2.threshold(delta, dnum, 255, cv2.THRESH_BINARY)[1]
    (contours, _) = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < cnum:
            continue
        status = 1
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
    status_list.append(status)

    if show_status == 1:
        # Using cv2.putText() method
        frame = cv2.putText(frame, "gGaussianBlur:" + str(gnum), g_org, font,
                           fontScale, color, thickness, cv2.LINE_AA)
        frame = cv2.putText(frame, "<cC>ontourArea:" + str(cnum), c_org, font,
                           fontScale, color, thickness, cv2.LINE_AA)
        frame = cv2.putText(frame, "dDelta:" + str(dnum), d_org, font,
                           fontScale, color, thickness, cv2.LINE_AA)

    #cv2.imshow("gray_frame Frame", gray_frame)
    #cv2.imshow("Delta Frame", delta)
    #cv2.imshow("Threshold Frame", threshold)

    if show_quadrants:
        cv2.imshow(v_title + " Q1",frame[0:frameHalfHeight, 0:frameHalfWidth])
        cv2.imshow(v_title + " Q2",frame[0:frameHalfHeight, frameHalfWidth:frameWidth])
        cv2.imshow(v_title + " Q3",frame[frameHalfHeight:frameHeight, 0:frameHalfWidth])
        cv2.imshow(v_title + " Q4",frame[frameHalfHeight:frameHeight, frameHalfWidth:frameWidth])
    else:
        cv2.imshow(v_title, frame)

    key = cv2.waitKey(1)

    if key == ord('q'):
        if status == 1:
            break
    if key == ord('h'):
        if status == 1:
            if show_status == 0:
                show_status = 1
            else:
                show_status = 0
    if key == ord('G'):
        if status == 1:
            gnum = (gnum + 2)
    if key == ord('g'):
        if status == 1:
            if gnum == 1:
                gnum = 1
            else:
                gnum = (gnum - 2)
    if key == ord('C'):
        if status == 1:
            cnum = (cnum + 1)
    if key == ord('c'):
        if status == 1:
            if cnum == 1:
                cnum = 1
            else:
                cnum = (cnum - 1)
    if key == ord('>'):
        if status == 1:
            cnum = (cnum + 200)
    if key == ord('<'):
        if status == 1:
            if cnum < 201:
                cnum = 1
            else:
                cnum = (cnum - 200)
    if key == ord('D'):
        if status == 1:
            dnum = (dnum + 1)
    if key == ord('d'):
        if status == 1:
            if dnum == 1:
                dnum = 1
            else:
                dnum = (dnum - 1)
    if key == ord('r'):
        if status == 1:
            # Reset settings
            gnum = 25
            cnum = 10000 
            dnum = 5
    if key == ord('s'):
        timestamp = datetime.datetime.now()
        img_name = "{}/{}.png".format(out_dir, 
                   timestamp.strftime("%Y%m%d-%H%M%S"))
        cv2.imwrite(img_name, frame)
        count += 1
    if key == ord('S'):
        if not kcw.recording:
            timestamp = datetime.datetime.now()
            p = "{}/{}.avi".format(out_dir,
                timestamp.strftime("%Y%m%d-%H%M%S"))
            kcw.start(p, cv2.VideoWriter_fourcc(*"X264"),20)
    if updateConsecFrames:
        consecFrames += 1
    # update the key frame clip buffer
    kcw.update(frame)
    # if we are recording and reached a threshold on consecutive
    # number of frames with no action, stop recording the clip
    if kcw.recording and consecFrames == buffer_size:
        kcw.finish()
    if key == ord('x'):
        kcw.finish()
    if key == ord('p'):
        cv2.waitKey(-1)

    if use_threading:
        time.sleep(0.1)

if kcw.recording:
    kcw.finish()
#Clean up, Free memory
vs.stop()
cv2.destroyAllWindows
