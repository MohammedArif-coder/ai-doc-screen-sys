import cv2


original_path = "input/dummy_pan.png"
tampered_path = "input/tampered_pan.png"


original = cv2.imread(original_path)
tampered = cv2.imread(tampered_path)


if original is None:
    print("ERROR: Original PAN image not found.")
    exit()

if tampered is None:
    print("ERROR: Tampered PAN image not found.")
    exit()


# Make sure both images have the same size
if original.shape != tampered.shape:
    print("ERROR: Images have different sizes.")
    exit()


# Calculate pixel differences
difference = cv2.absdiff(original, tampered)

# Convert difference to grayscale
gray_difference = cv2.cvtColor(
    difference,
    cv2.COLOR_BGR2GRAY
)

# Threshold the difference
_, changed_pixels = cv2.threshold(
    gray_difference,
    30,
    255,
    cv2.THRESH_BINARY
)

# Count changed pixels
changed_count = cv2.countNonZero(changed_pixels)

total_pixels = changed_pixels.shape[0] * changed_pixels.shape[1]

change_percentage = (changed_count / total_pixels) * 100


print("----- PAN REFERENCE COMPARISON -----")
print("Total Pixels      :", total_pixels)
print("Changed Pixels    :", changed_count)
print("Change Percentage :", round(change_percentage, 2), "%")


if change_percentage > 1:
    print("Result            : REVIEW")
    print("Reason            : Significant image changes detected.")
else:
    print("Result            : NO SIGNIFICANT CHANGE")