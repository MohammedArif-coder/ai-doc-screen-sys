import cv2

from app.passport.preprocessing import preprocess_image


IMAGE_PATH = "app/passport/samples/test.jpg"


result = preprocess_image(IMAGE_PATH)

print("PREPROCESSING TEST")
print("------------------")

print("Original shape:",
      result["original"].shape)

print("Processed shape:",
      result["processed"].shape)

print("Grayscale shape:",
      result["gray"].shape)

print("Enhanced shape:",
      result["enhanced"].shape)

print("Was resized:",
      result["was_resized"])


cv2.imwrite(
    "app/passport/artifacts/processed.jpg",
    result["processed"]
)

cv2.imwrite(
    "app/passport/artifacts/gray.jpg",
    result["gray"]
)

cv2.imwrite(
    "app/passport/artifacts/enhanced.jpg",
    result["enhanced"]
)

print("\nSaved:")
print("artifacts/processed.jpg")
print("artifacts/gray.jpg")
print("artifacts/enhanced.jpg")