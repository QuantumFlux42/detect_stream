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
 
from collections import deque
from queue import Queue
from threading import Thread
import cv2
import datetime
import os
import pafy
import sys
import time

class VideoStream:
    def __init__(self, path, queueSize = 128):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        self.stream = cv2.VideoCapture(path)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 530)
        self.stopped = False
        # initialize the queue used to store frames read from
        # the video file
        self.Q = Queue(maxsize = queueSize)
    def start(self):
        # start a thread to read frames from the file video stream
        t = Thread(target = self.update, args=())
        t.daemon = True
        t.start()
        return self
    def update(self):
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                return
            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                # read the next frame from the file
                (grabbed, frame) = self.stream.read()
                # if the `grabbed` boolean is `False`, then we have
                # reached the end of the video file
                if not grabbed:
                    self.stop()
                    return
                # add the frame to the queue
                self.Q.put(frame)
    def read(self):
        # return next frame in the queue
        return self.Q.get()
    def more(self):
        # return True if there are still frames in the queue
        print(self.Q.qsize())
        return self.Q.qsize() > 0
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


buffer_size = 684
# Shameless jack of code 
class KeyClipWriter:
    def __init__(self, bufSize=buffer_size, timeout=1.0):
        # store the maximum buffer size of frames to be kept
        # in memory along with the sleep timeout during threading
        self.bufSize = bufSize
        self.timeout = timeout
        # initialize the buffer of frames, queue of frames that
        # need to be written to file, video writer, writer thread,
        # and boolean indicating whether recording has started or not
        self.frames = deque(maxlen=bufSize)
        self.Q = None
        self.writer = None
        self.thread = None
        self.recording = False

    def update(self, frame):
        # update the frames buffer
        self.frames.appendleft(frame)
        # if we are recording, update the queue as well
        if self.recording:
            self.Q.put(frame)

    def start(self, outputPath, fourcc, fps):
        # indicate that we are recording, start the video writer,
        # and initialize the queue of frames that need to be written
        # to the video file
        self.recording = True
        self.writer = cv2.VideoWriter(outputPath, fourcc, fps,
             (1920,1080), True)
        #    (self.frames[0].shape[1], self.frames[0].shape[0]), True)
        self.Q = Queue()
        # loop over the frames in the deque structure and add them
        # to the queue
        for i in range(len(self.frames), 0, -1):
            self.Q.put(self.frames[i - 1])
        # start a thread write frames to the video file
        self.thread = Thread(target=self.write, args=())
        self.thread.daemon = True
        self.thread.start()

    def write(self):
        # keep looping
        while True:
            # if we are done recording, exit the thread
            if not self.recording:
                return
            # check to see if there are entries in the queue
            if not self.Q.empty():
                # grab the next frame in the queue and write it
                # to the video file
                frame = self.Q.get()
                self.writer.write(frame)
            # otherwise, the queue is empty, so sleep for a bit
            # so we don't waste CPU cycles
            else:
                time.sleep(self.timeout)

    def flush(self):
        # empty the queue by flushing all remaining frames to file
        while not self.Q.empty():
            frame = self.Q.get()
            self.writer.write(frame)

    def finish(self):
        # indicate that we are done recording, join the thread,
        # flush all remaining frames in the queue to file, and
        # release the writer pointer
        self.recording = False
        self.thread.join()
        self.flush()
        self.writer.release()

kcw = KeyClipWriter(bufSize=buffer_size)
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
    for stream in video.streams:
        print(stream)
    v_title = video.title
    v_streams = video.allstreams
    v_stream = v_streams[4]
    best = video.getbest(preftype="mp4")
    print("Selected:", best)
    path = best.url
else:
    path = sys.argv[1]

baseline_image = None
status_list = [None,None]

vs = VideoStream(path).start()
time.sleep(5) # Get a chance to buffer some frames
print("Video Capture Started")

# while vs.more():
while True:
    frame = vs.read()
    status=0
    gray_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray_frame=cv2.GaussianBlur(gray_frame,(gnum,gnum),0)
    updateConsecFrames = True

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
        frame = cv2.putText(frame, "gGaussianBlur:" + str(gnum), g_org, font,
                           fontScale, color, thickness, cv2.LINE_AA)
        frame = cv2.putText(frame, "<cC>ontourArea:" + str(cnum), c_org, font,
                           fontScale, color, thickness, cv2.LINE_AA)
        frame = cv2.putText(frame, "dDelta:" + str(dnum), d_org, font,
                           fontScale, color, thickness, cv2.LINE_AA)

    #cv2.imshow("gray_frame Frame",gray_frame)
    #cv2.imshow("Delta Frame",delta)
    #cv2.imshow("Threshold Frame",threshold)
    (h, w) = frame.shape[:2]
    print(h, w)
    cv2.imshow(v_title,frame[0:h, 0:w])

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
    if key==ord('g'):
        if status==1:
            if gnum == 1:
                gnum = 1
            else:
                gnum = (gnum - 2)
    if key==ord('C'):
        if status==1:
            cnum = (cnum + 1)
    if key==ord('c'):
        if status==1:
            if cnum == 1:
                cnum = 1
            else:
                cnum = (cnum - 1)
    if key==ord('>'):
        if status==1:
            cnum = (cnum + 200)
    if key==ord('<'):
        if status==1:
            if cnum < 201:
                cnum = 1
            else:
                cnum = (cnum - 200)
    if key==ord('D'):
        if status==1:
            dnum = (dnum + 1)
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

    time.sleep(0.1)

if kcw.recording:
    kcw.finish()
#Clean up, Free memory
vs.stop()
cv2.destroyAllWindows
