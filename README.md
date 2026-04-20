# DarkScan — Dark Pattern Detector

A Streamlit app that scrapes any URL and flags manipulative UI patterns with severity scores.

## What it detects

| # | Pattern | Severity |
|---|---------|----------|
| 01 | Fake urgency & false scarcity ("Only 2 left!", "Sale ends in 10 mins") | High |
| 02 | Hidden costs & fine-print pricing (fees revealed at checkout) | High |
| 03 | Confirm-shaming ("No thanks, I hate saving money") | High |
| 04 | Pre-ticked marketing consent checkboxes | **Critical** |
| 05 | De-emphasized cancel/decline buttons (visual misdirection) | Medium |
| 06 | Roach motel (cancel by phone only, hard exit) | **Critical** |
| 07 | Privacy zuckering (vague "trusted partners" data sharing) | High |
| 08 | Disguised ads & fake download buttons | High |
| 09 | Trick questions & double-negative opt-outs | High |

## Setup

```bash
# 1. Clone / download this folder
git clone https://github.com/yourusername/darkscan
cd darkscan

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

## Deploy to Streamlit Cloud (free)

1. Push to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo → select `app.py` → Deploy
4. Share the URL — it refreshes on every visit, always live

## How scoring works

Each finding adds to the manipulation score (max 100):
- Critical: +30 points
- High: +20 points  
- Medium: +10 points
- Low: +5 points

**Score guide:**
- 0 = Clean
- 1–19 = Mildly suspicious
- 20–39 = Moderately manipulative
- 40–59 = Highly manipulative
- 60+ = Extremely predatory

## Limitations

- JavaScript-rendered content is not detected (add Playwright for JS support)
- Some patterns require multiple page views to confirm (e.g. countdown that resets)
- Results are heuristic-based — always verify manually

## Legal

This tool is for educational and consumer awareness purposes. 
Dark patterns identified may be subject to GDPR, FTC, and EU DSA regulations.
