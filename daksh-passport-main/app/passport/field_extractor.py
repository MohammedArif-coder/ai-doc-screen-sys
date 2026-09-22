import re


DATE_PATTERNS = [
    re.compile(r"^\d{2}[/-]\d{2}[/-]\d{4}$"),
    re.compile(r"^\d{2}[/-]\d{2}[/-]\d{2}$"),
    re.compile(r"^\d{4}[/-]\d{2}[/-]\d{2}$"),
]

PASSPORT_PATTERN = re.compile(
    r"^[A-Z0-9]{6,12}$"
)

COUNTRY_CODE_PATTERN = re.compile(
    r"^[A-Z]{3}$"
)

SEX_PATTERN = re.compile(
    r"^[MFX]$"
)


FIELD_ALIASES = {
    "name": [
        "name",
        "names",
        "full name",
        "full names",
        "given name",
        "given names",
        "surname",
        "family name",
        "holder name",
    ],

    "passport_number": [
        "passport no",
        "passport number",
        "passport no.",
        "document number",
        "document no",
        "number",
    ],

    "country_code": [
        "country code",
        "country",
        "code",
    ],

    "nationality": [
        "nationality",
        "citizenship",
    ],

    "sex": [
        "sex",
        "gender",
    ],

    "date_of_birth": [
        "date of birth",
        "birth date",
        "dob",
    ],

    "place_of_birth": [
        "place of birth",
        "birth place",
        "birthplace",
    ],

    "expiry_date": [
        "date of expiry",
        "expiry date",
        "expiration date",
        "date of expiration",
        "valid until",
    ],

    "issue_date": [
        "date of issue",
        "issue date",
        "issued on",
        "date issued",
    ],

    "issuing_authority": [
        "issuing authority",
        "issuing office",
        "authority",
        "issued by",
    ],
}


# Labels that should never be treated as field values
NON_VALUE_LABELS = {
    "passport",
    "type",
    "passport no",
    "passport number",
    "country code",
    "names",
    "name",
    "nationality",
    "sex",
    "gender",
    "date of birth",
    "birth date",
    "dob",
    "place of birth",
    "birthplace",
    "date of expiry",
    "expiry date",
    "expiration date",
    "date of expiration",
    "date of issue",
    "issue date",
    "issued on",
    "date issued",
    "issuing authority",
    "issuing office",
    "authority",
    "issued by",
    "holder's signature",
    "holders signature",
}


def normalize_text(text):
    text = str(text).upper().strip()

    text = text.replace(":", " ")
    text = text.replace(".", " ")
    text = text.replace("-", " ")

    text = re.sub(r"[^A-Z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_label(text):
    text = normalize_text(text)
    return text.lower()


def box_info(box):
    if not box:
        return None

    xs = [p[0] for p in box]
    ys = [p[1] for p in box]

    return {
        "left": min(xs),
        "top": min(ys),
        "right": max(xs),
        "bottom": max(ys),
        "center_x": (min(xs) + max(xs)) / 2,
        "center_y": (min(ys) + max(ys)) / 2,
    }


def prepare_items(ocr_results):
    items = []

    for item in ocr_results:

        text = str(item.get("text", "")).strip()

        if not text:
            continue

        info = box_info(item.get("box"))

        if info is None:
            continue

        # Remove obvious MRZ lines only.
        # Do not remove the whole lower passport area.
        normalized = text.replace(" ", "")

        if (
            len(normalized) >= 25
            and normalized.count("<") >= 3
        ):
            continue

        items.append({
            "text": text,
            **info
        })

    return items


def is_date(text):
    text = str(text).strip()

    return any(
        pattern.fullmatch(text)
        for pattern in DATE_PATTERNS
    )


def is_sex(text):
    return bool(
        SEX_PATTERN.fullmatch(
            normalize_text(text)
        )
    )


def is_country_code(text):
    return bool(
        COUNTRY_CODE_PATTERN.fullmatch(
            normalize_text(text)
        )
    )


def is_possible_passport_number(text):
    value = normalize_text(text).replace(" ", "")

    if not PASSPORT_PATTERN.fullmatch(value):
        return False

    if is_country_code(value):
        return False

    return any(
        char.isdigit()
        for char in value
    )


def is_label(text):
    normalized = normalize_label(text)

    return normalized in NON_VALUE_LABELS


def find_label(items, aliases):
    alias_set = {
        normalize_label(alias)
        for alias in aliases
    }

    candidates = []

    for item in items:

        normalized = normalize_label(
            item["text"]
        )

        if normalized in alias_set:

            candidates.append(
                item
            )

    if not candidates:
        return None

    # If multiple identical labels occur,
    # prefer the one in the main document body
    candidates.sort(
        key=lambda item: (
            item["top"],
            item["left"]
        )
    )

    return candidates[0]


def candidate_type_score(field, text):

    text = str(text).strip()

    if not text:
        return -100

    if field == "sex":
        return 100 if is_sex(text) else -100

    if field in {
        "date_of_birth",
        "expiry_date",
        "issue_date",
    }:
        return 100 if is_date(text) else -100

    if field == "country_code":
        return 100 if is_country_code(text) else -100

    if field == "passport_number":
        return (
            100
            if is_possible_passport_number(text)
            else -100
        )

    if field == "name":

        letters = sum(
            c.isalpha()
            for c in text
        )

        digits = sum(
            c.isdigit()
            for c in text
        )

        if letters >= 4 and digits == 0:
            return 80

        return -20

    if field == "nationality":

        letters = sum(
            c.isalpha()
            for c in text
        )

        return 70 if letters >= 4 else -20

    if field in {
        "place_of_birth",
        "issuing_authority",
    }:

        letters = sum(
            c.isalpha()
            for c in text
        )

        return 60 if letters >= 4 else -20

    return 0

def find_near_label(items, field):
    label = find_label(
        items,
        FIELD_ALIASES[field]
    )

    if label is None:
        return None

    candidates = []

    for item in items:

        if item is label:
            continue

        text_normalized = normalize_label(
            item["text"]
        )

        # Never select another field label
        if is_label(item["text"]):
            continue

        # Never use signature text as a value
        if text_normalized in {
            "holder s signature",
            "holders signature",
        }:
            continue

        type_score = candidate_type_score(
            field,
            item["text"]
        )

        if type_score < 0:
            continue

        dx = abs(
            item["center_x"] -
            label["center_x"]
        )

        dy = abs(
            item["center_y"] -
            label["center_y"]
        )

        vertical_gap = (
            item["top"] -
            label["bottom"]
        )

        same_row = dy <= 50

        below = (
            vertical_gap >= -15
            and vertical_gap <= 120
        )

        # General geometry score
        if same_row:
            geometry_score = (
                100 -
                min(dx, 200) * 0.35
            )

        elif below:
            geometry_score = (
                80 -
                min(dx, 250) * 0.25
            )

        else:
            continue

        # Special handling for issuing authority
        if field == "issuing_authority":

            # Allow small OCR-box overlap.
            # Our UAE sample overlaps by 6 pixels.
            if vertical_gap < -15:
                continue

            # The value must horizontally overlap
            # the label region.
            horizontal_overlap = (
                item["right"] >= label["left"]
                and
                item["left"] <= label["right"]
            )

            if not horizontal_overlap:
                continue

            # Reject text clearly positioned
            # far to the left of the label.
            if item["right"] < label["left"] - 30:
                continue

            geometry_score += 40

            # Prefer wider text blocks such as
            # MINISTRYOFINTERIOR.
            width = (
                item["right"] -
                item["left"]
            )

            geometry_score += min(
                width / 10,
                25
            )

        score = (
            type_score
            + geometry_score
            - min(dy, 100) * 0.15
        )

        candidates.append(
            (score, item)
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return candidates[0][1]
def find_passport_number(items):

    candidates = []

    for item in items:

        text = normalize_text(
            item["text"]
        ).replace(" ", "")

        if not is_possible_passport_number(
            text
        ):
            continue

        if len(text) < 6:
            continue

        # Exclude obvious MRZ lines
        if text.count("<") >= 3:
            continue

        candidates.append(
            (len(text), item)
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return candidates[0][1]


def extract_visual_fields(ocr_results):

    items = prepare_items(
        ocr_results
    )

    fields = {
        "passport_number": None,
        "country_code": None,
        "name": None,
        "nationality": None,
        "sex": None,
        "date_of_birth": None,
        "expiry_date": None,
        "place_of_birth": None,
        "issue_date": None,
        "issuing_authority": None,
    }

    # ------------------------------------------
    # Passport number
    # ------------------------------------------

    passport_item = find_passport_number(
        items
    )

    if passport_item:

        fields["passport_number"] = (
            normalize_text(
                passport_item["text"]
            ).replace(" ", "")
        )

    # ------------------------------------------
    # All remaining fields
    # ------------------------------------------

    for field in fields:

        if field == "passport_number":
            continue

        item = find_near_label(
            items,
            field
        )

        if item:

            fields[field] = (
                item["text"].strip()
            )

    return fields