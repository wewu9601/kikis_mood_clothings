# python-html-css
kiki's mood closet 

This version keeps the HTML and CSS interface, but uses Python as the main programming language.

This project uses Python as the main programming language through PyScript.

HTML and CSS are used only for the interface layout and pixel-art visual style. The main logic is written in main.py.

Python is used for:

storing theme and outfit data
switching outfit items
switching themes
calculating theme-based scores
generating the pixel character
updating the visual interface
handling keyboard controls
saving outfit states
This project uses PyScript / Pyodide, so it is a browser-based Python project. It may not run directly inside Ed's default Python environment.

File structure
kiki_mood_closet_pyscript/
├── index.html
├── style.css
├── main.py
├── pyscript.json
└── README.md
What each file does
index.html: page structure only
style.css: pixel-style visual design
main.py: main program logic in Python
pyscript.json: PyScript configuration
Why this counts as Python-main
Python controls:

outfit data
theme data
keyboard interactions
button interactions
sprite rendering
theme-based score calculation
saved outfit data
HTML and CSS are used only for layout and visual style.

How to run
Because browsers usually block external Python files when opened directly, run a local server from this folder:

python3 -m http.server
Then open:

http://localhost:8000
On Windows, you can also use:

python -m http.server
Controls
↑ / ↓: choose outfit slot
← / →: change selected item
T: switch theme
S: save outfit
