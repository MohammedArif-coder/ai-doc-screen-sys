import cv2

from app.passport.quality import analyze_quality


image = cv2.imread("app/passport/samples/test.jpg")

if image is None:
    raise ValueError("Could not load test.jpg")

print("ORIGINAL")
print(analyze_quality(image))

blurred = cv2.GaussianBlur(image, (51, 51), 0)

print("\nARTIFICIALLY BLURRED")
print(analyze_quality(blurred))