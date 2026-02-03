import os
import json
import subprocess
import platform
import requests
from datetime import datetime
import uuid
import zipfile
import secrets
import string

# ----------------- Optional Dependencies -----------------

# System info
try:
    import psutil
except ImportError:
    psutil = None

# DuckDuckGo search
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

# Wikipedia
try:
    import wikipedia
except ImportError:
    wikipedia = None

# BeautifulSoup for HTML parsing
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# Translation
try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None

# Language detection
try:
    from langdetect import detect as langdetect_detect
except ImportError:
    langdetect_detect = None

# Transformers for NLP (sentiment, summarization)
try:
    from transformers import pipeline as hf_pipeline
except ImportError:
    hf_pipeline = None

# Sympy for symbolic math
try:
    import sympy as sp
except ImportError:
    sp = None

# Geopy for geocoding
try:
    from geopy.geocoders import Nominatim
except ImportError:
    Nominatim = None

# Pillow for image info
try:
    from PIL import Image
except ImportError:
    Image = None

# Text-to-speech
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

# yfinance for ticker prices
try:
    import yfinance as yf
except ImportError:
    yf = None

# Markdown
try:
    import markdown as md_lib
except ImportError:
    md_lib = None

# Timezone conversion
try:
    import pytz
except ImportError:
    pytz = None

# RSS
try:
    import feedparser
except ImportError:
    feedparser = None

# Holidays
try:
    import holidays
except ImportError:
    holidays = None

# QR code
try:
    import qrcode
except ImportError:
    qrcode = None

# PDF
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# Network speed test
try:
    import speedtest
except ImportError:
    speedtest = None

# Clipboard
try:
    import pyperclip
except ImportError:
    pyperclip = None

# Code formatter
try:
    import black
except ImportError:
    black = None

# Linter
try:
    from flake8.api import legacy as flake8_legacy
except ImportError:
    flake8_legacy = None

# ========================= CORE TOOLS =========================

def get_weather(city: str):
    """Get current weather for a city."""
    try:
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return f"The weather in {city} is {response.text.strip()}."
        return f"Error: Could not fetch weather (Status {response.status_code})"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"


def run_command(cmd: str):
    """Execute a shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip() if result.stdout else "Command executed successfully (no output)."
        else:
            return f"Command failed:\nStdout: {result.stdout}\nStderr: {result.stderr}"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def web_search(query: str):
    """Search the web using DuckDuckGo."""
    if not DDGS:
        return "Error: duckduckgo-search library not installed."
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No results found."
        formatted_results = "\n".join(
            [f"- {r['title']}: {r['href']}\n  {r['body']}" for r in results]
        )
        return formatted_results
    except Exception as e:
        return f"Error searching web: {str(e)}"


def get_system_info(_=None):
    """Get system information (CPU, RAM, OS)."""
    info = [f"System: {platform.system()} {platform.release()}"]

    if psutil:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        info.append(f"CPU Usage: {cpu_usage}%")
        info.append(f"RAM: {ram.percent}% used ({ram.used // (1024**3)}GB / {ram.total // (1024**3)}GB)")
    else:
        info.append("Note: Install 'psutil' for detailed CPU/RAM stats.")

    return "\n".join(info)


def read_file(path: str):
    """Read content of a file."""
    try:
        if not os.path.exists(path):
            return f"Error: File '{path}' does not exist."
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(path: str, content: str):
    """Write content to a file."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"


def calculate(expression: str):
    """Evaluate a mathematical expression (simple eval, restricted builtins)."""
    try:
        allowed_names = {"abs": abs, "round": round, "min": min, "max": max, "pow": pow}
        return str(eval(expression, {"__builtins__": None}, allowed_names))
    except Exception as e:
        return f"Error calculating: {str(e)}"


def get_time(_=None):
    """Get current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ===================== FIRST BATCH OF EXTRA TOOLS =====================

# 1) Wikipedia summary
def wiki_summary(query: str, sentences: int = 3):
    """Get a short summary from Wikipedia."""
    if wikipedia is None:
        return "Error: 'wikipedia' library not installed."
    try:
        return wikipedia.summary(query, sentences=sentences)
    except Exception as e:
        return f"Error fetching summary: {e}"


# 2) Currency converter
def convert_currency(amount: float, from_cur: str, to_cur: str):
    """Convert currency using exchangerate.host."""
    try:
        url = f"https://api.exchangerate.host/convert?from={from_cur}&to={to_cur}&amount={amount}"
        r = requests.get(url, timeout=5).json()
        if r.get("result") is None:
            return "Error converting currency."
        return f"{amount} {from_cur} = {r['result']} {to_cur}"
    except Exception as e:
        return f"Error converting currency: {e}"


# 3) IP geolocation
def ip_geolocate(ip: str = ""):
    """Geolocate an IP using ip-api.com."""
    try:
        url = f"http://ip-api.com/json/{ip or ''}"
        data = requests.get(url, timeout=5).json()
        if data.get("status") != "success":
            return f"Error: {data.get('message', 'lookup failed')}"
        return f"{data['query']}: {data['country']}, {data['regionName']}, {data['city']}"
    except Exception as e:
        return f"Error geolocating IP: {e}"


# 4) Public IP
def get_public_ip(_=None):
    """Get public IP address."""
    try:
        return requests.get("https://api64.ipify.org?format=text", timeout=5).text.strip()
    except Exception as e:
        return f"Error getting IP: {e}"


# 5) Fetch page title
def fetch_page_title(url: str):
    """Fetch the <title> of a URL."""
    if BeautifulSoup is None:
        return "Error: 'beautifulsoup4' library not installed."
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string if soup.title else "No title found"
        return title.strip()
    except Exception as e:
        return f"Error fetching title: {e}"


# 6) Translate text
def translate_text(text: str, target_lang: str = "en"):
    """Translate text using GoogleTranslator (deep-translator)."""
    if GoogleTranslator is None:
        return "Error: 'deep-translator' library not installed."
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        return f"Error translating text: {e}"


# 7) Detect language
def detect_language(text: str):
    """Detect language of text."""
    if langdetect_detect is None:
        return "Error: 'langdetect' library not installed."
    try:
        lang = langdetect_detect(text)
        return f"Detected language: {lang}"
    except Exception as e:
        return f"Error detecting language: {e}"


# 8) Sentiment analysis
_sentiment_pipe = None
def sentiment(text: str):
    """Sentiment analysis using transformers."""
    global _sentiment_pipe
    if hf_pipeline is None:
        return "Error: 'transformers' library not installed."
    try:
        if _sentiment_pipe is None:
            _sentiment_pipe = hf_pipeline("sentiment-analysis")
        result = _sentiment_pipe(text)[0]
        return f"Label: {result['label']}, score: {result['score']:.3f}"
    except Exception as e:
        return f"Error in sentiment analysis: {e}"


# 9) Text summarization
_summarizer = None
def summarize_text(text: str, max_tokens: int = 130):
    """Summarize text using transformers."""
    global _summarizer
    if hf_pipeline is None:
        return "Error: 'transformers' library not installed."
    try:
        if _summarizer is None:
            _summarizer = hf_pipeline("summarization")
        summary = _summarizer(
            text, max_length=max_tokens, min_length=30, do_sample=False
        )[0]["summary_text"]
        return summary
    except Exception as e:
        return f"Error summarizing: {e}"


# 10) Solve equation (symbolic)
def solve_equation(equation: str, var: str = "x"):
    """Solve a simple equation like '2*x + 3 = 7'."""
    if sp is None:
        return "Error: 'sympy' library not installed."
    try:
        x = sp.symbols(var)
        left, right = equation.split("=")
        expr = sp.Eq(sp.sympify(left), sp.sympify(right))
        sol = sp.solve(expr, x)
        return f"Solutions for {var}: {sol}"
    except Exception as e:
        return f"Error solving equation: {e}"


# 11) Disk usage
def get_disk_usage(path: str = "/"):
    """Get disk usage for a path."""
    if psutil is None:
        return "Error: 'psutil' library not installed."
    try:
        du = psutil.disk_usage(path)
        return (
            f"Disk usage for {path}: {du.percent}% used "
            f"({du.used // (1024**3)}GB / {du.total // (1024**3)}GB)"
        )
    except Exception as e:
        return f"Error getting disk usage: {e}"


# 12) List processes
def list_processes(limit: int = 10):
    """List top processes by CPU usage."""
    if psutil is None:
        return "Error: 'psutil' library not installed."
    try:
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent"]):
            procs.append(p.info)
        procs = sorted(
            procs, key=lambda x: x.get("cpu_percent", 0), reverse=True
        )[:limit]
        return "\n".join(
            [f"{p['pid']} {p['name']} CPU:{p['cpu_percent']}%" for p in procs]
        ) or "No processes found."
    except Exception as e:
        return f"Error listing processes: {e}"


# 13) List files
def list_files(path: str = "."):
    """List files in a directory."""
    try:
        if not os.path.exists(path):
            return f"Path '{path}' does not exist."
        files = os.listdir(path)
        return "\n".join(files) if files else "Directory is empty."
    except Exception as e:
        return f"Error listing files: {e}"


# 14–15) Simple TODO manager
TODO_FILE = "todos.json"

def add_todo(item: str):
    """Add a todo item."""
    try:
        todos = []
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, "r", encoding="utf-8") as f:
                todos = json.load(f)
        todos.append({"item": item, "done": False})
        with open(TODO_FILE, "w", encoding="utf-8") as f:
            json.dump(todos, f, indent=2)
        return "Todo added."
    except Exception as e:
        return f"Error adding todo: {e}"


def list_todos(_=None):
    """List todo items."""
    try:
        if not os.path.exists(TODO_FILE):
            return "No todos yet."
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            todos = json.load(f)
        if not todos:
            return "No todos yet."
        lines = []
        for i, t in enumerate(todos, 1):
            lines.append(f"[{'x' if t.get('done') else ' '}] {i}. {t.get('item')}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error listing todos: {e}"


# 16) Timezone conversion
def convert_time(time_str: str, from_tz: str, to_tz: str,
                 fmt: str = "%Y-%m-%d %H:%M"):
    """Convert time between timezones."""
    if pytz is None:
        return "Error: 'pytz' library not installed."
    try:
        from_zone = pytz.timezone(from_tz)
        to_zone = pytz.timezone(to_tz)
        dt = datetime.strptime(time_str, fmt)
        dt = from_zone.localize(dt).astimezone(to_zone)
        return dt.strftime(fmt)
    except Exception as e:
        return f"Error converting time: {e}"


# 17–18) Geocoding & reverse geocoding
_geocoder = None
if Nominatim is not None:
    _geocoder = Nominatim(user_agent="agent_tools")

def geocode_address(address: str):
    """Address -> coordinates (lat, lon)."""
    if _geocoder is None:
        return "Error: 'geopy' library not installed."
    try:
        loc = _geocoder.geocode(address)
        if not loc:
            return "Address not found."
        return f"{loc.address}\nLat: {loc.latitude}, Lon: {loc.longitude}"
    except Exception as e:
        return f"Error geocoding address: {e}"


def reverse_geocode(lat: float, lon: float):
    """Coordinates -> address."""
    if _geocoder is None:
        return "Error: 'geopy' library not installed."
    try:
        loc = _geocoder.reverse((lat, lon))
        if not loc:
            return "Location not found."
        return loc.address
    except Exception as e:
        return f"Error in reverse geocoding: {e}"


# 19) Image info
def image_info(path: str):
    """Get basic image info."""
    if Image is None:
        return "Error: 'Pillow' library not installed."
    try:
        if not os.path.exists(path):
            return f"File '{path}' not found."
        with Image.open(path) as img:
            return f"Format: {img.format}, Size: {img.size}, Mode: {img.mode}"
    except Exception as e:
        return f"Error reading image: {e}"


# 20) Text-to-speech
_tts_engine = None
def text_to_speech(text: str, out_file: str = "output.wav"):
    """Text to speech (saves audio to a file)."""
    global _tts_engine
    if pyttsx3 is None:
        return "Error: 'pyttsx3' library not installed."
    try:
        if _tts_engine is None:
            _tts_engine = pyttsx3.init()
        _tts_engine.save_to_file(text, out_file)
        _tts_engine.runAndWait()
        return f"Saved speech to {out_file}"
    except Exception as e:
        return f"Error in TTS: {e}"


# 21) Ticker price
def get_ticker_price(symbol: str):
    """Get current price for a stock/crypto ticker."""
    if yf is None:
        return "Error: 'yfinance' library not installed."
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if hist.empty:
            return f"No data for {symbol}."
        price = hist["Close"].iloc[-1]
        return f"{symbol} current price: {price}"
    except Exception as e:
        return f"Error fetching price: {e}"


# 22) Markdown -> HTML
def markdown_to_html(text: str):
    """Convert markdown to HTML."""
    if md_lib is None:
        return "Error: 'markdown' library not installed."
    try:
        return md_lib.markdown(text)
    except Exception as e:
        return f"Error converting markdown: {e}"


# ===================== SECOND BATCH OF EXTRA TOOLS =====================

# 23) Hacker News top stories
def hn_top_stories(limit: int = 5):
    """Get top stories from Hacker News."""
    try:
        top_ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=5
        ).json()[:limit]
        stories = []
        for sid in top_ids:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                timeout=5
            ).json()
            stories.append(f"- {item.get('title')} ({item.get('url', 'no url')})")
        return "\n".join(stories)
    except Exception as e:
        return f"Error fetching Hacker News: {e}"


# 24) RSS feed reader
def rss_headlines(url: str, limit: int = 5):
    """Get headlines from an RSS feed."""
    if feedparser is None:
        return "Error: 'feedparser' library not installed."
    try:
        feed = feedparser.parse(url)
        entries = feed.entries[:limit]
        return "\n".join([f"- {e.title} ({e.link})" for e in entries])
    except Exception as e:
        return f"Error reading feed: {e}"


# 25) Public holiday checker
def is_public_holiday(date_str: str, country: str = "IN"):
    """Check if a given date (YYYY-MM-DD) is a public holiday in a given country."""
    if holidays is None:
        return "Error: 'holidays' library not installed."
    try:
        year = int(date_str.split("-")[0])
        country_holidays = holidays.CountryHoliday(country, years=year)
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        if dt in country_holidays:
            return f"{date_str} is a holiday: {country_holidays[dt]}"
        else:
            return f"{date_str} is not a public holiday in {country}."
    except Exception as e:
        return f"Error checking holiday: {e}"


# 26) Strong password generator
def generate_password(length: int = 16):
    """Generate a random strong password."""
    chars = string.ascii_letters + string.digits + string.punctuation
    pw = "".join(secrets.choice(chars) for _ in range(length))
    return pw


# 27) UUID generator
def generate_uuid(_=None):
    """Generate a random UUID v4."""
    return str(uuid.uuid4())


# 28) JSON pretty printer / validator
def pretty_json(raw: str):
    """Validate and pretty-print JSON."""
    try:
        obj = json.loads(raw)
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Invalid JSON: {e}"


# 29) URL shortener (TinyURL)
def shorten_url(url: str):
    """Shorten a URL using TinyURL."""
    try:
        resp = requests.get("https://tinyurl.com/api-create.php", params={"url": url}, timeout=5)
        if resp.status_code == 200:
            return resp.text.strip()
        return f"Error shortening URL: status {resp.status_code}"
    except Exception as e:
        return f"Error shortening URL: {e}"


# 30) QR code generator
def generate_qr(data: str, filename: str = "qr.png"):
    """Generate a QR code image."""
    if qrcode is None:
        return "Error: 'qrcode' library not installed."
    try:
        img = qrcode.make(data)
        img.save(filename)
        return f"QR code saved to {filename}"
    except Exception as e:
        return f"Error generating QR: {e}"


# 31) Zip path (file/folder)
def zip_path(path: str, zip_name: str = "archive.zip"):
    """Zip a file or folder."""
    try:
        if not os.path.exists(path):
            return f"Path '{path}' does not exist."
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for f in files:
                        full = os.path.join(root, f)
                        arcname = os.path.relpath(full, start=path)
                        zf.write(full, arcname)
            else:
                zf.write(path, os.path.basename(path))
        return f"Created zip: {zip_name}"
    except Exception as e:
        return f"Error zipping path: {e}"


# 32) Unzip archive
def unzip_file(zip_path: str, dest: str = "./unzipped"):
    """Unzip a zip file."""
    try:
        if not os.path.exists(zip_path):
            return f"Zip file '{zip_path}' does not exist."
        os.makedirs(dest, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(dest)
        return f"Extracted to {dest}"
    except Exception as e:
        return f"Error unzipping file: {e}"


# 33) PDF text extractor
def pdf_to_text(path: str):
    """Extract text from a PDF file."""
    if PyPDF2 is None:
        return "Error: 'PyPDF2' library not installed."
    try:
        if not os.path.exists(path):
            return f"File '{path}' not found."
        text = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)
    except Exception as e:
        return f"Error reading PDF: {e}"


# 34–35) Notes manager
NOTES_FILE = "notes.json"

def add_note(text: str):
    """Add a note."""
    try:
        notes = []
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                notes = json.load(f)
        notes.append({"text": text, "time": datetime.now().isoformat()})
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=2)
        return "Note added."
    except Exception as e:
        return f"Error adding note: {e}"


def list_notes(limit: int = 10):
    """List last N notes."""
    try:
        if not os.path.exists(NOTES_FILE):
            return "No notes yet."
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            notes = json.load(f)
        notes = notes[-limit:]
        return "\n".join([f"{n['time']}: {n['text']}" for n in notes])
    except Exception as e:
        return f"Error listing notes: {e}"


# 36) System uptime
def system_uptime(_=None):
    """Get system uptime."""
    try:
        if psutil:
            boot = datetime.fromtimestamp(psutil.boot_time())
            delta = datetime.now() - boot
            return f"Uptime: {delta}"
        if os.path.exists("/proc/uptime"):
            with open("/proc/uptime") as f:
                seconds = float(f.read().split()[0])
            return f"Uptime: {seconds/3600:.2f} hours"
        return "Uptime not available."
    except Exception as e:
        return f"Error getting uptime: {e}"


# 37) Network speed test
def network_speed_test(_=None):
    """Run a simple network speed test."""
    if speedtest is None:
        return "Error: 'speedtest-cli' library not installed."
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        down = st.download() / 1_000_000
        up = st.upload() / 1_000_000
        return f"Download: {down:.2f} Mbps, Upload: {up:.2f} Mbps"
    except Exception as e:
        return f"Error running speed test: {e}"


# 38–39) Clipboard operations
def clipboard_set(text: str):
    """Set system clipboard text."""
    if pyperclip is None:
        return "Error: 'pyperclip' library not installed."
    try:
        pyperclip.copy(text)
        return "Clipboard updated."
    except Exception as e:
        return f"Error setting clipboard: {e}"


def clipboard_get(_=None):
    """Get system clipboard text."""
    if pyperclip is None:
        return "Error: 'pyperclip' library not installed."
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Error getting clipboard: {e}"


# 40) Python code formatter (black)
def format_python(code: str):
    """Format Python code with black."""
    if black is None:
        return "Error: 'black' library not installed."
    try:
        return black.format_str(code, mode=black.FileMode())
    except Exception as e:
        return f"Error formatting code: {e}"


# 41) Python linter (flake8)
def lint_python(code: str, filename: str = "temp_code.py"):
    """Lint Python code with flake8."""
    if flake8_legacy is None:
        return "Error: 'flake8' library not installed."
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        style_guide = flake8_legacy.get_style_guide()
        report = style_guide.check_files([filename])
        return f"Issues found: {report.total_errors}"
    except Exception as e:
        return f"Error linting code: {e}"


# 42) Programming joke
def programming_joke(_=None):
    """Get a random programming joke."""
    try:
        r = requests.get("https://official-joke-api.appspot.com/jokes/programming/random", timeout=5).json()
        if not r:
            return "No joke found."
        j = r[0]
        return f"{j['setup']}\n{j['punchline']}"
    except Exception as e:
        return f"Error fetching joke: {e}"


# 43) Page meta (title + description)
def fetch_page_meta(url: str):
    """Fetch page title and meta description."""
    if BeautifulSoup is None:
        return "Error: 'beautifulsoup4' library not installed."
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "No title"
        desc_tag = soup.find("meta", attrs={"name": "description"})
        desc = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else "No description"
        return f"Title: {title}\nDescription: {desc}"
    except Exception as e:
        return f"Error fetching page meta: {e}"


# 44) Tail file
def tail_file(path: str, lines: int = 20):
    """Tail last N lines of a file."""
    try:
        if not os.path.exists(path):
            return f"File '{path}' not found."
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = f.readlines()
        tail = data[-lines:]
        return "".join(tail)
    except Exception as e:
        return f"Error tailing file: {e}"


# ================= TOOL REGISTRY =================

available_tools = {
    # Core tools
    "get_weather": get_weather,
    "run_command": run_command,
    "web_search": web_search,
    "get_system_info": get_system_info,
    "read_file": read_file,
    "write_file": write_file,
    "calculate": calculate,
    "get_time": get_time,

    # First batch
    "wiki_summary": wiki_summary,
    "convert_currency": convert_currency,
    "ip_geolocate": ip_geolocate,
    "get_public_ip": get_public_ip,
    "fetch_page_title": fetch_page_title,
    "translate_text": translate_text,
    "detect_language": detect_language,
    "sentiment": sentiment,
    "summarize_text": summarize_text,
    "solve_equation": solve_equation,
    "get_disk_usage": get_disk_usage,
    "list_processes": list_processes,
    "list_files": list_files,
    "add_todo": add_todo,
    "list_todos": list_todos,
    "convert_time": convert_time,
    "geocode_address": geocode_address,
    "reverse_geocode": reverse_geocode,
    "image_info": image_info,
    "text_to_speech": text_to_speech,
    "get_ticker_price": get_ticker_price,
    "markdown_to_html": markdown_to_html,

    # Second batch
    "hn_top_stories": hn_top_stories,
    "rss_headlines": rss_headlines,
    "is_public_holiday": is_public_holiday,
    "generate_password": generate_password,
    "generate_uuid": generate_uuid,
    "pretty_json": pretty_json,
    "shorten_url": shorten_url,
    "generate_qr": generate_qr,
    "zip_path": zip_path,
    "unzip_file": unzip_file,
    "pdf_to_text": pdf_to_text,
    "add_note": add_note,
    "list_notes": list_notes,
    "system_uptime": system_uptime,
    "network_speed_test": network_speed_test,
    "clipboard_set": clipboard_set,
    "clipboard_get": clipboard_get,
    "format_python": format_python,
    "lint_python": lint_python,
    "programming_joke": programming_joke,
    "fetch_page_meta": fetch_page_meta,
    "tail_file": tail_file,
}
