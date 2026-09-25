from app.passport.mrz_parser import parse_td3
from app.passport.consistency import compare_passport_fields


line1 = "P<MAZR0UI<<TAREQ<AL<<<<<<<<<<<<<<<<<<<<<<<<<"
line2 = "M56H12345ARE15121981M03052021<<<<<<<<<<<<<<8"

mrz = parse_td3(line1, line2)


visual = {
    "passport_number": "M56H12345",
    "country_code": "ARE",
    "name": "TAREQ AL-MAZROUI",
    "sex": "M",
    "date_of_birth": "15/12/1981",
    "expiry_date": "03/05/2021"
}


results = compare_passport_fields(visual, mrz)


print("VISUAL ↔ MRZ CONSISTENCY")
print("=" * 70)

for result in results:
    print(f"\nField: {result['field']}")
    print(f"Status: {result['status']}")
    print(f"Visual: {result['visual']}")
    print(f"MRZ: {result['mrz']}")