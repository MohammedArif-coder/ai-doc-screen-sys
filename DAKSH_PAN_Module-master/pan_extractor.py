import re


def clean_name(value):
    """
    Clean OCR noise from a person's name.
    """

    value = value.upper().strip()

    # Keep only alphabets and spaces
    value = re.sub(r"[^A-Z ]", " ", value)

    # Remove extra spaces
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def clean_pan(value):
    """
    Clean OCR noise from PAN number.
    """

    value = value.upper().strip()

    # Keep only letters and numbers
    value = re.sub(r"[^A-Z0-9]", "", value)

    return value


def clean_dob(value):
    """
    Clean OCR noise from DOB.
    """

    match = re.search(
        r"\d{2}/\d{2}/\d{4}",
        value
    )

    if match:
        return match.group(0)

    return ""


def extract_pan_fields(text):

    fields = {
        "pan_number": "",
        "name": "",
        "father_name": "",
        "dob": ""
    }

    # ------------------------------------------------
    # PAN NUMBER
    # ------------------------------------------------

    pan_match = re.search(
        r"PAN\s*NUMBER\s*:\s*([A-Z0-9]+)",
        text,
        re.IGNORECASE
    )

    if pan_match:
        fields["pan_number"] = clean_pan(
            pan_match.group(1)
        )

    # ------------------------------------------------
    # NAME
    # ------------------------------------------------

    name_match = re.search(
        r"\bNAME\s*:\s*([^\n]+)",
        text,
        re.IGNORECASE
    )

    if name_match:

        raw_name = name_match.group(1)

        cleaned_name = clean_name(
            raw_name
        )

        # Keep the first meaningful words.
        # This removes OCR garbage after the name.
        words = cleaned_name.split()

        if len(words) >= 2:
            fields["name"] = (
                words[0] + " " + words[1]
            )
        elif len(words) == 1:
            fields["name"] = words[0]

    # ------------------------------------------------
    # FATHER'S NAME
    # ------------------------------------------------

    father_match = re.search(
        r"FATHER'?S\s*NAME\s*:\s*([^\n]+)",
        text,
        re.IGNORECASE
    )

    if father_match:

        raw_father_name = father_match.group(1)

        cleaned_father_name = clean_name(
            raw_father_name
        )

        words = cleaned_father_name.split()

        if len(words) >= 2:
            fields["father_name"] = (
                words[0] + " " + words[1]
            )
        elif len(words) == 1:
            fields["father_name"] = words[0]

    # ------------------------------------------------
    # DATE OF BIRTH
    # ------------------------------------------------

    dob_match = re.search(
        r"DATE\s*OF\s*BIRTH\s*:\s*([^\n]+)",
        text,
        re.IGNORECASE
    )

    if dob_match:

        fields["dob"] = clean_dob(
            dob_match.group(1)
        )

    return fields


if __name__ == "__main__":

    # Test OCR text
    ocr_text = """
    PAN NUMBER: ABCDE1234F fs) rth f=] { |
    NAME: RAVI KUMAR eres . re
    FATHER'S NAME: SURES. .._.... __ et > » y i
    DATE OF BIRTH: 15/08/2005 | ia ws > oat
    """

    result = extract_pan_fields(
        ocr_text
    )

    print("----- EXTRACTED PAN FIELDS -----")

    print(
        "PAN Number   :",
        result["pan_number"]
    )

    print(
        "Name         :",
        result["name"]
    )

    print(
        "Father Name  :",
        result["father_name"]
    )

    print(
        "Date of Birth:",
        result["dob"]
    )