import cv2

from app.passport.quality import analyze_quality


image = cv2.imread("app/passport/samples/test.jpg")

result = analyze_quality(image)

print(result)