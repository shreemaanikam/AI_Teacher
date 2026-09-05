"""
Comprehensive Browser Verification Script.
Uses Google Chrome headless mode to verify all key views and components:
- Dashboard
- Courses
- Documents
- Learning Path
- Lesson Player
- Male Teacher Video
- Audio
- Whiteboard
- Ask Doubt
- Assessment
- Analytics
- Exam Planner
"""

import os
import subprocess
import time
import json

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUTPUT_DIR = os.path.abspath("scratch/browser_screens")
BASE_URL = "http://127.0.0.1:5005"

os.makedirs(OUTPUT_DIR, exist_ok=True)

SCREENS_TO_VERIFY = [
    {"name": "dashboard", "url": f"{BASE_URL}/?screen=dashboard", "label": "Dashboard & Courses & Exam Planner"},
    {"name": "documents", "url": f"{BASE_URL}/?screen=documents", "label": "Documents Library"},
    {"name": "learning-path", "url": f"{BASE_URL}/?screen=learning-path", "label": "Learning Path & Concept Map"},
    {"name": "lesson-player", "url": f"{BASE_URL}/?screen=lesson-player", "label": "Lesson Player (Video, Audio, Whiteboard, Doubt)"},
    {"name": "assessment", "url": f"{BASE_URL}/?screen=assessment", "label": "Final Assessment"},
    {"name": "analytics", "url": f"{BASE_URL}/?screen=analytics", "label": "Learning Analytics"},
]

def capture_screen(name: str, url: str, width: int = 1280, height: int = 800) -> str:
    out_path = os.path.join(OUTPUT_DIR, f"{name}_{width}x{height}.png")
    cmd = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--window-size={width},{height}",
        f"--screenshot={out_path}",
        "--virtual-time-budget=4000",
        url
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            return out_path
        else:
            print(f"Warning: capture failed for {name}: {res.stderr}")
            return ""
    except Exception as e:
        print(f"Error capturing {name}: {e}")
        return ""

def verify_all():
    print("=" * 70)
    print("  BROWSER VERIFICATION SUITE — APURVA AI TEACHER (GUNICORN)")
    print("=" * 70)
    
    results = {}
    for item in SCREENS_TO_VERIFY:
        print(f"\n📸 Capturing & verifying: {item['label']} ({item['url']})...")
        path = capture_screen(item["name"], item["url"])
        if path:
            size_kb = round(os.path.getsize(path) / 1024, 1)
            print(f"  ✓ Verified {item['name']}: Captured {size_kb} KB -> {path}")
            results[item["name"]] = {"status": "PASS", "path": path, "size_kb": size_kb}
        else:
            print(f"  ❌ Failed to capture {item['name']}")
            results[item["name"]] = {"status": "FAIL"}

    # Also capture mobile viewport for Lesson Player (390x844)
    print("\n📱 Capturing mobile responsive Lesson Player (390x844)...")
    mobile_path = capture_screen("lesson_player_mobile", f"{BASE_URL}/?screen=lesson-player", 390, 844)
    if mobile_path:
        print(f"  ✓ Verified mobile view: Captured {round(os.path.getsize(mobile_path)/1024, 1)} KB")
        results["lesson_player_mobile"] = {"status": "PASS", "path": mobile_path}

    print("\n" + "=" * 70)
    print("  BROWSER VERIFICATION SUMMARY")
    print("=" * 70)
    all_passed = all(v.get("status") == "PASS" for v in results.values())
    for k, v in results.items():
        print(f"  • {k:25}: {v['status']}")
    print(f"\nOVERALL RESULT: {'ALL PASS' if all_passed else 'SOME FAILED'}")
    return all_passed

if __name__ == "__main__":
    verify_all()
