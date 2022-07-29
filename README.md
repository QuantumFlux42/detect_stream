# detect_stream

PREREQUISITES:
`pip install cv2-python pafy youtube-dl`

An error will pop up pointing to <something>/site-packages/pafy/backend_youtube_dl.py and dislikes. 

Edit the file it points you to, look for the line that starts with dislikes... and comment it out (change to #dislikes...). Save the file and everything should load proper.

RUNNING:
$ python ./motion_detect.py http://url.to/YouTube

Changing detection variables:
Gaussian Blur: g will decrease blur, G will increase blur
Delta    : d will decrease threshold, D will increase threshold
contourArea  : c will decrease contourArea, C will increase contourArea
             : < will decrease contourArea by 200, > will increase contourArea by 200 (Tutorials started it at 10000 but low numbers helped box small objects)
Hide Display : h will hide and unhide the detection variables

PLAYBACK CONTROLS:
Pause (p)
unpause (anykey)
save image (s)
save video clip (S) Recording begins -30s from when you push S
exit recording (x)
