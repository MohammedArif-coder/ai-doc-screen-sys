def parse_td3(line1, line2):
    line1 = line1.ljust(44, "<")
    line2 = line2.ljust(44, "<")

    data = {}

    data["document_type"] = line1[0]
    data["issuing_country"] = line1[2:5]

    names = line1[5:44]
    parts = names.split("<<", 1)

    data["surname"] = parts[0].replace("<", " ").strip()

    if len(parts) > 1:
        data["given_names"] = parts[1].replace("<", " ").strip()
    else:
        data["given_names"] = ""

    data["passport_number"] = line2[0:9]
    data["passport_number_check"] = line2[9]

    data["nationality"] = line2[10:13]

    data["date_of_birth"] = line2[13:19]
    data["date_of_birth_check"] = line2[19]

    data["sex"] = line2[20]

    data["expiry_date"] = line2[21:27]
    data["expiry_date_check"] = line2[27]

    data["optional_data"] = line2[28:43]

    data["final_check"] = line2[43]

    return data