import sys
import numpy as np
import cv2
src = cv2.imread("./data/lenna.bmp", cv2.IMREAD_GRAYSCALE)

if src is None:
    print("Image load failed!")
    sys.exit()


dst1 = cv2.add(src, 100)
dst2 = np.clip(src + 100.0, 0, 255).astype(np.uint8)

cv2.imshow("src", src)
cv2.imshow("dst1", dst1)
cv2.imshow("dst2", dst2)
cv2.waitKey()

src = cv2.imread("./data/lenna.bmp")

if src is None:
    print("Image load failed!")
    sys.exit()

dst1 = cv2.add(src, (100, 100, 100, 0))
dst2 = np.clip(src + 100.0, 0, 255).astype(np.uint8)

cv2.imshow("src", src)
cv2.imshow("dst1", dst1)
cv2.imshow("dst2", dst2)
cv2.waitKey()    

cv2.destroyAllWindows()