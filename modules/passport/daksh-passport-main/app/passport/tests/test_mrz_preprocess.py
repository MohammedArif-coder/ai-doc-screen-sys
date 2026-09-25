from app.passport.mrz_preprocess import crop_mrz


IMAGE_PATH = "app/passport/artifacts/processed.jpg"
OUTPUT_PATH = "app/passport/artifacts/mrz_crop.png"

print("Creating MRZ crop...")

crop_mrz(IMAGE_PATH, OUTPUT_PATH)

print("MRZ crop saved:")
print(OUTPUT_PATH)