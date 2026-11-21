# Builds data.json for the Kindle dashboard: date, Portland weather, shared calendar events.
# Runs inside GitHub Actions on a schedule. Calendar comes from the CAL_ICS_URL secret when set,
# otherwise from events.json. If a source fails, the previous values are kept.
import json, os, datetime, urllib.request
from zoneinfo import ZoneInfo
PT = ZoneInfo("America/Los_Angeles")
now = datetime.datetime.now(PT); today = now.date()
try: D = json.load(open("data.json"))
except Exception: D = {}
D["date"] = now.strftime("%A, %b ") + str(now.day)
h = now.hour
D["greeting"] = "Good morning," if h < 12 else "Good afternoon," if h < 17 else "Good evening,"
D.setdefault("j", []); D.setdefault("b", [])
for k in ("quote", "author", "question"): D.pop(k, None)
WMO = {0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Cloudy", 45: "Fog", 48: "Fog", 51: "Drizzle", 53: "Drizzle",
       55: "Drizzle", 56: "Freezing drizzle", 57: "Freezing drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
       66: "Freezing rain", 67: "Freezing rain", 71: "Light snow", 73: "Snow", 75: "Heavy snow", 77: "Snow", 80: "Showers",
       81: "Showers", 82: "Heavy showers", 85: "Snow showers", 86: "Snow showers", 95: "Thunderstorms", 96: "Thunderstorms",
       99: "Thunderstorms"}
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "home-hub"})
    return urllib.request.urlopen(req, timeout=30).read()
try:
    w = json.loads(get("https://api.open-meteo.com/v1/forecast?latitude=45.5579&longitude=-122.6465"
                       "&current=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min,"
                       "precipitation_probability_max&temperature_unit=fahrenheit&timezone=America%2FLos_Angeles&forecast_days=6"))
    dl = w["daily"]; r = lambda x: str(round(x))
    D["weather"] = {"temp": r(w["current"]["temperature_2m"]), "cond": WMO.get(w["current"]["weather_code"], "Cloudy"),
                    "high": r(dl["temperature_2m_max"][0]), "low": r(dl["temperature_2m_min"][0]),
                    "rain": r(dl["precipitation_probability_max"][0] or 0)}
    days = []
    for i in range(5):
        d = datetime.date.fromisoformat(dl["time"][i])
        days.append(["TODAY" if i == 0 else d.strftime("%a").upper(), r(dl["temperature_2m_max"][i]), r(dl["temperature_2m_min"][i])])
    D["days"] = days
except Exception as e:
    print("weather unreachable:", e)
    D["days"] = [["TODAY" if i == 0 else (today + datetime.timedelta(days=i)).strftime("%a").upper(), "--", "--"] for i in range(5)]
def clean(t):
    t = (t or "Busy").strip()
    for p in ("Johnathon: ", "Bee: "):
        if t.startswith(p): t = t[len(p):]
    return t
def load_events():
    # returns list of (start datetime in PT, end datetime in PT, all_day, title)
    end = today + datetime.timedelta(days=5); out = []
    url = os.environ.get("CAL_ICS_URL", "").strip()
    if url:
        import icalendar, recurring_ical_events
        cal = icalendar.Calendar.from_ical(get(url))
        for ev in recurring_ical_events.of(cal).between(today, end):
            s = ev["DTSTART"].dt; e = ev["DTEND"].dt if ev.get("DTEND") else s
            allday = not isinstance(s, datetime.datetime)
            if allday:
                s2 = datetime.datetime.combine(s, datetime.time(0), PT); e2 = datetime.datetime.combine(e, datetime.time(0), PT)
            else:
                s2 = (s if s.tzinfo else s.replace(tzinfo=PT)).astimezone(PT); e2 = (e if e.tzinfo else e.replace(tzinfo=PT)).astimezone(PT)
            out.append((s2, e2, allday, clean(str(ev.get("SUMMARY", "")))))
    else:
        for ev in json.load(open("events.json")):
            allday = len(ev["start"]) == 10
            s2 = datetime.datetime.fromisoformat(ev["start"]).replace(tzinfo=PT)
            e2 = datetime.datetime.fromisoformat(ev["end"]).replace(tzinfo=PT) if ev.get("end") else s2 + datetime.timedelta(hours=24 if allday else 1)
            out.append((s2, e2, allday, clean(ev["title"])))
    return out
try:
    rows = []
    for s, e, allday, title in sorted(load_events(), key=lambda x: (x[0].date(), not x[2], x[0])):
        n = (s.date() - today).days
        if n < 0 or n > 4 or e <= now: continue
        lab = "Today" if n == 0 else s.strftime("%a")
        when = lab + " all day" if allday else lab + " " + s.strftime("%I:%M %p").lstrip("0")
        rows.append([str(n), "day" if n == 1 else "days", title, when])
    D["events"] = rows[:10]
except Exception as e:
    print("calendar unreachable:", type(e).__name__)
json.dump(D, open("data.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(D["date"], len(D.get("events", [])), "events")
