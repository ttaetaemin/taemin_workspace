import cv2
import numpy as np
import sys

oldx = oldy= -1

def on_mouse(event, x, y, flags, param):
    global oldx, oldy

    if event == cv2.EVENT_LBUTTONDOWN:
        oldx, oldy = x, y
        print('EVENT_LBUTTONDOWN: %d, %d' % (x, y))


    elif event == cv2.EVENT_LBUTTONUP:
        print('EVENT_LBUTTONDOWN: %d, %d' % (x, y))


    elif event == cv2.EVENT_MOUSEMOVE:
        if flags & cv2.EVENT_FLAG_LBUTTON:
            cv2.line(img, (oldx, oldy), (x, y), (255, 0, 0), 4 ,cv2.LINE_AA) ## rgb 순서가 아니라 bgr
            cv2.imshow('image', img)
            oldx, oldy = x, y


img = np.ones((480, 640, 3), dtype=np.uint8)*255


cv2.namedWindow('image')
cv2.setMouseCallback('image', on_mouse, img)

cv2.imshow('image', img)
cv2.waitKey()

cv2.destroyAllWindows()



# img = np.ones((512, 512,3), np.uint8)

# def draw_circle(event, x, y, flags, param):
#     if event == cv2.EVENT_FLAG_LBUTTON:
#         print(x, y)
    

# cv2.namedWindow(winname="my_first_drawing")
# cv2.setMouseCallback("my_first_drawing", draw_circle, img)

# while True:
#     cv2.imshow("my_first_drawing", img)

#     if cv2.waitKey(10) == 27:
#         break

cv2.destroyAllWindows()

