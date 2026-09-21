"""Generates the 3 sample product-manual PDFs used as the corpus for RAG
Model 3. Run once to (re)create the PDFs under data/.

Usage:
    python generate_sample_pdfs.py
"""
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

DOCUMENTS = {
    "trailhead_gps_watch_manual.pdf": (
        "Trailhead GPS Watch - User Manual",
        [
            "The Trailhead GPS Watch tracks distance, pace, elevation gain, "
            "and heart rate for running, hiking, and cycling activities. "
            "A full charge provides up to 14 days of battery life in "
            "smartwatch mode, or 30 hours in continuous GPS tracking mode.",

            "To pair the watch with your phone, hold the side button for "
            "3 seconds until the Bluetooth icon flashes, then open the "
            "Trailhead app and select Add Device. The watch supports iOS "
            "13 and above, and Android 9 and above.",

            "The watch is water resistant to 50 meters and is safe for "
            "swimming and showering, but should not be used for scuba "
            "diving or high-pressure water activities such as jet skiing.",

            "If the watch does not respond, hold the side button and the "
            "down button together for 10 seconds to force a restart. This "
            "will not erase saved activities, which are synced to the "
            "cloud automatically once the watch reconnects to Wi-Fi.",

            "The warranty covers manufacturing defects for 2 years from "
            "the date of purchase. Water damage caused by exceeding the "
            "50 meter depth rating is not covered under warranty.",
        ],
    ),
    "aurora_wifi_router_manual.pdf": (
        "Aurora Mesh Wi-Fi Router - Setup Guide",
        [
            "The Aurora Mesh Router supports Wi-Fi 6 and covers up to "
            "2,000 square feet per unit. For larger homes, up to 5 Aurora "
            "units can be linked together in a mesh network for extended "
            "coverage.",

            "To set up the router, connect it to your modem using the "
            "included Ethernet cable, plug in the power adapter, and wait "
            "for the status light to turn solid blue, which takes about "
            "90 seconds. Then download the Aurora app to complete setup.",

            "The default network name and password are printed on a "
            "sticker on the bottom of the router. We strongly recommend "
            "changing the default password during setup using the Aurora "
            "app under Network Settings > Wi-Fi Password.",

            "Parental controls can be enabled per device under Family "
            "Profiles in the app, allowing you to pause internet access, "
            "set bedtime schedules, and block specific website categories.",

            "If the internet connection drops frequently, try moving the "
            "router at least 2 feet away from other electronics, and check "
            "for firmware updates under Settings > About > Check for "
            "Updates. The router updates its firmware automatically by "
            "default.",
        ],
    ),
    "brewmaster_coffee_machine_manual.pdf": (
        "BrewMaster Pro Coffee Machine - Care and Use",
        [
            "The BrewMaster Pro heats water to a consistent 200 degrees "
            "Fahrenheit for optimal extraction and supports both ground "
            "coffee and compatible single-serve pods.",

            "Before first use, run one full brew cycle with only water and "
            "no coffee to clean the internal lines. Repeat this cleaning "
            "cycle every 60 days, or the descale indicator light will turn "
            "on automatically based on usage.",

            "To descale the machine, fill the water tank with a mixture of "
            "one part white vinegar to two parts water, run a full brew "
            "cycle, then run two additional cycles with clean water to "
            "rinse the lines completely.",

            "The machine will automatically power off after 30 minutes of "
            "inactivity to save energy. Press the power button once to "
            "wake it; it will be ready to brew within 15 seconds.",

            "Do not immerse the base unit in water. The water tank, drip "
            "tray, and pod holder are dishwasher safe on the top rack "
            "only. The warranty is void if unauthorized descaling "
            "solutions other than food-grade citric acid or white vinegar "
            "are used.",
        ],
    ),
}


def build_pdf(path: str, title: str, paragraphs):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path, pagesize=letter)
    story = [Paragraph(title, styles["Title"]), Spacer(1, 0.3 * inch)]
    for para in paragraphs:
        story.append(Paragraph(para, styles["BodyText"]))
        story.append(Spacer(1, 0.2 * inch))
    doc.build(story)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for filename, (title, paragraphs) in DOCUMENTS.items():
        path = os.path.join(DATA_DIR, filename)
        build_pdf(path, title, paragraphs)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
