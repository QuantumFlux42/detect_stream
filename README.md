# detect_stream
You'll see an error relating to youtube-dl (you'll need to pip install it).
`pip install youtube-dl`

Another error will pop up pointing to <something>/site-packages/pafy/backend_youtube_dl.py 

Edit the file it points you to, and look for the line that starts with dislikes... and comment it out (change to #dislikes...). Save the file and everything should load proper.

Changing detection variables:
Gaussian Blur: g will decrease blur, G will increase blur
Threshold    : t will decrease threshold, T will increase threshold
contourArea  : c will decrease contourArea, C will increase contourArea
             : < will decrease contourArea by 200, > will increase contourArea by 200 (Tutorials started it at 10000 but low numbers helped box small objects)
