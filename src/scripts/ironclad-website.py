#!/usr/bin/env python3
"""
IronClad .ironclad Website Hosting System
- Username registry (file-based, first-come-first-serve)
- Seed phrase recovery
- DNS resolution
- Website hosting with nginx
"""

import subprocess
import json
import os
import sys
import hashlib
import secrets
from datetime import datetime, timedelta

# Configuration
IRONCLAD_DIR = "/opt/ironclad"
REGISTRY_FILE = f"{IRONCLAD_DIR}/registry/users.json"
IDENTITY_FILE = f"{IRONCLAD_DIR}/registry/identity.json"
WEBSITES_DIR = "/var/www/ironclad"
DNS_CONFIG_FILE = f"{IRONCLAD_DIR}/dns/ironclad.conf"

# BIP39-like wordlist (simplified - 2048 words)
WORDLIST = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
    "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
    "acoustic", "acquire", "across", "action", "actor", "actress", "actual", "adapt",
    "add", "addict", "address", "adjust", "admit", "adult", "advance", "advice",
    "aerobic", "affair", "afford", "afraid", "again", "age", "agent", "agree",
    "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol",
    "alert", "alien", "all", "alley", "allow", "almost", "alone", "alpha",
    "already", "also", "alter", "always", "amateur", "amazing", "among", "amount",
    "amused", "analyst", "anchor", "ancient", "anger", "angle", "angry", "animal",
    "ankle", "announce", "annual", "another", "answer", "antenna", "anticipate",
    "anxiety", "any", "apart", "apology", "appear", "apple", "approve", "april",
    "arch", "arctic", "area", "arena", "argue", "arm", "armed", "armor",
    "army", "around", "arrange", "arrest", "arrive", "arrow", "art", "artefact",
    "artist", "artwork", "ask", "aspect", "assault", "asset", "assist", "assume",
    "asthma", "athlete", "atom", "attack", "attend", "attitude", "attract", "auction",
    "audit", "august", "aunt", "author", "auto", "autumn", "average", "avocado",
    "avoid", "awake", "aware", "away", "awesome", "awful", "awkward", "axis",
    "baby", "bachelor", "bacon", "badge", "bag", "balance", "balcony", "ball",
    "bamboo", "banana", "banner", "bar", "barely", "bargain", "barrel", "base",
    "basic", "basket", "battle", "beach", "bean", "beauty", "because", "become",
    "beef", "before", "begin", "behave", "behind", "believe", "below", "belt",
    "bench", "benefit", "best", "betray", "better", "between", "beyond", "bicycle",
    "bid", "bike", "bind", "biology", "bird", "birth", "bitter", "black",
    "blade", "blame", "blanket", "blast", "bleak", "bless", "blind", "blood",
    "blossom", "blouse", "blue", "blur", "blush", "board", "boat", "body",
    "boil", "bomb", "bone", "bonus", "book", "boost", "border", "boring",
    "borrow", "boss", "bottom", "bounce", "box", "boy", "bracket", "brain",
    "brand", "brass", "brave", "bread", "breeze", "brick", "bridge", "brief",
    "bright", "bring", "brisk", "broccoli", "broken", "bronze", "broom", "brother",
    "brown", "brush", "bubble", "buddy", "budget", "buffalo", "build", "bulb",
    "bulk", "bullet", "bundle", "bunker", "burden", "burger", "burst", "bus",
    "business", "busy", "butter", "buyer", "buzz", "cabbage", "cabin", "cable",
    "cactus", "cage", "cake", "call", "calm", "camera", "camp", "canal",
    "cancel", "candy", "cannon", "canoe", "canvas", "canyon", "capable", "capital",
    "captain", "carbon", "card", "cargo", "carpet", "carry", "cart", "case",
    "cash", "casino", "castle", "casual", "cat", "catalog", "catch", "category",
    "cattle", "caught", "cause", "caution", "cave", "ceiling", "celery", "cement",
    "census", "century", "cereal", "certain", "chair", "chalk", "champion", "change",
    "chaos", "chapter", "charge", "chase", "chat", "cheap", "check", "cheese",
    "chef", "cherry", "chest", "chicken", "chief", "child", "chimney", "choice",
    "choose", "chronic", "chuckle", "chunk", "churn", "cigar", "cinnamon", "circle",
    "citizen", "city", "civil", "claim", "clap", "clarify", "claw", "clay",
    "clean", "clerk", "clever", "click", "client", "cliff", "climb", "clinic",
    "clip", "clock", "clog", "close", "cloth", "cloud", "clown", "club",
    "clump", "cluster", "clutch", "coach", "coast", "coconut", "code", "coffee",
    "coil", "coin", "collect", "color", "column", "combine", "come", "comfort",
    "comic", "common", "company", "concert", "conduct", "confirm", "congress", "connect",
    "consider", "control", "convince", "cook", "cool", "copper", "copy", "coral",
    "core", "corn", "correct", "cost", "cotton", "couch", "country", "couple",
    "course", "cousin", "cover", "coyote", "crack", "cradle", "craft", "cram",
    "crane", "crash", "crater", "crawl", "crazy", "cream", "credit", "creek",
    "crew", "cricket", "crime", "crisp", "critic", "crop", "cross", "crouch",
    "crowd", "crucial", "cruel", "cruise", "crunch", "crush", "cry", "crystal",
    "cube", "culture", "cup", "cupboard", "curious", "current", "curtain", "curve",
    "cushion", "custom", "cute", "cycle", "dad", "damage", "damp", "dance",
    "danger", "daring", "dash", "daughter", "dawn", "day", "deal", "debate",
    "debris", "decade", "december", "decide", "decline", "decorate", "decrease", "deer",
    "defense", "define", "defy", "degree", "delay", "deliver", "demand", "demise",
    "denial", "dentist", "deny", "depart", "depend", "deposit", "depth", "deputy",
    "derive", "describe", "desert", "design", "desk", "despair", "destroy", "detail",
    "detect", "develop", "device", "devote", "diagram", "dial", "diamond", "diary",
    "dice", "diesel", "diet", "differ", "digital", "dignity", "dilemma", "dinner",
    "dinosaur", "direct", "dirt", "disagree", "discover", "disease", "dish", "dismiss",
    "disorder", "display", "distance", "divert", "divide", "divorce", "dizzy", "doctor",
    "document", "dog", "doll", "dolphin", "domain", "donate", "donkey", "donor",
    "door", "dose", "double", "dove", "down", "download", "draft", "dragon",
    "drama", "draw", "dream", "dress", "drift", "drill", "drink", "drip",
    "drive", "drop", "drum", "drunk", "duck", "dumb", "dune", "during",
    "dust", "dutch", "duty", "dwarf", "dynamic", "eager", "eagle", "early",
    "earn", "earth", "easily", "east", "easy", "echo", "ecology", "economy",
    "edge", "edit", "educate", "effort", "egg", "eight", "eject", "elastic",
    "elbow", "elder", "electric", "elegant", "element", "elephant", "elevator", "elite",
    "else", "embark", "embody", "embrace", "emerge", "emotion", "employ", "empower",
    "empty", "enable", "enact", "end", "endorse", "enemy", "energy", "enforce",
    "engage", "engine", "enhance", "enjoy", "enlist", "enough", "enrich", "enroll",
    "ensure", "enter", "entire", "entry", "envelope", "episode", "equal", "equip",
    "era", "erase", "erode", "erosion", "error", "erupt", "escape", "essay",
    "essence", "estate", "eternal", "ethics", "evidence", "evil", "evoke", "evolve",
    "exact", "example", "excess", "exchange", "excite", "exclude", "excuse", "execute",
    "exercise", "exhaust", "exhibit", "exile", "exist", "exit", "exotic", "expand",
    "expect", "expire", "explain", "expose", "express", "extend", "extra", "eye",
    "eyebrow", "fabric", "face", "faculty", "fade", "faint", "faith", "fall",
    "false", "fame", "family", "famous", "fan", "fancy", "fantasy", "farm",
    "fashion", "fat", "fatal", "father", "fatigue", "fault", "favorite", "feature",
    "february", "federal", "fee", "feed", "feel", "female", "fence", "festival",
    "fetch", "fever", "few", "fiber", "fiction", "field", "figure", "file",
    "film", "filter", "final", "finance", "find", "fine", "finger", "finish",
    "fire", "firm", "first", "fiscal", "fish", "fit", "fitness", "fix",
    "flag", "flame", "flash", "flat", "flavor", "flee", "flight", "flip",
    "float", "flock", "floor", "flower", "fluid", "flush", "fly", "foam",
    "focus", "fog", "foil", "fold", "follow", "food", "foot", "force",
    "forest", "forget", "fork", "fortune", "forum", "forward", "fossil", "foster",
    "found", "fox", "fragile", "frame", "frequent", "fresh", "friend", "fringe",
    "frog", "front", "frost", "frown", "frozen", "fruit", "fuel", "fun",
    "funny", "furnace", "fury", "future", "gadget", "gain", "galaxy", "gallery",
    "game", "gap", "garage", "garbage", "garden", "garlic", "gas", "gasp",
    "gate", "gather", "gauge", "gaze", "general", "genius", "genre", "gentle",
    "genuine", "gesture", "ghost", "giant", "gift", "giggle", "ginger", "giraffe",
    "girl", "give", "glad", "glance", "glare", "glass", "glide", "glimpse",
    "globe", "gloom", "glory", "glove", "glow", "glue", "goat", "goddess",
    "gold", "good", "goose", "gorilla", "gospel", "gossip", "govern", "gown",
    "grab", "grace", "grain", "grant", "grape", "grass", "gravity", "great",
    "green", "grid", "grief", "grit", "grocery", "group", "grow", "grunt",
    "guard", "guess", "guide", "guilt", "guitar", "gun", "gym", "habit",
    "hair", "half", "hammer", "hamster", "hand", "handle", "harbor", "hard",
    "harsh", "harvest", "hat", "have", "hawk", "hazard", "head", "health",
    "heart", "heavy", "hedgehog", "height", "hello", "helmet", "help", "hen",
    "hero", "hidden", "high", "hill", "hint", "hip", "hire", "history",
    "hobby", "hockey", "hold", "hole", "holiday", "hollow", "home", "honey",
    "hood", "hope", "horn", "horror", "horse", "hospital", "host", "hotel",
    "hour", "hover", "hub", "huge", "human", "humble", "humor", "hundred",
    "hungry", "hunt", "hurdle", "hurry", "hurt", "husband", "hybrid", "ice",
    "icon", "idea", "identify", "idle", "ignore", "ill", "illegal", "illness",
    "image", "imitate", "immense", "immune", "impact", "impose", "improve", "impulse",
    "inch", "include", "income", "increase", "index", "indicate", "indoor", "industry",
    "infant", "inflict", "inform", "inhale", "inherit", "initial", "inject", "injury",
    "inmate", "inner", "innocent", "input", "inquiry", "insane", "insect", "inside",
    "inspire", "install", "intact", "interest", "into", "invest", "invite", "involve",
    "iron", "island", "isolate", "issue", "item", "ivory", "jacket", "jaguar",
    "jar", "jazz", "jealous", "jeans", "jelly", "jewel", "job", "join",
    "joke", "journey", "joy", "judge", "juice", "jump", "jungle", "junior",
    "junk", "just", "kangaroo", "keen", "keep", "ketchup", "key", "kick",
    "kid", "kidney", "kind", "kingdom", "kiss", "kit", "kitchen", "kite",
    "kitten", "kiwi", "knee", "knife", "knock", "know", "lab", "label",
    "labor", "ladder", "lady", "lake", "lamp", "language", "laptop", "large",
    "later", "latin", "laugh", "laundry", "lava", "law", "lawn", "lawsuit",
    "layer", "lazy", "leader", "leaf", "learn", "leave", "lecture", "left",
    "leg", "legal", "legend", "leisure", "lemon", "lend", "length", "lens",
    "leopard", "lesson", "letter", "level", "liar", "liberty", "library", "license",
    "life", "lift", "light", "like", "limb", "limit", "linen", "lion",
    "liquid", "list", "little", "live", "lizard", "load", "loan", "lobster",
    "local", "lock", "logic", "lonely", "long", "loop", "lottery", "loud",
    "lounge", "love", "loyal", "lucky", "luggage", "lumber", "lunar", "lunch",
    "luxury", "lyrics", "machine", "mad", "magic", "magnet", "maid", "mail",
    "main", "major", "make", "mammal", "man", "manage", "mandate", "mango",
    "mansion", "manual", "maple", "marble", "march", "margin", "marine", "market",
    "marriage", "mask", "mass", "master", "match", "material", "math", "matrix",
    "matter", "maximum", "maze", "meadow", "mean", "measure", "meat", "mechanic",
    "medal", "media", "melody", "melt", "member", "memory", "men", "mend",
    "mental", "mentor", "menu", "mercy", "merge", "merit", "merry", "mesh",
    "message", "metal", "method", "middle", "midnight", "milk", "million", "mimic",
    "mind", "minimum", "minor", "minute", "miracle", "mirror", "misery", "miss",
    "mistake", "mix", "mixed", "mixture", "mobile", "model", "modify", "mom",
    "moment", "monitor", "monkey", "monster", "month", "moon", "moral", "more",
    "morning", "mosquito", "mother", "motion", "motor", "mountain", "mouse", "move",
    "movie", "much", "muffin", "mule", "multiply", "muscle", "museum", "mushroom",
    "music", "must", "mutual", "myself", "mystery", "myth", "naive", "name",
    "napkin", "narrow", "nasty", "nation", "nature", "near", "neck", "need",
    "negative", "neglect", "neither", "nephew", "nerve", "nest", "net", "network",
    "neutral", "never", "news", "next", "nice", "night", "noble", "noise",
    "nominee", "noodle", "normal", "north", "nose", "notable", "note", "nothing",
    "notice", "novel", "now", "nuclear", "number", "nurse", "nut", "oak",
    "obey", "object", "oblige", "obscure", "observe", "obtain", "obvious", "occur",
    "ocean", "october", "odor", "off", "offer", "office", "often", "oil",
    "okay", "old", "olive", "olympic", "omit", "once", "one", "onion",
    "online", "only", "open", "opera", "opinion", "oppose", "option", "orange",
    "orbit", "orchard", "order", "ordinary", "organ", "orient", "original", "orphan",
    "ostrich", "other", "outdoor", "outer", "output", "outside", "oval", "oven",
    "over", "own", "owner", "oxygen", "oyster", "ozone", "paddle", "page",
    "pair", "palace", "palm", "panda", "panel", "panic", "panther", "paper",
    "parade", "parent", "park", "parrot", "party", "pass", "patch", "path",
    "patient", "patrol", "pattern", "pause", "pave", "payment", "peace", "peanut",
    "pear", "peasant", "pelican", "pen", "penalty", "pencil", "people", "pepper",
    "perfect", "permit", "person", "pet", "phone", "photo", "phrase", "physical",
    "piano", "picnic", "picture", "piece", "pig", "pigeon", "pill", "pilot",
    "pink", "pioneer", "pipe", "pistol", "pitch", "pizza", "place", "planet",
    "plastic", "plate", "play", "please", "pledge", "pluck", "plug", "plunge",
    "poem", "poet", "point", "polar", "pole", "police", "pond", "pony",
    "pool", "popular", "portion", "position", "possible", "post", "potato", "pottery",
    "poverty", "powder", "power", "practice", "praise", "predict", "prefer", "prepare",
    "present", "pretty", "prevent", "price", "pride", "primary", "print", "priority",
    "prison", "private", "prize", "problem", "process", "produce", "profit", "program",
    "project", "promote", "proof", "property", "prosper", "protect", "proud", "provide",
    "public", "pudding", "pull", "pulp", "pulse", "pumpkin", "punch", "pupil",
    "puppy", "purchase", "purity", "purpose", "purse", "push", "put", "puzzle",
    "pyramid", "quality", "quantum", "quarter", "question", "quick", "quit", "quiz",
    "quote", "rabbit", "raccoon", "race", "rack", "radar", "radio", "rail",
    "rain", "raise", "rally", "ramp", "ranch", "random", "range", "rapid",
    "rare", "rate", "rather", "raven", "raw", "reach", "react", "read",
    "real", "realm", "rear", "reason", "rebel", "rebuild", "recall", "receive",
    "recipe", "record", "recycle", "red", "reduce", "reflect", "reform", "refuse",
    "region", "regret", "regular", "reject", "relax", "release", "relief", "rely",
    "remain", "remember", "remind", "remote", "remove", "render", "renew", "rent",
    "reopen", "repair", "repeat", "replace", "reply", "report", "represent", "reproduce",
    "public", "require", "rescue", "resemble", "resist", "resource", "response", "result",
    "retire", "retreat", "return", "reunion", "reveal", "review", "reward", "rhythm",
    "rib", "ribbon", "rice", "rich", "ride", "ridge", "rifle", "right",
    "rigid", "ring", "riot", "ripple", "risk", "ritual", "rival", "river",
    "road", "roast", "robot", "robust", "rocket", "romance", "roof", "rookie",
    "room", "rose", "rotate", "rough", "round", "route", "royal", "rubber",
    "rude", "rug", "rule", "run", "runway", "rural", "sad", "saddle",
    "sadness", "safe", "sail", "salad", "salmon", "salon", "salt", "salute",
    "same", "sample", "sanctuary", "sand", "satisfy", "satoshi", "sauce", "sausage",
    "save", "say", "scale", "scan", "scare", "scatter", "scene", "scent",
    "school", "science", "scissors", "scorpion", "scout", "scrap", "screen", "script",
    "scrub", "sea", "search", "season", "seat", "second", "secret", "section",
    "security", "seed", "seek", "segment", "select", "sell", "seminar", "senior",
    "sense", "sentence", "series", "service", "session", "settle", "setup", "seven",
    "shadow", "shaft", "shallow", "share", "shed", "shell", "sheriff", "shield",
    "shift", "shine", "ship", "shiver", "shock", "shoe", "shoot", "shop",
    "short", "shoulder", "shove", "shrimp", "shrug", "shuffle", "shy", "sibling",
    "sick", "side", "siege", "sight", "sign", "silent", "silk", "silly",
    "silver", "similar", "simple", "since", "sing", "siren", "sister", "situate",
    "six", "size", "skate", "sketch", "ski", "skill", "skin", "skirt",
    "skull", "slab", "slam", "sleep", "slender", "slice", "slide", "slight",
    "slim", "slogan", "slot", "slow", "slush", "small", "smart", "smile",
    "smoke", "smooth", "snack", "snake", "snap", "sniff", "snow", "soar",
    "social", "sock", "soda", "soft", "solar", "soldier", "solid", "solution",
    "solve", "someone", "song", "soon", "sorry", "sort", "soul", "sound",
    "soup", "source", "south", "space", "spare", "spatial", "spawn", "speak",
    "special", "speed", "spell", "spend", "sphere", "spice", "spider", "spike",
    "spin", "spirit", "split", "spoil", "sponsor", "spoon", "sport", "spot",
    "spread", "spring", "spy", "square", "squeeze", "squirrel", "stable", "stadium",
    "staff", "stage", "stairs", "stake", "stamp", "stand", "start", "state",
    "stay", "steak", "steel", "stem", "step", "stereo", "stick", "still",
    "sting", "stock", "stomach", "stone", "stool", "story", "stove", "strategy",
    "street", "strike", "strong", "struggle", "student", "stuff", "stumble", "style",
    "subject", "submit", "subway", "success", "such", "sudden", "suffer", "sugar",
    "suggest", "suit", "summer", "sun", "sunny", "sunset", "super", "supply",
    "supreme", "sure", "surface", "surge", "surprise", "surround", "survey", "suspect",
    "sustain", "swallow", "swamp", "swap", "swarm", "swear", "sweat", "sweep",
    "sweet", "swift", "swim", "swing", "switch", "sword", "symbol", "symptom",
    "syrup", "system", "table", "tackle", "tag", "tail", "talent", "talk",
    "tank", "tape", "target", "task", "taste", "tattoo", "taxi", "teach",
    "team", "tell", "ten", "tenant", "tennis", "tent", "term", "test",
    "text", "thank", "that", "theme", "then", "theory", "there", "they",
    "thing", "this", "thought", "three", "thrive", "throw", "thumb", "thunder",
    "ticket", "tide", "tiger", "tilt", "timber", "time", "tiny", "tip",
    "tired", "tissue", "title", "toast", "tobacco", "toddler", "toe", "together",
    "toilet", "token", "tomato", "tomorrow", "tone", "tongue", "tonight", "tool",
    "tooth", "top", "topic", "topple", "torch", "tornado", "tortoise", "toss",
    "total", "tourist", "toward", "tower", "town", "toy", "track", "trade",
    "traffic", "tragic", "train", "transfer", "trap", "trash", "travel", "tray",
    "treat", "tree", "trend", "trial", "tribe", "trick", "trigger", "trim",
    "trip", "trophy", "trouble", "truck", "true", "truly", "trumpet", "trust",
    "truth", "try", "tube", "tuition", "tumble", "tuna", "tunnel", "turkey",
    "turn", "turtle", "twelve", "twenty", "twice", "twin", "twist", "two",
    "type", "typical", "ugly", "umbrella", "unable", "unaware", "uncle", "uncover",
    "under", "undo", "unfair", "unfold", "unhappy", "uniform", "unique", "unit",
    "universe", "unknown", "unlock", "until", "unusual", "unveil", "update", "upgrade",
    "uphold", "upon", "upper", "upset", "urban", "urge", "usage", "use",
    "used", "useful", "useless", "usual", "utility", "vacant", "vacuum", "vague",
    "valid", "valley", "valve", "van", "vanish", "vapor", "various", "vegan",
    "velvet", "vendor", "venture", "venue", "verb", "verify", "version", "very",
    "vessel", "veteran", "viable", "vibrant", "vicious", "victory", "video", "view",
    "village", "vintage", "violin", "virtual", "virus", "visa", "visit", "visual",
    "vital", "vivid", "vocal", "voice", "void", "volcano", "volume", "vote",
    "voyage", "wage", "wagon", "wait", "wake", "walk", "wall", "walnut",
    "want", "warfare", "warm", "warrior", "wash", "wasp", "waste", "water",
    "wave", "way", "wealth", "weapon", "wear", "weasel", "weather", "web",
    "wedding", "weekend", "weird", "welcome", "west", "wet", "whale", "what",
    "wheat", "wheel", "when", "where", "whip", "whisper", "wide", "width",
    "wife", "wild", "will", "win", "window", "wine", "wing", "wink",
    "winner", "winter", "wire", "wisdom", "wise", "wish", "witch", "withdraw",
    "witness", "wolf", "woman", "wonder", "wood", "wool", "word", "work",
    "world", "worry", "worth", "wrap", "wreck", "wrestle", "wrist", "write",
    "wrong", "yard", "year", "yellow", "you", "young", "youth", "zebra",
    "zero", "zone", "zoo"
]

def run_cmd(cmd, sudo=False):
    """Run shell command"""
    if sudo:
        cmd = f"echo '9300' | sudo -S {cmd}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def ensure_dir(path):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)

def load_registry():
    """Load user registry"""
    ensure_dir(os.path.dirname(REGISTRY_FILE))
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    return {"users": {}, "version": 1}

def save_registry(registry):
    """Save user registry"""
    ensure_dir(os.path.dirname(REGISTRY_FILE))
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(registry, f, indent=2)

def generate_seed_phrase():
    """Generate 12-word BIP39-like seed phrase"""
    words = []
    for _ in range(12):
        words.append(secrets.choice(WORDLIST))
    return " ".join(words)

def seed_to_hash(seed):
    """Convert seed phrase to hash for verification"""
    return hashlib.sha256(seed.encode()).hexdigest()

def load_identity():
    """Load local identity"""
    ensure_dir(os.path.dirname(IDENTITY_FILE))
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, 'r') as f:
            return json.load(f)
    return None

def save_identity(identity):
    """Save local identity"""
    ensure_dir(os.path.dirname(IDENTITY_FILE))
    with open(IDENTITY_FILE, 'w') as f:
        json.dump(identity, f, indent=2)

def get_yggdrasil_ip():
    """Get current Yggdrasil IP"""
    rc, stdout, _ = run_cmd("/usr/bin/yggdrasilctl -json getSelf 2>/dev/null")
    if rc == 0:
        try:
            data = json.loads(stdout)
            return data.get('address', '')
        except:
            pass
    return ""

def register_username(username, seed_phrase):
    """Register a new username"""
    registry = load_registry()
    
    # Check if username taken
    if username in registry["users"]:
        return False, "Username already taken"
    
    # Get current Yggdrasil IP
    ygg_ip = get_yggdrasil_ip()
    if not ygg_ip:
        return False, "Yggdrasil not running"
    
    # Create user entry
    registry["users"][username] = {
        "yggdrasil_ip": ygg_ip,
        "registered": datetime.now().isoformat(),
        "seed_hash": seed_to_hash(seed_phrase),
        "websites": [],
        "last_updated": datetime.now().isoformat()
    }
    
    save_registry(registry)
    
    # Create identity file
    identity = {
        "username": username,
        "seed_phrase": seed_phrase,
        "seed_hash": seed_to_hash(seed_phrase),
        "yggdrasil_ip": ygg_ip
    }
    save_identity(identity)
    
    # Create website directory
    user_dir = f"{WEBSITES_DIR}/{username}"
    ensure_dir(user_dir)
    run_cmd(f"chown -R www-data:www-data {WEBSITES_DIR}", sudo=True)
    
    return True, "Username registered"

def claim_website(username, website_name):
    """Claim a website subdomain"""
    registry = load_registry()
    
    if username not in registry["users"]:
        return False, "Username not registered"
    
    # Check limit (5 per week)
    user = registry["users"][username]
    registered = datetime.fromisoformat(user["registered"])
    if datetime.now() - registered < timedelta(days=7):
        week_limit = 5
    else:
        week_limit = 5  # Reset each week
    
    current_websites = len(user.get("websites", []))
    if current_websites >= week_limit:
        return False, f"Website limit ({week_limit}/week) reached"
    
    # Add website
    if "websites" not in user:
        user["websites"] = []
    
    if website_name in user["websites"]:
        return False, "Website name already taken"
    
    user["websites"].append(website_name)
    user["last_updated"] = datetime.now().isoformat()
    
    # Update Yggdrasil IP if changed
    ygg_ip = get_yggdrasil_ip()
    if ygg_ip and ygg_ip != user["yggdrasil_ip"]:
        user["yggdrasil_ip"] = ygg_ip
    
    save_registry(registry)
    
    # Create website directory
    site_dir = f"{WEBSITES_DIR}/{username}/{website_name}"
    ensure_dir(site_dir)
    
    # Create sample index.html
    sample_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{website_name}.{username}.ironclad</title>
    <style>
        body {{ font-family: sans-serif; padding: 50px; text-align: center; }}
    </style>
</head>
<body>
    <h1>Welcome to {website_name}.{username}.ironclad</h1>
    <p>Hosted on IronClad P2P Network</p>
</body>
</html>"""
    with open(f"{site_dir}/index.html", 'w') as f:
        f.write(sample_html)
    
    run_cmd(f"chown -R www-data:www-data {site_dir}", sudo=True)
    
    return True, f"Website {website_name}.{username}.ironclad created"

def recover_username(seed_phrase):
    """Recover username using seed phrase"""
    registry = load_registry()
    seed_hash = seed_to_hash(seed_phrase)
    
    # Find user with matching seed hash
    for username, user_data in registry["users"].items():
        if user_data.get("seed_hash") == seed_hash:
            # Update Yggdrasil IP
            ygg_ip = get_yggdrasil_ip()
            if ygg_ip:
                user_data["yggdrasil_ip"] = ygg_ip
                user_data["last_updated"] = datetime.now().isoformat()
                save_registry(registry)
                
                # Update local identity
                identity = {
                    "username": username,
                    "seed_phrase": seed_phrase,
                    "seed_hash": seed_hash,
                    "yggdrasil_ip": ygg_ip
                }
                save_identity(identity)
            
            return True, username
    
    return False, "No account found with this seed phrase"

def setup_dns():
    """Set up Unbound DNS for .ironclad"""
    ensure_dir(os.path.dirname(DNS_CONFIG_FILE))
    
    registry = load_registry()
    
    # Generate DNS config
    dns_config = """server:
    local-zone: "ironclad." static
    local-data-ptr: "localhost.ironclad. IN A 127.0.0.1"
"""
    for username, user_data in registry["users"].items():
        ygg_ip = user_data.get("yggdrasil_ip", "")
        if ygg_ip:
            dns_config += f"    local-data: \"{username}.ironclad. IN AAAA {ygg_ip}\"\n"
            # Also add for each website
            for website in user_data.get("websites", []):
                dns_config += f"    local-data: \"{website}.{username}.ironclad. IN AAAA {ygg_ip}\"\n"
    
    with open(DNS_CONFIG_FILE, 'w') as f:
        f.write(dns_config)
    
    # Reload Unbound
    run_cmd("systemctl restart unbound", sudo=True)
    
    return True

def show_status():
    """Show current status"""
    identity = load_identity()
    if identity:
        print(f"Logged in as: {identity['username']}")
        print(f"Yggdrasil IP: {identity.get('yggdrasil_ip', 'N/A')}")
    else:
        print("Not registered")
    
    registry = load_registry()
    print(f"Total users: {len(registry['users'])}")
    
    # List websites
    if identity and identity['username'] in registry['users']:
        websites = registry['users'][identity['username']].get('websites', [])
        print(f"Your websites: {', '.join(websites) if websites else 'None'}")

# CLI
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("IronClad Website Hosting System")
        print("Usage:")
        print("  register <username>              - Register new username")
        print("  seed                             - Show/regenerate seed phrase")
        print("  recover <seed>                   - Recover username with seed")
        print("  claim <website>                   - Claim website subdomain")
        print("  status                            - Show status")
        print("  dns                               - Update DNS config")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "register":
        if len(sys.argv) > 2:
            username = sys.argv[2]
            # Generate seed phrase
            seed = generate_seed_phrase()
            success, msg = register_username(username, seed)
            if success:
                print(f"Registered as: {username}")
                print(f"Seed phrase: {seed}")
                print("SAVE THIS SEED PHRASE! It's needed for account recovery!")
            else:
                print(f"Error: {msg}")
        else:
            print("Usage: ironclad-register <username>")
            
    elif action == "seed":
        identity = load_identity()
        if identity:
            print(f"Seed phrase: {identity['seed_phrase']}")
        else:
            print("Not registered")
            
    elif action == "recover":
        if len(sys.argv) > 2:
            seed = " ".join(sys.argv[2:])
            success, msg = recover_username(seed)
            if success:
                print(f"Recovered username: {msg}")
            else:
                print(f"Error: {msg}")
        else:
            print("Usage: ironclad-recover <seed_phrase>")
            
    elif action == "claim":
        if len(sys.argv) > 2:
            identity = load_identity()
            if identity:
                username = identity['username']
                website = sys.argv[2]
                success, msg = claim_website(username, website)
                if success:
                    print(f"Created: {msg}")
                else:
                    print(f"Error: {msg}")
            else:
                print("Not registered")
        else:
            print("Usage: ironclad-claim <website_name>")
            
    elif action == "status":
        show_status()
        
    elif action == "dns":
        setup_dns()
        print("DNS updated")
        
    else:
        print(f"Unknown: {action}")
