from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dateutil import parser as dateparser
import pandas as pd
import time
import re

# ─────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

all_data = []


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def get_sentiment(text):
    text = text.lower()
    if any(w in text for w in ["cancelled", "arrested", "hospitalised", "forcibly", "clash", "detained", "leak", "corrupt"]):
        return "Highly Negative"
    elif any(w in text for w in ["protest", "demand", "criticism", "concern", "irregularit"]):
        return "Negative"
    elif any(w in text for w in ["resolved", "announced", "re-exam", "secured", "dialogue", "ended"]):
        return "Neutral"
    elif any(w in text for w in ["reform", "measures", "accountability", "transparent"]):
        return "Positive"
    else:
        return "Neutral"


def get_escalation(text):
    text = text.lower()
    if any(w in text for w in ["arrested", "hospitalised", "forcibly", "detained", "court", "cbi"]):
        return 4
    elif any(w in text for w in ["march", "clash", "hunger strike", "barricade"]):
        return 3
    elif any(w in text for w in ["protest", "demand", "petition", "rally"]):
        return 2
    elif any(w in text for w in ["allegation", "concern", "question"]):
        return 1
    else:
        return 0


def normalize_date(d):
    """Convert any date string to YYYY-MM-DD; fallback to 2026-01-01."""
    try:
        return dateparser.parse(str(d)).strftime("%Y-%m-%d")
    except Exception:
        return "2026-01-01"


# ─────────────────────────────────────────
# SOURCE 1: WIKIPEDIA
# ─────────────────────────────────────────
print("\n[1/3] Scraping Wikipedia...")

try:
    driver.get("https://en.wikipedia.org/wiki/2026_NEET_controversy")
    time.sleep(4)

    paragraphs = driver.find_elements(By.TAG_NAME, "p")

    for p in paragraphs:
        text = p.text.strip()
        if len(text) < 30:
            continue

        date_match = re.search(r'(\d{1,2}\s+\w+\s+2026|\w+\s+\d{1,2},?\s+2026)', text)
        date_str = date_match.group(0) if date_match else "2026-01-01"

        location = "Pan-India"
        for loc in ["Delhi", "Rajasthan", "Maharashtra", "Pune", "Sikar", "Mumbai", "Chennai", "Bengaluru"]:
            if loc in text:
                location = loc
                break

        all_data.append({
            "date": normalize_date(date_str),
            "event_summary": text[:200],
            "location": location,
            "protest_type": (
                "PIL Filed" if "PIL" in text else
                "Hunger Strike" if "hunger strike" in text.lower() else
                "Street Protest" if "protest" in text.lower() else
                "None"
            ),
            "participants_est": 0,
            "escalation_level": get_escalation(text),
            "sentiment": get_sentiment(text),
            "source": "Wikipedia"
        })

    wiki_count = len([d for d in all_data if d["source"] == "Wikipedia"])
    print(f"  ✓ Wikipedia: {wiki_count} rows")

except Exception as e:
    print(f"  ✗ Wikipedia failed: {e}")


# ─────────────────────────────────────────
# SOURCE 2: BRUT MEDIA TIMELINE
# ─────────────────────────────────────────
print("\n[2/3] Adding Brut Media timeline...")

brut_events = [
    ("2026-05-03", "NEET-UG 2026 conducted for ~22 lakh candidates; paper leak allegations surface", "Pan-India", "None", 2200000, 1, "Negative"),
    ("2026-05-12", "NTA cancels NEET-UG 2026; CBI handed investigation; re-exam announced", "Pan-India", "PIL Filed", 0, 4, "Highly Negative"),
    ("2026-05-13", "Student protests begin in Delhi and other cities demanding transparency", "Delhi", "Street Protest", 5000, 2, "Negative"),
    ("2026-06-06", "CJP begins protest at Jantar Mantar demanding Education Minister's resignation", "Delhi", "Street Protest", 500, 3, "Negative"),
    ("2026-06-21", "NEET re-exam conducted with IAF aircraft transporting papers; tight security", "Pan-India", "None", 0, 1, "Neutral"),
    ("2026-06-28", "Sonam Wangchuk begins indefinite hunger strike at Jantar Mantar", "Delhi", "Hunger Strike", 1000, 3, "Negative"),
    ("2026-07-16", "Delhi High Court intervenes; orders medical care for Wangchuk", "Delhi", "PIL Filed", 0, 3, "Negative"),
    ("2026-07-16", "NEET re-exam results declared; fresh protests over score discrepancies", "Pan-India", "Street Protest", 2000, 2, "Negative"),
    ("2026-07-18", "Delhi Police forcibly removes Wangchuk to Medanta Hospital after health deteriorates", "Delhi", "Hunger Strike", 300, 4, "Highly Negative"),
    ("2026-07-20", "Sansad Chalo march; thousands detained; clashes at barricades", "Delhi", "Street Protest", 10000, 5, "Highly Negative"),
    ("2026-07-23", "PM Modi announces fast-track courts, anti-paper-leak legislation", "Pan-India", "None", 0, 2, "Neutral"),
    ("2026-07-24", "Wangchuk ends 26-day hunger strike after talks with JP Nadda and Jitendra Singh", "Delhi", "Hunger Strike", 0, 2, "Positive"),
    ("2026-07-25", "Education Minister Dharmendra Pradhan resigns under mounting pressure", "Delhi", "None", 0, 5, "Highly Negative"),
]

for event in brut_events:
    all_data.append({
        "date": event[0],           # already YYYY-MM-DD
        "event_summary": event[1],
        "location": event[2],
        "protest_type": event[3],
        "participants_est": event[4],
        "escalation_level": event[5],
        "sentiment": event[6],
        "source": "Brut Media"
    })

print(f"  ✓ Brut Media: {len(brut_events)} rows")


# ─────────────────────────────────────────
# SOURCE 3: NDTV HEADLINES
# ─────────────────────────────────────────
print("\n[3/3] Scraping NDTV headlines...")

try:
    driver.get("https://www.ndtv.com/topic/neet-paper-leak")
    time.sleep(5)

    # Broadened selectors to catch more elements
    headlines = driver.find_elements(
        By.CSS_SELECTOR,
        "h2, h3, a[href*='neet'], .news-card-title, .list-title, .story__headline, span.story__headline"
    )

    ndtv_count = 0
    for h in headlines:
        text = h.text.strip()
        if len(text) < 20:
            continue
        if "NEET" not in text.upper() and "paper leak" not in text.lower():
            continue

        all_data.append({
            "date": "2026-01-01",   # NDTV doesn't expose clean dates here
            "event_summary": text[:200],
            "location": "Pan-India",
            "protest_type": "None",
            "participants_est": 0,
            "escalation_level": get_escalation(text),
            "sentiment": get_sentiment(text),
            "source": "NDTV"
        })
        ndtv_count += 1

    print(f"  ✓ NDTV: {ndtv_count} rows")

except Exception as e:
    print(f"  ✗ NDTV failed: {e}")


# ─────────────────────────────────────────
# MERGE + CLEAN + SAVE
# ─────────────────────────────────────────
print("\n[Merging and cleaning data...]")

df = pd.DataFrame(all_data)

# Strip Wikipedia citation markers like [1], [2]
df["event_summary"] = df["event_summary"].str.replace(r'\[.*?\]', '', regex=True).str.strip()

# Rename columns to match DB table exactly
df = df.rename(columns={
    "participants_est": "participants",
    "escalation_level": "escalation"
})

# Ensure numeric types
df["participants"] = pd.to_numeric(df["participants"], errors="coerce").fillna(0).astype(int)
df["escalation"] = pd.to_numeric(df["escalation"], errors="coerce").fillna(0).astype(int)

# Drop duplicates and empty rows
df = df.drop_duplicates(subset=["event_summary"])
df = df[df["event_summary"].str.len() > 20]
df = df.reset_index(drop=True)

# Save
output_path = "neet_protest_dataset.csv"
df.to_csv(output_path, index=False)

print(f"\n✅ Done! Final dataset: {len(df)} rows, {len(df.columns)} columns")
print(f"📁 Saved to: {output_path}")

print(f"\nSource breakdown:")
print(df["source"].value_counts())

print(f"\nSentiment breakdown:")
print(df["sentiment"].value_counts())          # ← fixed: was "sentiment_label"

print(f"\nEscalation distribution:")
print(df["escalation"].value_counts().sort_index())

driver.quit()