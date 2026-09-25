MRZ_CHAR_VALUES = {}

for i in range(10):
    MRZ_CHAR_VALUES[str(i)] = i

for i, char in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    MRZ_CHAR_VALUES[char] = 10 + i

MRZ_CHAR_VALUES["<"] = 0


def calculate_check_digit(value):
    weights = [7, 3, 1]
    total = 0

    for i, char in enumerate(value):
        total += MRZ_CHAR_VALUES.get(char, 0) * weights[i % 3]

    return str(total % 10)


def check_field(value, expected_digit):
    calculated = calculate_check_digit(value)
    return calculated == expected_digit, calculated


def validate_mrz(line1, line2):
    result = {
        "line1_length": len(line1),
        "line2_length": len(line2),
        "checks": {}
    }

    if len(line1) != 44:
        result["line1_valid"] = False
    else:
        result["line1_valid"] = True

    if len(line2) != 44:
        result["line2_valid"] = False
    else:
        result["line2_valid"] = True

    if len(line2) == 44:
        passport_number = line2[0:9]
        passport_check = line2[9]

        dob = line2[13:19]
        dob_check = line2[19]

        expiry = line2[21:27]
        expiry_check = line2[27]

        passport_ok, passport_calculated = check_field(
            passport_number,
            passport_check
        )

        dob_ok, dob_calculated = check_field(
            dob,
            dob_check
        )

        expiry_ok, expiry_calculated = check_field(
            expiry,
            expiry_check
        )

        result["checks"]["passport_number"] = {
            "valid": passport_ok,
            "expected": passport_check,
            "calculated": passport_calculated
        }

        result["checks"]["date_of_birth"] = {
            "valid": dob_ok,
            "expected": dob_check,
            "calculated": dob_calculated
        }

        result["checks"]["expiry_date"] = {
            "valid": expiry_ok,
            "expected": expiry_check,
            "calculated": expiry_calculated
        }

    return result