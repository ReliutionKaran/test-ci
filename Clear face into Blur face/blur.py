import cv2
import os

face_cascade = cv2.CascadeClassifier("D:\Python Projects\Clear face into Blur face\Opencv_harcascade\haarcascade_frontalface_default.xml")

img = cv2.imread("group.png")

detection = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=6)

output_img = "blur_image"
os.makedirs(output_img, exist_ok=True)

for face in detection:
    x, y, w, h = face
    img[y:y+h, x:x+w] = cv2.GaussianBlur(img[y:y+h, x:x+w], (15, 15), cv2.BORDER_DEFAULT)
    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

cv2.imshow("output", img)
cv2.waitKey(0)

output_path = os.path.join(output_img, "blurface.png")
cv2.imwrite(output_path, img)

print(f"Processed image saved at: {output_path}")
