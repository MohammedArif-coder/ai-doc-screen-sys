import re
from datetime import datetime


def validate_pan_fields(fields):
    validation = {
        "pan_format": False,
        "name_present": False,
        "father_name_present": False,
        "dob_format": False,
        "issues": []
    }

    # 1. Check PAN number format
    pan = fields.get("pan_number", "")

    if re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan):
        validation["pan_format"] = True
    else:
        validation["issues"].append("Invalid PAN number format")

    # 2. Check name
    name = fields.get("name", "").strip()

    if name:
        validation["name_present"] = True
    else:
        validation["issues"].append("Name is missing")

    # 3. Check father's name
    father_name = fields.get("father_name", "").strip()

    if father_name:
        validation["father_name_present"] = True
    else:
        validation["issues"].append("Father's name is missing")

    # 4. Check DOB format
    dob = fields.get("dob", "").strip()

    try:
        datetime.strptime(dob, "%d/%m/%Y")
        validation["dob_format"] = True
    except ValueError:
        validation["issues"].append("Invalid DOB format")

    return validation


if __name__ == "__main__":

    # Sample extracted PAN fields
    fields = {
        "pan_number": "ABCDE1234F",
        "name": "RAVI KUMAR",
        "father_name": "SURESH KUMAR",
        "dob": "15/08/2005"
    }

    result = validate_pan_fields(fields)

    print("----- PAN VALIDATION -----")

    print("PAN Format       :", "VALID" if result["pan_format"] else "INVALID")
    print("Name             :", "PRESENT" if result["name_present"] else "MISSING")
    print("Father's Name    :", "PRESENT" if result["father_name_present"] else "MISSING")
    print("DOB Format       :", "VALID" if result["dob_format"] else "INVALID")

    if result["issues"]:
        print("\nIssues:")
        for issue in result["issues"]:
            print("-", issue)
    else:
        print("\nNo basic validation issues found.")