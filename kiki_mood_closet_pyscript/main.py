"""
Kiki's Mood Closet: Pixel Edition

This is the main program logic.
The project uses HTML and CSS for the interface, but Python controls:
- data
- outfit switching
- theme switching
- scoring
- saved outfits
- pixel character rendering
- keyboard and button interactions
"""

from js import document, window
from pyodide.ffi import create_proxy
import json

# Keep event proxies alive.
_PROXIES = []

# ============ DATA ============
THEMES = [
    {
        "id": "graduation",
        "name": "Graduation Day",
        "emoji": "🎓",
        "bg": "linear-gradient(180deg,#f5e6b3,#fbf3d8)",
        "match": {
            "hair": ["neat"],
            "top": ["formal"],
            "bottom": ["formal"],
            "shoes": ["formal"],
            "acc": ["cap"],
        },
    },
    {
        "id": "study",
        "name": "Study Day",
        "emoji": "📚",
        "bg": "linear-gradient(180deg,#cfe3f5,#eaf3fb)",
        "match": {
            "hair": ["neat", "tied"],
            "top": ["casual", "cozy"],
            "bottom": ["casual"],
            "shoes": ["casual"],
            "acc": ["glasses"],
        },
    },
    {
        "id": "party",
        "name": "Party Night",
        "emoji": "🎉",
        "bg": "linear-gradient(180deg,#2d1a4a,#5a2a7a)",
        "match": {
            "hair": ["wild", "tied"],
            "top": ["sparkle"],
            "bottom": ["sparkle"],
            "shoes": ["sparkle"],
            "acc": ["star"],
        },
    },
    {
        "id": "cafe",
        "name": "Rainy Café",
        "emoji": "☕",
        "bg": "linear-gradient(180deg,#a8b5c4,#d0d8e0)",
        "match": {
            "hair": ["wavy", "tied"],
            "top": ["cozy"],
            "bottom": ["casual"],
            "shoes": ["casual"],
            "acc": ["glasses", "bow"],
        },
    },
    {
        "id": "weekend",
        "name": "Cute Weekend",
        "emoji": "🌸",
        "bg": "linear-gradient(180deg,#fcd4e2,#fde8ee)",
        "match": {
            "hair": ["wavy", "wild"],
            "top": ["casual", "sparkle"],
            "bottom": ["casual"],
            "shoes": ["casual", "sparkle"],
            "acc": ["bow", "star"],
        },
    },
]

ITEMS = {
    "hair": [
        {"id": "h1", "name": "Twin Buns", "tags": ["neat"], "color": "#7a3b2e"},
        {"id": "h2", "name": "Wavy Down", "tags": ["wavy"], "color": "#3a2a4a"},
        {"id": "h3", "name": "Star Pony", "tags": ["wild", "tied"], "color": "#a85ec9"},
    ],
    "top": [
        {"id": "t1", "name": "Sailor Tee", "tags": ["casual", "cozy"], "color": "#e8a8c0"},
        {"id": "t2", "name": "Blazer", "tags": ["formal"], "color": "#2a3a6a"},
        {"id": "t3", "name": "Glitter Top", "tags": ["sparkle"], "color": "#f0d24a"},
    ],
    "bottom": [
        {"id": "b1", "name": "Denim Skirt", "tags": ["casual"], "color": "#5a7ac0"},
        {"id": "b2", "name": "Pleated Skirt", "tags": ["formal", "casual"], "color": "#3a3a55"},
        {"id": "b3", "name": "Sparkle Pants", "tags": ["sparkle"], "color": "#c060c0"},
    ],
    "shoes": [
        {"id": "s1", "name": "Sneakers", "tags": ["casual"], "color": "#e85d5d"},
        {"id": "s2", "name": "Mary Janes", "tags": ["formal"], "color": "#3a1a2a"},
        {"id": "s3", "name": "Glitter Heels", "tags": ["sparkle"], "color": "#f0a0e0"},
    ],
    "acc": [
        {"id": "a1", "name": "Pink Bow", "tags": ["bow"], "color": "#ff7eb6"},
        {"id": "a2", "name": "Round Glasses", "tags": ["glasses"], "color": "#222"},
        {"id": "a3", "name": "Star Clip", "tags": ["star", "cap"], "color": "#f5d142"},
    ],
}

SLOTS = ["hair", "top", "bottom", "shoes", "acc"]
SLOT_LABEL = {
    "hair": "HAIR",
    "top": "TOP",
    "bottom": "BOTTOM",
    "shoes": "SHOES",
    "acc": "ACCESSORY",
}

# ============ STATE ============
theme_idx = 0
slot_idx = 0
outfit = {"hair": 0, "top": 0, "bottom": 0, "shoes": 0, "acc": 0}


def load_saved():
    try:
        raw = window.localStorage.getItem("kiki:saved")
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return []


saved = load_saved()


# ============ DOM HELPERS ============
def el(element_id):
    return document.getElementById(element_id)


def make(tag):
    return document.createElement(tag)


def add_event(element, event_name, callback):
    proxy = create_proxy(callback)
    _PROXIES.append(proxy)
    element.addEventListener(event_name, proxy)


app = el("app")
theme_emoji = el("themeEmoji")
theme_name = el("themeName")
theme_icons = el("themeIcons")
score_val = el("scoreVal")
score_label = el("scoreLabel")
slot_list = el("slotList")
kiki_sprite = el("kikiSprite")
flash = el("flash")
save_btn = el("saveBtn")
saved_strip = el("savedStrip")
saved_row = el("savedRow")


# ============ SPRITE RENDER ============
W, H = 16, 20
SKIN = "#fce0c4"
OUT = "#2a1a2a"
EYE = "#3a2a55"
CHEEK = "#f0a8b8"


def render_sprite(target, current_outfit):
    hair = ITEMS["hair"][current_outfit["hair"]]
    top = ITEMS["top"][current_outfit["top"]]
    bot = ITEMS["bottom"][current_outfit["bottom"]]
    shoe = ITEMS["shoes"][current_outfit["shoes"]]
    acc = ITEMS["acc"][current_outfit["acc"]]

    grid = [[None for _ in range(W)] for _ in range(H)]

    def set_px(x, y, color):
        if 0 <= x < W and 0 <= y < H:
            grid[y][x] = color

    def rect(x, y, width, height, color):
        for i in range(width):
            for j in range(height):
                set_px(x + i, y + j, color)

    # Head
    rect(5, 2, 6, 7, SKIN)
    for x in range(5, 11):
        set_px(x, 1, OUT)
        set_px(x, 9, OUT)
    for y in range(2, 9):
        set_px(4, y, OUT)
        set_px(11, y, OUT)

    # Hair
    if hair["id"] == "h1":
        rect(5, 2, 6, 2, hair["color"])
        rect(3, 3, 2, 2, hair["color"])
        rect(11, 3, 2, 2, hair["color"])
        set_px(4, 2, hair["color"])
        set_px(11, 2, hair["color"])
    elif hair["id"] == "h2":
        rect(5, 2, 6, 2, hair["color"])
        rect(4, 3, 1, 6, hair["color"])
        rect(11, 3, 1, 6, hair["color"])
        rect(3, 8, 2, 3, hair["color"])
        rect(11, 8, 2, 3, hair["color"])
    else:
        rect(5, 2, 6, 2, hair["color"])
        rect(4, 2, 1, 4, hair["color"])
        rect(11, 2, 1, 4, hair["color"])
        rect(10, 0, 3, 3, hair["color"])

    # Eyes and face
    rect(6, 5, 1, 2, EYE)
    rect(9, 5, 1, 2, EYE)
    set_px(6, 5, "#fff")
    set_px(9, 5, "#fff")
    set_px(6, 7, CHEEK)
    set_px(9, 7, CHEEK)
    set_px(8, 7, OUT)

    # Accessory
    if acc["id"] == "a1":
        set_px(4, 1, acc["color"])
        set_px(5, 1, acc["color"])
        set_px(6, 1, acc["color"])
        set_px(5, 0, acc["color"])
    elif acc["id"] == "a2":
        set_px(6, 6, acc["color"])
        set_px(7, 6, acc["color"])
        set_px(9, 6, acc["color"])
        set_px(10, 6, acc["color"])
        set_px(8, 6, acc["color"])
    else:
        set_px(10, 1, acc["color"])
        set_px(11, 1, acc["color"])
        set_px(11, 0, acc["color"])

    # Neck and top
    rect(7, 9, 2, 1, SKIN)
    rect(4, 10, 8, 4, top["color"])
    rect(3, 10, 1, 3, SKIN)
    rect(12, 10, 1, 3, SKIN)
    for x in range(4, 12):
        set_px(x, 13, OUT)

    # Bottom
    rect(4, 14, 8, 3, bot["color"])
    for x in range(4, 12):
        set_px(x, 16, OUT)

    # Legs and shoes
    rect(6, 17, 1, 2, SKIN)
    rect(9, 17, 1, 2, SKIN)
    rect(5, 19, 3, 1, shoe["color"])
    rect(8, 19, 3, 1, shoe["color"])

    target.style.gridTemplateColumns = f"repeat({W}, 1fr)"
    target.style.gridTemplateRows = f"repeat({H}, 1fr)"
    target.innerHTML = ""

    frag = document.createDocumentFragment()
    for y in range(H):
        for x in range(W):
            d = make("div")
            d.style.background = grid[y][x] if grid[y][x] else "transparent"
            frag.appendChild(d)

    target.appendChild(frag)


# ============ SCORING ============
def score_outfit(current_outfit, current_theme_idx):
    theme = THEMES[current_theme_idx]
    score = 0

    for slot in SLOTS:
        item = ITEMS[slot][current_outfit[slot]]
        if any(tag in theme["match"][slot] for tag in item["tags"]):
            score += 20

    return score


def rating(score):
    if score >= 100:
        return {"label": "PERFECT!", "color": "#2a8a4a"}
    if score >= 80:
        return {"label": "GREAT", "color": "#c4a020"}
    if score >= 60:
        return {"label": "GOOD", "color": "#d68a20"}
    if score >= 40:
        return {"label": "MEH", "color": "#c4683a"}
    return {"label": "OOPS", "color": "#c43a3a"}


# ============ UI RENDER ============
def set_theme(index):
    global theme_idx
    theme_idx = index
    render_all()


def render_theme_icons():
    theme_icons.innerHTML = ""

    for i, theme in enumerate(THEMES):
        button = make("button")
        button.className = "icon-btn active" if i == theme_idx else "icon-btn"
        button.textContent = theme["emoji"]
        button.title = theme["name"]

        def handle_click(event, index=i):
            set_theme(index)

        add_event(button, "click", handle_click)
        theme_icons.appendChild(button)


def change_slot_item(slot, direction):
    outfit[slot] = (outfit[slot] + direction + len(ITEMS[slot])) % len(ITEMS[slot])
    render_all()


def select_slot(index):
    global slot_idx
    slot_idx = index
    render_slots()


def render_slots():
    theme = THEMES[theme_idx]
    slot_list.innerHTML = ""

    for i, slot in enumerate(SLOTS):
        item = ITEMS[slot][outfit[slot]]
        matches = any(tag in theme["match"][slot] for tag in item["tags"])

        li = make("li")
        li.className = "slot-row active" if i == slot_idx else "slot-row"

        def handle_row_click(event, index=i):
            select_slot(index)

        add_event(li, "click", handle_row_click)

        slot_key = make("span")
        slot_key.className = "slot-key"
        slot_key.textContent = SLOT_LABEL[slot]

        slot_value = make("span")
        slot_value.className = "slot-value"

        swatch = make("span")
        swatch.className = "swatch"
        swatch.style.background = item["color"]

        name_span = make("span")
        name_span.textContent = item["name"]

        slot_value.appendChild(swatch)
        slot_value.appendChild(name_span)

        if matches:
            match_tag = make("span")
            match_tag.className = "match-tag"
            match_tag.textContent = "✓"
            slot_value.appendChild(match_tag)

        nav = make("span")
        nav.className = "slot-nav"

        left = make("button")
        left.textContent = "◀"

        def handle_left(event, current_slot=slot):
            event.stopPropagation()
            change_slot_item(current_slot, -1)

        add_event(left, "click", handle_left)

        right = make("button")
        right.textContent = "▶"

        def handle_right(event, current_slot=slot):
            event.stopPropagation()
            change_slot_item(current_slot, 1)

        add_event(right, "click", handle_right)

        nav.appendChild(left)
        nav.appendChild(right)

        li.appendChild(slot_key)
        li.appendChild(slot_value)
        li.appendChild(nav)

        slot_list.appendChild(li)


def render_saved():
    if len(saved) == 0:
        saved_strip.hidden = True
        return

    saved_strip.hidden = False
    saved_row.innerHTML = ""

    for saved_outfit in saved:
        button = make("button")
        button.className = "saved-thumb"
        button.title = "Load outfit"

        def handle_load(event, loaded=saved_outfit):
            global outfit
            outfit = dict(loaded)
            render_all()

        add_event(button, "click", handle_load)

        inner = make("div")
        inner.className = "kiki-sprite"
        render_sprite(inner, saved_outfit)

        button.appendChild(inner)
        saved_row.appendChild(button)


def render_all():
    theme = THEMES[theme_idx]
    app.style.background = theme["bg"]
    theme_emoji.textContent = theme["emoji"]
    theme_name.textContent = theme["name"].upper()

    score = score_outfit(outfit, theme_idx)
    result = rating(score)

    score_val.textContent = str(score)
    score_val.style.color = result["color"]
    score_label.textContent = result["label"]
    score_label.style.color = result["color"]

    render_theme_icons()
    render_slots()
    render_sprite(kiki_sprite, outfit)
    render_saved()


# ============ SAVE ============
def save_outfit(event=None):
    global saved
    saved = (saved + [dict(outfit)])[-6:]

    try:
        window.localStorage.setItem("kiki:saved", json.dumps(saved))
    except Exception:
        pass

    flash.textContent = "✓ OUTFIT SAVED!"
    flash.hidden = False

    def hide_flash():
        flash.hidden = True

    window.setTimeout(create_proxy(hide_flash), 1400)
    render_saved()


# ============ KEYBOARD CONTROL ============
def handle_keydown(event):
    global slot_idx, theme_idx

    slot = SLOTS[slot_idx]
    key = event.key

    if key == "ArrowUp":
        slot_idx = (slot_idx - 1 + len(SLOTS)) % len(SLOTS)
        render_slots()
    elif key == "ArrowDown":
        slot_idx = (slot_idx + 1) % len(SLOTS)
        render_slots()
    elif key == "ArrowLeft":
        change_slot_item(slot, -1)
    elif key == "ArrowRight":
        change_slot_item(slot, 1)
    elif key.lower() == "t":
        theme_idx = (theme_idx + 1) % len(THEMES)
        render_all()
    elif key.lower() == "s":
        save_outfit()


# ============ START ============
add_event(save_btn, "click", save_outfit)
add_event(document, "keydown", handle_keydown)

render_all()
