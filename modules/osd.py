import cv2

def display_status(show_status, frame, gnum, g_org, cnum, c_org, dnum, d_org, 
                  font, fontScale, color, thickness):
    #Using cv2.putText() method
    frame = cv2.putText(frame, "gGaussianBlur:" + str(gnum), 
                       g_org, font, fontScale, color, thickness, cv2.LINE_AA)
    frame = cv2.putText(frame, "<cC>ontourArea:" + str(cnum), 
                       c_org, font, fontScale, color, thickness, cv2.LINE_AA)
    frame = cv2.putText(frame, "dDelta:" + str(dnum), 
                       d_org, font, fontScale, color, thickness, cv2.LINE_AA)