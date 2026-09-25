from app.passport.forensics import run_forensics


IMAGE_PATH = "app/passport/artifacts/processed.jpg"

ELA_PATH = "app/passport/artifacts/ela_heatmap.png"


print("Running forensic analysis...")

result = run_forensics(
    IMAGE_PATH,
    ELA_PATH
)


print("\nIMAGE QUALITY")
print("=" * 60)

for key, value in result["image_quality"].items():
    print(f"{key}: {value}")


print("\nMETADATA")
print("=" * 60)

for key, value in result["metadata"].items():
    print(f"{key}: {value}")


print("\nELA")
print("=" * 60)

for key, value in result["ela"].items():

    if key != "suspicious_regions":
        print(f"{key}: {value}")


print("\nSUSPICIOUS REGIONS")
print("=" * 60)

for i, region in enumerate(
    result["ela"]["suspicious_regions"],
    start=1
):

    print(
        f"{i}. "
        f"x={region['x']} "
        f"y={region['y']} "
        f"width={region['width']} "
        f"height={region['height']} "
        f"area={region['area']}"
    )


print("\nELA heatmap:")
print(ELA_PATH)