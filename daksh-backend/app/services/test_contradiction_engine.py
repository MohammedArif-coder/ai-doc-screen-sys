import unittest

from app.schemas import Evidence, EvidenceType
from app.services.contradiction_engine import detect_contradictions


def evidence(
    evidence_id: str,
    document_id: str,
    field: str,
    value: str,
    source: str,
    confidence: float | None = None,
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        document_id=document_id,
        evidence_type=EvidenceType.OBSERVATION,
        field=field,
        value=value,
        confidence=confidence,
        source=source,
    )


class ContradictionEngineTests(unittest.TestCase):
    def test_passport_name_matches_aadhaar_printed_name(self) -> None:
        result = detect_contradictions([
            evidence("p-name", "p", "name", "ARUN KUMAR", "passport.visual_fields"),
            evidence("a-name", "a", "printed.name", "ARUN KUMAR", "aadhaar.printed"),
        ])
        self.assertEqual(result, [])

    def test_passport_name_mismatches_aadhaar_printed_name(self) -> None:
        result = detect_contradictions([
            evidence("p-name", "p", "name", "ARUN KUMAR", "passport.visual_fields"),
            evidence("a-name", "a", "printed.name", "ARUN KUMER", "aadhaar.printed"),
        ])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].severity, "MEDIUM")

    def test_passport_name_matches_and_mismatches_qr_name(self) -> None:
        matching = detect_contradictions([
            evidence("p-name", "p", "name", "ARUN KUMAR", "passport.visual_fields"),
            evidence("a-qr-name", "a", "qr.name", "ARUN KUMAR", "aadhaar.qr"),
        ])
        mismatch = detect_contradictions([
            evidence("p-name", "p", "name", "ARUN KUMAR", "passport.visual_fields"),
            evidence("a-qr-name", "a", "qr.name", "ARUN KUMER", "aadhaar.qr"),
        ])
        self.assertEqual(matching, [])
        self.assertEqual(mismatch[0].severity, "MEDIUM")
        self.assertIn("a-qr-name", mismatch[0].explanation)

    def test_passport_dob_matches_and_mismatches_printed_dob(self) -> None:
        matching = detect_contradictions([
            evidence("p-dob", "p", "dob", "2005-04-12", "passport.visual_fields"),
            evidence("a-dob", "a", "printed.dob", "12/04/2005", "aadhaar.printed"),
        ])
        mismatch = detect_contradictions([
            evidence("p-dob", "p", "dob", "2005-04-12", "passport.visual_fields"),
            evidence("a-dob", "a", "printed.dob", "2005-04-13", "aadhaar.printed"),
        ])
        self.assertEqual(matching, [])
        self.assertEqual(mismatch[0].severity, "HIGH")

    def test_passport_dob_matches_and_mismatches_qr_dob(self) -> None:
        matching = detect_contradictions([
            evidence("p-dob", "p", "dob", "2005-04-12", "passport.visual_fields"),
            evidence("a-qr-dob", "a", "qr.dob", "12/04/2005", "aadhaar.qr"),
        ])
        mismatch = detect_contradictions([
            evidence("p-dob", "p", "dob", "2005-04-12", "passport.visual_fields"),
            evidence("a-qr-dob", "a", "qr.dob", "2005-04-13", "aadhaar.qr"),
        ])
        self.assertEqual(matching, [])
        self.assertEqual(mismatch[0].severity, "HIGH")

    def test_missing_or_unavailable_fields_do_not_contradict(self) -> None:
        self.assertEqual(
            detect_contradictions([
                evidence("p-name", "p", "name", "ARUN KUMAR", "passport.visual_fields"),
            ]),
            [],
        )
        self.assertEqual(
            detect_contradictions([
                evidence("p-name", "p", "name", "ARUN KUMAR", "passport.visual_fields"),
                evidence("a-status", "a", "qr.status", "NOT_CONFIGURED", "aadhaar.qr"),
            ]),
            [],
        )

    def test_none_confidence_is_preserved(self) -> None:
        result = detect_contradictions([
            evidence("p-name", "p", "name", "ARUN KUMAR", "passport.visual_fields"),
            evidence("a-name", "a", "printed.name", "ARUN KUMER", "aadhaar.printed"),
        ])
        self.assertIsNone(result[0].confidence)

    def test_printed_and_qr_provenance_remains_distinguishable(self) -> None:
        result = detect_contradictions([
            evidence("p-name", "p", "name", "ARUN KUMAR", "passport.visual_fields"),
            evidence("a-printed", "a", "printed.name", "ARUN KUMER", "aadhaar.printed"),
            evidence("a-qr", "a", "qr.name", "ARUN KUMER", "aadhaar.qr"),
        ])
        self.assertEqual(len(result), 2)
        self.assertEqual(
            {item.value_b for item in result},
            {"ARUN KUMER"},
        )
        self.assertTrue(all("a-" in item.explanation for item in result))

    def test_duplicate_evidence_does_not_duplicate_contradictions(self) -> None:
        items = [
            evidence("p-name", "p", "name", "ARUN KUMAR", "passport.visual_fields"),
            evidence("a-name", "a", "printed.name", "ARUN KUMER", "aadhaar.printed"),
        ]
        result = detect_contradictions(items + items)
        self.assertEqual(len(result), 1)

    def test_aadhaar_only_evidence_has_no_contradiction(self) -> None:
        self.assertEqual(
            detect_contradictions([
                evidence("a-name", "a", "printed.name", "ARUN KUMAR", "aadhaar.printed"),
                evidence("a-qr-name", "a", "qr.name", "ARUN KUMER", "aadhaar.qr"),
            ]),
            [],
        )

    def test_existing_passport_visa_mapping_remains_high(self) -> None:
        result = detect_contradictions([
            evidence("p-number", "p", "passport_number", "A123", "passport.visual_fields"),
            evidence("v-number", "v", "passport_no", "B456", "visa.ocr"),
        ])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].severity, "HIGH")


if __name__ == "__main__":
    unittest.main()
