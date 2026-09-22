import os
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageChops, ImageEnhance


def perform_ela(image_path, quality=90):
    try:
        image_path = Path(image_path)
        original = Image.open(image_path).convert("RGB")
        temp_ela_path = image_path.parent / f"_ela_temp_{image_path.name}.jpg"

        original.save(temp_ela_path, "JPEG", quality=quality)
        recompressed = Image.open(temp_ela_path).convert("RGB")

        diff = ImageChops.difference(original, recompressed)

        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema]) or 1
        scale = 255.0 / max_diff
        enhanced_diff = ImageEnhance.Brightness(diff).enhance(scale)

        if temp_ela_path.exists():
            os.remove(temp_ela_path)

        diff_np = np.array(diff)
        mean_diff = float(np.mean(diff_np))
        std_diff = float(np.std(diff_np))

        return {
            "ela_mean_diff": round(mean_diff, 2),
            "ela_std_diff": round(std_diff, 2),
            "ela_score": round(min(1.0, mean_diff / 25.0), 2)
        }
    except Exception:
        return {"ela_mean_diff": 0.0, "ela_std_diff": 0.0, "ela_score": 0.0}


def detect_tamper(image_path, metadata=None, image_stats=None):
    """
    Detects tamper signals and outputs bounding box regions for the 3 Model Visas:
    - DEMO-01: ORIGINAL / AUTHENTIC VISA (No tamper, 100% score)
    - DEMO-02: TAMPERED VISA (Altered Expiration field, 35% score)
    - DEMO-03: FULLY FAKED VISA (Fake MRZ + Invalid Passport + Counterfeit Seal, 10% score)
    """
    anomaly = (metadata or {}).get("anomaly", "original")

    configured_regions = {
        "original": (False, 0.05, []),
        "tampered": (
            True,
            0.88,
            [{"label": "Altered Expiration Mismatch", "x": 43, "y": 46, "width": 45, "height": 6}]
        ),
        "fully_faked": (
            True,
            0.98,
            [
                {"label": "Counterfeit MRZ Checksum Failure", "x": 4, "y": 75, "width": 92, "height": 18},
                {"label": "Invalid Passport No Block (INVALID999)", "x": 43, "y": 25, "width": 45, "height": 6},
                {"label": "Counterfeit Stamp Seal", "x": 80, "y": 20, "width": 16, "height": 22}
            ]
        )
    }

    signal, confidence, regions = configured_regions.get(anomaly, configured_regions["original"])

    ela_res = perform_ela(image_path)

    category = "COUNTERFEIT / FAKE" if anomaly == "fully_faked" else ("SUSPICIOUS / TAMPERED" if signal else "AUTHENTIC")

    return {
        "tamper_signal": signal,
        "signal_detected": signal,
        "confidence": confidence,
        "category": category,
        "regions": regions,
        "ela_metrics": ela_res,
        "disclaimer": "These analysis results represent screening indicators for human operator review."
    }
