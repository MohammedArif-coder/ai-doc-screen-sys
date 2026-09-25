import os
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

MODULES_DIR = ROOT_DIR / "modules"
ARCHIVE_DIR = ROOT_DIR / "archive"
LEGACY_FRONTENDS = ARCHIVE_DIR / "legacy_frontends"
LEGACY_DASHBOARDS = ARCHIVE_DIR / "legacy_html_dashboards"

def safe_move(src: Path, dst: Path):
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return
    print(f"Moving {src.relative_to(ROOT_DIR)} -> {dst.relative_to(ROOT_DIR)}")
    try:
        shutil.move(str(src), str(dst))
    except Exception as e:
        print(f"Move warning: {e}")

def safe_copy(src: Path, dst: Path):
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return
    print(f"Copying {src.relative_to(ROOT_DIR)} -> {dst.relative_to(ROOT_DIR)}")
    try:
        if src.is_dir():
            shutil.copytree(str(src), str(dst), dirs_exist_ok=True)
        else:
            shutil.copy2(str(src), str(dst))
    except Exception as e:
        print(f"Copy warning: {e}")

def safe_rmtree(path: Path):
    if not path.exists():
        return
    try:
        shutil.rmtree(str(path), ignore_errors=True)
    except Exception:
        pass

def reorganize():
    print("=== DAKSH REORGANIZATION SCRIPT ===")

    MODULES_DIR.mkdir(exist_ok=True)
    ARCHIVE_DIR.mkdir(exist_ok=True)
    LEGACY_FRONTENDS.mkdir(parents=True, exist_ok=True)
    LEGACY_DASHBOARDS.mkdir(parents=True, exist_ok=True)

    # 1. Aadhaar
    aadhaar_inner = ROOT_DIR / "aadhaar-screening-module-main" / "aadhaar-screening-module-main"
    if aadhaar_inner.exists():
        safe_copy(aadhaar_inner / "backend", MODULES_DIR / "aadhaar" / "backend")
        safe_copy(aadhaar_inner / "frontend", LEGACY_FRONTENDS / "aadhaar-frontend")
        for item in aadhaar_inner.iterdir():
            if item.name not in ["backend", "frontend"]:
                safe_copy(item, MODULES_DIR / "aadhaar" / item.name)
        safe_rmtree(ROOT_DIR / "aadhaar-screening-module-main")
        print("[OK] Reorganized Aadhaar module -> modules/aadhaar/")

    # 2. Passport
    passport_src = ROOT_DIR / "daksh-passport-main"
    if passport_src.exists():
        safe_copy(passport_src / "app", MODULES_DIR / "passport" / "backend" / "app")
        safe_copy(passport_src / "app" / "streamlit_app.py", LEGACY_FRONTENDS / "passport-frontend" / "streamlit_app.py")
        safe_copy(passport_src / "app" / "static", LEGACY_FRONTENDS / "passport-frontend" / "static")
        for item in passport_src.iterdir():
            if item.name != "app":
                safe_copy(item, MODULES_DIR / "passport" / item.name)
        safe_rmtree(passport_src)
        print("[OK] Reorganized Passport module -> modules/passport/")

    # 3. Visa
    visa_inner = ROOT_DIR / "ai-doc-screen-sys" / "ai-doc-screen-sys"
    if visa_inner.exists():
        safe_copy(visa_inner / "backend", MODULES_DIR / "visa" / "backend")
        safe_copy(visa_inner / "frontend", LEGACY_FRONTENDS / "visa-frontend")
        for item in visa_inner.iterdir():
            if item.name not in ["backend", "frontend"]:
                safe_copy(item, MODULES_DIR / "visa" / item.name)
        safe_rmtree(ROOT_DIR / "ai-doc-screen-sys")
        print("[OK] Reorganized Visa module -> modules/visa/")

    # 4. Driving Licence
    dl_src = ROOT_DIR / "Driving Licence module"
    if dl_src.exists():
        safe_copy(dl_src / "backend", MODULES_DIR / "driving-licence" / "backend")
        for item in dl_src.iterdir():
            if item.name != "backend":
                safe_copy(item, MODULES_DIR / "driving-licence" / item.name)
        safe_rmtree(dl_src)
        print("[OK] Reorganized Driving Licence module -> modules/driving-licence/")

    # 5. PAN
    pan_src = ROOT_DIR / "DAKSH_PAN_Module-master"
    if pan_src.exists():
        safe_copy(pan_src, MODULES_DIR / "pan" / "backend")
        safe_rmtree(pan_src)
        print("[OK] Reorganized PAN module -> modules/pan/")

    # 6. Legacy HTML Dashboards
    dashboards = [
        "DAKSH dash.html", "DAKSH dash_files",
        "frontend-daksh.html", "frontend-daksh_files",
        "pipeline.html", "pipeline_files"
    ]
    for d in dashboards:
        p = ROOT_DIR / d
        if p.exists():
            safe_move(p, LEGACY_DASHBOARDS / d)

    print("\n[SUCCESS] Reorganization complete!")

if __name__ == "__main__":
    reorganize()
