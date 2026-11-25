"""Story data: the how-to-play text and all five cases of Shadow Detective."""

from robot_info.display import GOLD, ORANGE, RED, WHITE, YELLOW


HOW_TO_PLAY = [
    ("Move", "You are the purple detective. Type in the control_node terminal: the ARROW "
             "KEYS walk. Walk out at the left or right edge of a room to change rooms."),
    ("Examine and talk", "Stand next to something and press SPACE to examine it or to "
                         "talk to a person. Clues go into your notebook (N). Some things "
                         "are locked - find the key or the code first!"),
    ("Watch out!", "Things move around in every room. Bumping into them costs 50 "
                   "points and pushes you back. Every case gets faster and more crowded."),
    ("Score", "New clue +100, new question +10, solved case +500 plus 100 for every "
              "attempt left. A wrong accusation costs 100 points."),
    ("Accuse", "When you are sure, press A. Choose the culprit and the clues that "
               "prove it. Each wrong accusation costs one attempt."),
]


# ==========================================================================
# STORY DATA - all five cases.
#
# Every case is a dictionary. To write your own case, copy one of them and
# change the texts. Rooms are drawn by the functions draw_<name> in
# shadow_detective.py (the "draw" entry of each room).
#
# Difficulty settings per case:
#   min_clues  - clues you must find before you may accuse someone
#   evidence   - how many clues you must pick when accusing
#   attempts   - wrong accusations allowed
#   glow       - how strongly clues glow (1 = strong, 0 = not at all)
#
# A spot can be locked: give it "needs": <clue id> and a "locked" text.
# It only reveals its clue after the needed clue has been found.
#
# The look of every case is set in its "theme" (see the end of this part).
# ==========================================================================

# Extra colours used by the cases
BLUE = (70, 110, 170)
PURPLE = (130, 80, 160)
ICE = (170, 215, 255)
PINK = (215, 95, 150)
CYAN = (80, 190, 200)
GREEN = (90, 180, 110)
SILVER = (185, 185, 195)

LEFT_DOOR = (40, 230, 110, 200)
RIGHT_DOOR = (810, 230, 110, 200)


# ==========================================================================
# CASE 1 - The Museum Heist (easy)
# ==========================================================================

CASE_1 = {
    "title": "The Museum Heist",
    "question": "Who stole The Moonlit Night?",
    "intro": "Rain hammers the city of Greyhaven. At 22:30 your phone rings: The "
             "Moonlit Night, the most valuable painting in the city museum, has "
             "been stolen. Four people were in the building. One of them is lying.",
    "min_clues": 3, "evidence": 1, "attempts": 3, "glow": 1.0,
    "start": "hall",
    "rooms": {
        "hall": {
            "name": "Entrance Hall", "draw": "hall", "wall": (46, 48, 54),
            "doors": [{"rect": LEFT_DOOR, "sign": "OFFICE", "to": "office"},
                      {"rect": RIGHT_DOOR, "sign": "EXHIBITION", "to": "exhibition"}],
            "people": [("ole", 700, 550, False)],
            "spots": [
                {"rect": (185, 170, 160, 90), "label": "Key board", "clue": "key", "color": RED},
                {"rect": (620, 160, 120, 90), "label": "Camera control panel",
                 "clue": "camera", "color": YELLOW},
                {"rect": (400, 190, 160, 240), "label": "Main entrance",
                 "look": ("Main Entrance", "The front doors are locked from the inside. "
                          "Nobody broke in - the thief was already in the building.")},
                {"rect": (170, 395, 220, 70), "label": "Reception desk",
                 "look": ("Reception Desk", "A stack of brochures: 'Home of The Moonlit "
                          "Night - insured, protected, priceless.'")},
            ],
        },
        "exhibition": {
            "name": "Exhibition Room", "draw": "exhibition", "wall": (50, 50, 56),
            "doors": [{"rect": LEFT_DOOR, "sign": "HALL", "to": "hall"},
                      {"rect": RIGHT_DOOR, "sign": "STORAGE", "to": "storage", "ajar": True}],
            "people": [("leon", 260, 550, False)],
            "spots": [
                {"rect": (460, 425, 340, 110), "label": "Footprints", "clue": "footprints",
                 "color": ORANGE},
                {"rect": (380, 110, 200, 170), "label": "Empty frame",
                 "look": ("Empty Frame", "The Moonlit Night is gone. Only a nail and a "
                          "dusty outline remain.")},
                {"rect": (350, 300, 260, 110), "label": "Velvet rope",
                 "look": ("Velvet Rope", "The rope was cut cleanly. The thief came prepared.")},
                {"rect": (180, 120, 120, 150), "label": "Portrait",
                 "look": ("Old Portrait", "A grim old man in a grey suit. He looks like he "
                          "knows something. He doesn't.")},
                {"rect": (640, 120, 110, 90), "label": "Landscape",
                 "look": ("Grey Landscape", "A grey landscape. Still here. Apparently not "
                          "worth stealing.")},
            ],
        },
        "office": {
            "name": "Director's Office", "draw": "office", "wall": (52, 48, 46),
            "doors": [{"rect": (820, 230, 110, 200), "sign": "HALL", "to": "hall"}],
            "people": [("weber", 430, 452, True)],
            "spots": [
                {"rect": (495, 335, 90, 45), "label": "Papers", "clue": "contract", "color": RED},
                {"rect": (330, 360, 340, 100), "label": "Desk",
                 "look": ("Desk", "A tidy desk. Very tidy. Almost too tidy.")},
                {"rect": (80, 110, 180, 170), "label": "Window",
                 "look": ("Window", "Rain. The window is locked from the inside.")},
                {"rect": (560, 130, 90, 110), "label": "Photo",
                 "look": ("Photo", "Director Weber at the museum gala, wearing her famous "
                          "bright red lipstick.")},
                {"rect": (690, 320, 100, 110), "label": "Safe",
                 "look": ("Safe", "The safe is open. Inside: unpaid bills. Lots and lots "
                          "of unpaid bills.")},
            ],
        },
        "storage": {
            "name": "Storage Room", "draw": "storage", "wall": (38, 38, 42),
            "doors": [{"rect": LEFT_DOOR, "sign": "EXHIBITION", "to": "exhibition"}],
            "people": [("karl", 560, 550, False)],
            "spots": [
                {"rect": (345, 312, 42, 42), "label": "Coffee cup", "clue": "cup", "color": RED},
                {"rect": (690, 225, 100, 100), "label": "Something behind the crates",
                 "clue": "painting", "color": GOLD},
                {"rect": (250, 395, 75, 40), "label": "Boots",
                 "look": ("Work Boots", "Karl's spare work boots. Enormous - size 45.")},
                {"rect": (175, 290, 70, 145), "label": "Mop and bucket",
                 "look": ("Mop and Bucket", "Karl's mop. The bucket is full of clean water.")},
                {"rect": (640, 320, 190, 115), "label": "Crates",
                 "look": ("Crates", "Old crates full of plaster statues.")},
            ],
        },
    },
    "clues": {
        "footprints": ("Muddy Footprints",
                       "Small muddy footprints, shoe size 38. They lead from the empty "
                       "frame straight to the storage room."),
        "key": ("Missing Key",
                "The hook labelled STORAGE on the key board is empty. Someone took the "
                "storage room key."),
        "camera": ("Camera Log",
                   "The camera was switched off from 22:10 to 22:20 with the admin "
                   "password. Only Director Weber and guard Ole know it."),
        "contract": ("Insurance Contract",
                     "The painting's insurance was raised from 200,000 to 2,000,000 - "
                     "just last week. Signed: H. Weber."),
        "cup": ("Lipstick Cup",
                "A coffee cup, still warm, with a red lipstick mark on the rim. Someone "
                "was in here only minutes ago."),
        "painting": ("Hidden Painting",
                     "Behind the crates, wrapped in a blanket: The Moonlit Night! The "
                     "painting never left the building."),
    },
    "culprit": "weber",
    "strong": ["footprints", "camera", "contract", "cup"],
    "weak_text": {
        "key": "Weber shrugs: 'Anyone in this building could have taken that key.' "
               "That alone proves nothing.",
        "painting": "Weber gasps: 'You found it! But that doesn't tell you who hid it.' "
                    "You need evidence that points to her.",
    },
    "confession": "Director Weber confesses!",
    "solution": "Director Weber was broke. Last week she raised the insurance to "
                "2,000,000. At 22:05 she sent Ole up to the roof, switched off the "
                "camera with her password, took the storage key and hid the painting "
                "behind the crates - leaving lipstick on a coffee cup and size 38 "
                "footprints on the floor. After the insurance paid, she wanted to sell "
                "the painting in secret.",
    "suspects": {
        "karl": {
            "name": "Karl", "role": "Janitor", "style": "karl", "accent": BLUE,
            "greeting": "Evening, detective. Mind the wet floor.",
            "topics": [
                {"q": "Where were you tonight?",
                 "a": "Mopping the basement, like every night. Ask my mop, it'll tell you."},
                {"q": "What about the footprints?", "req": "footprints",
                 "a": "Not mine, detective! I wear size 45 boots. Those tiny prints come "
                      "from a fancy shoe."},
                {"q": "Did you take the storage key?", "req": "key",
                 "a": "Why would I? I carry my own key ring. I haven't touched that board "
                      "in years."},
                {"q": "Is this your coffee cup?", "req": "cup",
                 "a": "Me? I only drink tea. And I don't wear lipstick, ha!"},
                {"q": "What do you think of the director?",
                 "a": "Coffee, coffee, coffee. She leaves cups with red lipstick all over "
                      "my clean museum!"},
            ],
            "innocent": "Karl's boots are size 45 - far too big for the footprints. And "
                        "he doesn't even know the camera password. Karl is innocent.",
        },
        "weber": {
            "name": "Helga Weber", "role": "Museum Director", "style": "weber", "accent": RED,
            "greeting": "Detective! Thank goodness. Please, find my painting.",
            "topics": [
                {"q": "Where were you tonight?",
                 "a": "In my office all evening, doing paperwork. I never left, I swear."},
                {"q": "Who knows the camera password?", "req": "camera",
                 "a": "Only me... and Ole, the guard. If I were you, I'd take a closer "
                      "look at him."},
                {"q": "Why was the insurance raised?", "req": "contract",
                 "a": "Pure coincidence! The painting has, um, gained value. The art "
                      "market, you know."},
                {"q": "Were you in the storage room?", "req": "cup",
                 "a": "The storage room? Never! I don't even drink coffee."},
                {"q": "Does the museum have money trouble?",
                 "a": "The museum is doing perfectly fine. Next question, please."},
            ],
            "innocent": "",
        },
        "leon": {
            "name": "Leon", "role": "Artist", "style": "leon", "accent": PURPLE,
            "greeting": "Ah, the detective. Here to admire art, or to blame the artist?",
            "topics": [
                {"q": "Where were you tonight?",
                 "a": "I came at 21:00 to see my rival's painting one last time. I left at "
                      "21:30 - the guard let me out."},
                {"q": "You hated the painter, right?",
                 "a": "Hate? He copied my style! But stealing his painting would only make "
                      "him more famous. No, thank you."},
                {"q": "What about the footprints?", "req": "footprints",
                 "a": "Size 38? Please. I wear 43. Big feet, big talent."},
            ],
            "innocent": "Ole locked the door behind Leon at 21:30, but the painting "
                        "vanished after 22:10. Leon is innocent.",
        },
        "ole": {
            "name": "Ole", "role": "Security Guard", "style": "ole", "accent": YELLOW,
            "greeting": "Detective. I didn't see anything... well, almost nothing.",
            "topics": [
                {"q": "Where were you tonight?",
                 "a": "Doing my rounds. At 22:15 I was up on the roof. When I came back "
                      "down, the frame was empty."},
                {"q": "Why were you on the roof?",
                 "a": "The director called me at 22:05. She said the roof alarm was "
                      "beeping. But it wasn't beeping at all..."},
                {"q": "Who switched off the camera?", "req": "camera",
                 "a": "Not me! The control panel is down here, and I was on the roof. Only "
                      "the director and I know the password."},
                {"q": "Did you see Leon tonight?",
                 "a": "Yes, he left at 21:30. I locked the door behind him myself."},
                {"q": "I heard you have gambling debts.",
                 "a": "...It's true. But I'm trying to quit. I would never steal. I love "
                      "this job."},
            ],
            "innocent": "Ole was on the roof when the camera was switched off - the "
                        "director sent him there. Ole is innocent.",
        },
    },
}


# ==========================================================================
# CASE 2 - Blackout at Hotel Aurora (medium)
# ==========================================================================

CASE_2 = {
    "title": "Blackout at Hotel Aurora",
    "question": "Who stole the Ice Star?",
    "intro": "Hotel Aurora, 23:00. In the middle of the Countess's party, every light "
             "in the hotel goes out. Five minutes of darkness. When the lights come "
             "back, her diamond necklace, the Ice Star, is gone from its glass case.",
    "min_clues": 4, "evidence": 2, "attempts": 3, "glow": 0.45,
    "start": "lobby",
    "rooms": {
        "lobby": {
            "name": "Hotel Lobby", "draw": "lobby", "wall": (58, 50, 44),
            "doors": [{"rect": LEFT_DOOR, "sign": "BALLROOM", "to": "ballroom"},
                      {"rect": RIGHT_DOOR, "sign": "KITCHEN", "to": "kitchen"}],
            "people": [("finch", 420, 440, True), ("countess", 250, 550, False)],
            "spots": [
                {"rect": (515, 312, 85, 40), "label": "Book on the desk", "clue": "keylog",
                 "color": GOLD},
                {"rect": (555, 175, 130, 80), "label": "Key rack",
                 "look": ("Key Rack", "Every key is back on its hook - including the "
                          "basement key. Whoever borrowed it brought it back.")},
                {"rect": (330, 345, 300, 85), "label": "Reception desk",
                 "look": ("Reception Desk", "A brass bell and a vase of white lilies. "
                          "Very elegant.")},
                {"rect": (180, 110, 110, 130), "label": "Portrait",
                 "look": ("Portrait", "Aurora Valdez, founder of the hotel, 1902. She "
                          "looks disappointed in all of you.")},
            ],
        },
        "ballroom": {
            "name": "Ballroom", "draw": "ballroom", "wall": (44, 40, 52),
            "doors": [{"rect": RIGHT_DOOR, "sign": "LOBBY", "to": "lobby"}],
            "people": [("mia", 150, 550, False)],
            "spots": [
                {"rect": (370, 285, 75, 50), "label": "Inside the piano", "clue": "recorder",
                 "color": RED},
                {"rect": (330, 425, 60, 30), "label": "Under the bench", "clue": "clasp",
                 "color": ICE},
                {"rect": (240, 270, 250, 150), "label": "Grand piano",
                 "look": ("Grand Piano", "A shiny black grand piano. The lid is open.")},
                {"rect": (620, 270, 100, 165), "label": "Display case",
                 "look": ("Empty Display Case", "The lock was opened, not broken. The Ice "
                          "Star lay on this velvet cushion until 23:00.")},
                {"rect": (540, 100, 100, 140), "label": "Window",
                 "look": ("Window", "Closed and locked. The thief didn't come from "
                          "outside.")},
            ],
        },
        "kitchen": {
            "name": "Hotel Kitchen", "draw": "kitchen", "wall": (60, 62, 60),
            "doors": [{"rect": LEFT_DOOR, "sign": "LOBBY", "to": "lobby"},
                      {"rect": RIGHT_DOOR, "sign": "BASEMENT", "to": "fuseroom"}],
            "people": [("bruno", 480, 550, False)],
            "spots": [
                {"rect": (282, 308, 56, 36), "label": "Glove", "clue": "glove",
                 "color": WHITE},
                {"rect": (712, 340, 64, 95), "label": "Rubbish bin", "clue": "letter",
                 "color": WHITE},
                {"rect": (190, 150, 170, 60), "label": "Shelf",
                 "look": ("Timer Shelf", "A row of egg timers. One of them is missing.")},
                {"rect": (555, 315, 150, 115), "label": "Stove",
                 "look": ("Stove", "Pots of soup, still bubbling. Smells amazing.")},
                {"rect": (360, 455, 90, 40), "label": "Cake on the floor",
                 "look": ("Ruined Cake", "A three-layer chocolate cake, dropped in the "
                          "dark. A tragedy.")},
            ],
        },
        "fuseroom": {
            "name": "Fuse Room", "draw": "fuseroom", "wall": (36, 38, 40),
            "doors": [{"rect": LEFT_DOOR, "sign": "KITCHEN", "to": "kitchen"}],
            "people": [],
            "spots": [
                {"rect": (500, 248, 70, 64), "label": "Something on the fuse box",
                 "clue": "timer", "color": ORANGE},
                {"rect": (585, 455, 85, 45), "label": "Paper on the floor", "clue": "sheet",
                 "color": WHITE},
                {"rect": (410, 150, 160, 175), "label": "Fuse box",
                 "look": ("Main Fuse Box", "The main switch for the whole hotel. Someone "
                          "flipped it off - and later back on.")},
                {"rect": (700, 190, 100, 240), "label": "Boiler",
                 "look": ("Boiler", "An old boiler. It rumbles like a grumpy bear.")},
            ],
        },
    },
    "clues": {
        "recorder": ("Tape Recorder",
                     "Hidden inside the piano: a tape recorder with the Moonlight Sonata on "
                     "it. The piano music in the dark was a recording!"),
        "clasp": ("Broken Clasp",
                  "Under the piano bench: a broken silver clasp from the Ice Star "
                  "necklace."),
        "keylog": ("Key Log",
                   "The key log at reception: 'Basement key - borrowed 19:10 - M. Rossi.' "
                   "Mia Rossi is the pianist."),
        "timer": ("Egg Timer",
                  "An egg timer from the kitchen is wired to the main switch. It was set "
                  "for exactly 23:00 - the blackout was planned."),
        "sheet": ("Sheet Music",
                  "A torn page of sheet music on the basement floor. Pencil notes in the "
                  "corner, signed 'M.'"),
        "glove": ("Flour Glove",
                  "A white glove covered in flour, lying on the kitchen counter."),
        "letter": ("Bank Letter",
                   "A crumpled letter in the bin: the bank demands that Manager Finch pays "
                   "back 50,000 by Friday."),
    },
    "culprit": "mia",
    "strong": ["recorder", "clasp", "keylog", "sheet"],
    "weak_text": {
        "timer": "The timer proves the blackout was planned - but not who planned it. "
                 "Anyone could walk into the kitchen.",
        "glove": "Every cook in this hotel has flour on their gloves. That proves nothing.",
        "letter": "Money trouble is a motive, not a proof.",
    },
    "confession": "Mia Rossi confesses!",
    "solution": "Mia stole an egg timer from the kitchen, borrowed the basement key at "
                "19:10 and wired the timer to the main switch - dropping a page of her "
                "sheet music. At 23:00 the lights went out, and a tape recorder in the "
                "piano kept 'playing' for her. In the dark she grabbed the Ice Star, but "
                "the clasp broke and fell under the piano bench.",
    "suspects": {
        "countess": {
            "name": "Countess Valentina", "role": "Owner of the Ice Star", "style": "countess",
            "accent": CYAN,
            "greeting": "Darling detective, my Ice Star! Find it, I beg you!",
            "topics": [
                {"q": "What happened tonight?",
                 "a": "At 23:00 the lights went out. Five minutes of darkness! When they "
                      "came back, the glass case was open and empty."},
                {"q": "Did you hear anything in the dark?",
                 "a": "Only that lovely piano music. Mia played the whole time - without "
                      "one single mistake. In complete darkness!"},
                {"q": "Is the necklace insured?",
                 "a": "Insured? Darling, I never insure anything. I trust people."},
                {"q": "Is this clasp from your necklace?", "req": "clasp",
                 "a": "Yes! That's from my Ice Star! Where did you find it?"},
            ],
            "innocent": "Why would the Countess steal her own necklace? It wasn't even "
                        "insured. She is innocent.",
        },
        "finch": {
            "name": "Mr. Finch", "role": "Hotel Manager", "style": "manager", "accent": RED,
            "greeting": "Welcome to the Aurora! Please, keep this quiet. Our reputation!",
            "topics": [
                {"q": "Where were you during the blackout?",
                 "a": "Right here at the desk with a candle, calming the guests. At least "
                      "ten people saw me."},
                {"q": "Who can go into the fuse room?",
                 "a": "Staff only. Anybody else has to borrow the key here and sign the "
                      "key log."},
                {"q": "Did anything strange happen today?",
                 "a": "The piano came back from the tuner this morning. The movers said it "
                      "was heavier than usual."},
                {"q": "You owe the bank money?", "req": "letter",
                 "a": "...Yes. Times are hard. But I would never rob my own guests!"},
            ],
            "innocent": "Finch stood at the desk with a candle during the whole blackout - "
                        "ten guests saw him. He is innocent.",
        },
        "bruno": {
            "name": "Bruno", "role": "Chef", "style": "chef", "accent": ORANGE,
            "greeting": "Out of my kitchen! ...Oh, a detective. Fine. Be quick.",
            "topics": [
                {"q": "Where were you during the blackout?",
                 "a": "Here, with my three cooks. We dropped a whole cake in the dark. A "
                      "tragedy!"},
                {"q": "Did anyone come into the kitchen today?",
                 "a": "Mia, the pianist. At 19:00 she asked me how to get to the basement. "
                      "Strange question for a pianist."},
                {"q": "Is this your glove?", "req": "glove",
                 "a": "Of course! It's covered in flour - I'm a chef. I lost it this "
                      "morning."},
                {"q": "Is this egg timer from your kitchen?", "req": "timer",
                 "a": "Looks like one of mine. One went missing yesterday. Anyone can walk "
                      "in here."},
            ],
            "innocent": "Bruno was in the kitchen with three cooks during the blackout. "
                        "He is innocent.",
        },
        "mia": {
            "name": "Mia Rossi", "role": "Pianist", "style": "pianist", "accent": PINK,
            "greeting": "Shh... can't you see I'm practising?",
            "topics": [
                {"q": "Where were you during the blackout?",
                 "a": "At the piano, of course. I played the Moonlight Sonata in the dark. "
                      "Everyone heard me."},
                {"q": "Why did you borrow the basement key?", "req": "keylog",
                 "a": "Basement key? Oh, um... I was looking for the bathroom."},
                {"q": "What is this recorder in your piano?", "req": "recorder",
                 "a": "That's... for recording my practice. Lots of pianists do that!"},
                {"q": "Is this your sheet music?", "req": "sheet",
                 "a": "Lots of people play music. Lots of names start with M."},
            ],
            "innocent": "",
        },
    },
}


# ==========================================================================
# CASE 3 - The Stolen Formula (hard)
# ==========================================================================

CASE_3 = {
    "title": "The Stolen Formula",
    "question": "Who stole the formula?",
    "intro": "A thunderstorm over Ravenwood Manor. Professor Ada Ravenwood has invented "
             "a battery that could change the world. During her dinner party, the "
             "formula vanished from the safe in her laboratory. Five guests. One thief. "
             "And this time, someone wants you to blame the wrong person.",
    "min_clues": 5, "evidence": 3, "attempts": 2, "glow": 0.0,
    "start": "dining",
    "rooms": {
        "dining": {
            "name": "Dining Room", "draw": "dining", "wall": (60, 42, 40),
            "doors": [{"rect": LEFT_DOOR, "sign": "GREENHOUSE", "to": "greenhouse"},
                      {"rect": RIGHT_DOOR, "sign": "LIBRARY", "to": "library"}],
            "people": [("felix", 420, 450, True), ("hargreaves", 200, 550, False)],
            "spots": [
                {"rect": (620, 238, 75, 36), "label": "Notes on the sideboard",
                 "clue": "notes", "color": WHITE},
                {"rect": (625, 330, 50, 30), "label": "Ashtray",
                 "look": ("Ashtray", "At Mr. Crane's seat: a half-smoked cigar. It smells "
                          "of cherries.")},
                {"rect": (180, 360, 600, 75), "label": "Dinner table",
                 "look": ("Dinner Table", "Seven plates, half-eaten cake and melted "
                          "candles. Next to one plate there is a small empty space.")},
                {"rect": (300, 105, 100, 130), "label": "Portrait",
                 "look": ("Portrait", "Professor Ada Ravenwood. Her new battery could "
                          "power a whole city for a week.")},
            ],
        },
        "library": {
            "name": "Library", "draw": "library", "wall": (40, 46, 42),
            "doors": [{"rect": LEFT_DOOR, "sign": "DINING ROOM", "to": "dining"},
                      {"rect": RIGHT_DOOR, "sign": "LABORATORY", "to": "lab"}],
            "people": [("lily", 270, 550, False)],
            "spots": [
                {"rect": (435, 400, 75, 32), "label": "Paper in the fireplace",
                 "clue": "telegram", "color": ORANGE},
                {"rect": (528, 357, 52, 30), "label": "Camera", "clue": "photos",
                 "color": CYAN},
                {"rect": (590, 90, 190, 330), "label": "Bookshelf", "clue": "passage",
                 "color": GOLD},
                {"rect": (370, 250, 150, 180), "label": "Fireplace",
                 "look": ("Fireplace", "The fire is still warm. Someone burnt papers here "
                          "tonight.")},
                {"rect": (160, 90, 190, 330), "label": "Bookshelf",
                 "look": ("Bookshelf", "Books about electricity, magnets and... cake "
                          "recipes.")},
            ],
        },
        "lab": {
            "name": "Laboratory", "draw": "lab", "wall": (48, 54, 62),
            "doors": [{"rect": LEFT_DOOR, "sign": "LIBRARY", "to": "library"}],
            "people": [("nora", 520, 550, False)],
            "spots": [
                {"rect": (590, 438, 55, 28), "label": "Something shiny", "clue": "hairpin",
                 "color": GOLD},
                {"rect": (682, 440, 56, 28), "label": "Grey dust", "clue": "ash",
                 "color": SILVER},
                {"rect": (620, 250, 125, 145), "label": "Safe", "clue": "safe",
                 "color": GOLD},
                {"rect": (300, 105, 260, 135), "label": "Blackboard",
                 "look": ("Blackboard", "Formulas everywhere. One line says: 'Battery: 10x "
                          "stronger!' The rest is gibberish to you.")},
                {"rect": (150, 330, 300, 100), "label": "Lab bench",
                 "look": ("Lab Bench", "Flasks, wires and a half-eaten sandwich.")},
                {"rect": (790, 180, 110, 250), "label": "Strange machine",
                 "look": ("Strange Machine", "Copper coils that hum quietly. You decide "
                          "not to touch it.")},
            ],
        },
        "greenhouse": {
            "name": "Greenhouse", "draw": "greenhouse", "wall": (30, 40, 44),
            "doors": [{"rect": RIGHT_DOOR, "sign": "DINING ROOM", "to": "dining"}],
            "people": [("victor", 470, 550, False)],
            "spots": [
                {"rect": (655, 290, 80, 120), "label": "Behind the palm", "clue": "coat",
                 "color": GOLD},
                {"rect": (160, 300, 220, 130), "label": "Flower pots",
                 "look": ("Flower Pots", "Orchids, cactuses and one very sad tomato.")},
                {"rect": (600, 150, 170, 280), "label": "Palm tree",
                 "look": ("Palm Tree", "A huge palm. Its leaves are wet - somebody brushed "
                          "past it with a wet coat.")},
            ],
        },
    },
    "clues": {
        "safe": ("Open Safe",
                 "The safe was opened with the code, not forced. Only the professor, Nora "
                 "and Mr. Crane know the code."),
        "hairpin": ("Hairpin",
                    "A silver hairpin with the letter N, right in front of the safe. "
                    "Almost too easy to find..."),
        "ash": ("Cigar Ash",
                "Fresh cigar ash on the lab floor. It smells of cherries."),
        "telegram": ("Burnt Telegram",
                     "Half-burnt: '...SOLARCORP PAYS 1 MILLION FOR THE FORMULA. DELIVER "
                     "TONIGHT.' Addressed to: V. Crane."),
        "photos": ("Lily's Photos",
                   "Photos of the lab door, taken at 20:15 and 20:50. Both times the door "
                   "is closed and locked."),
        "passage": ("Secret Passage",
                    "One bookshelf slides aside: a secret passage to the laboratory! "
                    "That's how the thief got past the locked lab door."),
        "notes": ("Butler's Notes",
                  "Who left the table: 20:30 Felix (5 min). 20:40 Mr. Crane (15 min). "
                  "20:50 Nora (3 min, fetched dessert)."),
        "coat": ("Hidden Coat",
                 "A wet coat behind the palm. In the pocket: a train ticket for 06:00 "
                 "tomorrow. Name: V. Crane."),
    },
    "culprit": "victor",
    "strong": ["ash", "telegram", "notes", "coat"],
    "weak_text": {
        "safe": "Three people know the code. The open safe alone doesn't tell you which "
                "one it was.",
        "hairpin": "The hairpin points at Nora - not at the person you accused.",
        "photos": "The photos show the lab door was locked. Useful - but they don't "
                  "show the thief.",
        "passage": "The passage explains HOW the thief got in - not WHO it was.",
    },
    "confession": "Victor Crane confesses!",
    "solution": "Victor Crane sold the formula to SolarCorp for one million. At 20:40 he "
                "left the dinner and took Nora's hairpin from the table. He used the "
                "secret passage in the library, opened the safe with the code and dropped "
                "the hairpin to frame Nora - but the ash of his cherry cigar gave him "
                "away. He burnt the telegram and hid his wet coat with the train ticket "
                "in the greenhouse, ready to escape at 06:00.",
    "suspects": {
        "nora": {
            "name": "Nora Blake", "role": "Lab Assistant", "style": "labcoat", "accent": GREEN,
            "greeting": "Detective, please - the professor thinks I did it. I would never!",
            "topics": [
                {"q": "Who knows the safe code?",
                 "a": "Only the professor, me and Mr. Crane, her business partner."},
                {"q": "Where were you at 20:40?",
                 "a": "At the dinner table. At 20:50 I fetched dessert from the kitchen - "
                      "three minutes. The cook saw me."},
                {"q": "Is this your hairpin?", "req": "hairpin",
                 "a": "Yes! I took it off at dinner because it hurt. I left it next to my "
                      "plate. How did it get here?"},
                {"q": "Did you know about the passage?", "req": "passage",
                 "a": "A secret passage? No! I always use the normal lab door."},
            ],
            "innocent": "The hairpin was planted. Hargreaves saw it next to Nora's plate "
                        "until 20:45, and she only left the table for three minutes. "
                        "Nora was framed!",
        },
        "felix": {
            "name": "Felix", "role": "The Professor's Nephew", "style": "nephew",
            "accent": ORANGE,
            "greeting": "A stolen formula? Boring. Is there more cake?",
            "topics": [
                {"q": "Where were you at 20:40?",
                 "a": "On the phone in the hall from 20:30, five minutes. Then back to my "
                      "cake."},
                {"q": "Will you inherit everything one day?",
                 "a": "Maybe. But the formula is worth nothing to me. I can't even read "
                      "it."},
                {"q": "What do you think of Mr. Crane?",
                 "a": "Victor? Nervous all evening. He kept looking at his watch."},
            ],
            "innocent": "Felix was only gone for five minutes and doesn't know the safe "
                        "code. He is innocent.",
        },
        "hargreaves": {
            "name": "Mr. Hargreaves", "role": "Butler", "style": "butler", "accent": SILVER,
            "greeting": "Good evening. I have served the professor for thirty years. Ask me "
                        "anything.",
            "topics": [
                {"q": "Did anyone leave the dinner table?",
                 "a": "I keep notes of everything, sir. You'll find them on the sideboard."},
                {"q": "Who smokes in this house?",
                 "a": "Only Mr. Crane. Those dreadful cherry cigars."},
                {"q": "Did you hear anything strange?",
                 "a": "Thunder. And at 20:45 a creak from the library. Old houses creak, "
                      "sir."},
                {"q": "Did you see Nora's hairpin?", "req": "hairpin",
                 "a": "Indeed. It lay next to her plate. When I cleared the table at "
                      "20:45, it was gone."},
            ],
            "innocent": "The butler served dinner all evening in front of every guest. "
                        "He is innocent.",
        },
        "lily": {
            "name": "Lily Chen", "role": "Journalist", "style": "journalist", "accent": CYAN,
            "greeting": "Lily Chen, Daily Herald. Off the record? I didn't take it.",
            "topics": [
                {"q": "Why are you here?",
                 "a": "An interview with the professor about her new battery. Big story."},
                {"q": "Did you notice anything in here?",
                 "a": "At 20:45 I came in to look for a book. The whole room smelled of "
                      "cherries. Funny, right?"},
                {"q": "Why did you photograph the lab door?", "req": "photos",
                 "a": "For my article! Look at the times - the door was locked both "
                      "times."},
                {"q": "Did you know about this passage?", "req": "passage",
                 "a": "No! Wow. That's going on the front page."},
            ],
            "innocent": "Lily's own photos show the lab door stayed locked, and she didn't "
                        "know about the passage. She is innocent.",
        },
        "victor": {
            "name": "Victor Crane", "role": "Business Partner", "style": "partner",
            "accent": (200, 120, 60),
            "greeting": "Detective. Terrible business. Simply terrible.",
            "topics": [
                {"q": "Where were you at 20:40?",
                 "a": "I went out for some fresh air. Here in the greenhouse. The whole "
                      "time, I promise."},
                {"q": "Who knows the safe code?",
                 "a": "The professor, Nora and me. Nora has money problems, you know..."},
                {"q": "Do you smoke cherry cigars?", "req": "ash",
                 "a": "Who doesn't? A fine cigar. That proves nothing."},
                {"q": "What is this telegram?", "req": "telegram",
                 "a": "Never seen it. 'V. Crane'? Lots of people have that name."},
                {"q": "Is this your coat?", "req": "coat",
                 "a": "...My coat? Someone must have taken it by mistake."},
            ],
            "innocent": "",
        },
    },
}

# ==========================================================================
# CASE 4 - Snowbound Express (hard)
# ==========================================================================

CASE_4 = {
    "title": "Snowbound Express",
    "question": "Who stole the Emperor's Egg?",
    "intro": "The night train from Vienna to Venice is stuck in a snowstorm high in "
             "the Alps. At midnight the Emperor's Egg - a golden egg covered in jewels - "
             "vanished from the locked luggage car. The snow is three metres deep. "
             "Nobody could have left the train. The thief is still on board.",
    "min_clues": 6, "evidence": 3, "attempts": 2, "glow": 0.0,
    "start": "dining",
    "rooms": {
        "lounge": {
            "name": "Lounge Car", "draw": "lounge", "wall": (62, 40, 46),
            "doors": [{"rect": RIGHT_DOOR, "sign": "DINING CAR", "to": "dining"}],
            "people": [("odile", 520, 550, False)],
            "spots": [
                {"rect": (355, 368, 70, 32), "label": "Paper on the table", "clue": "program"},
                {"rect": (180, 345, 110, 50), "label": "Armchair", "clue": "telegram"},
                {"rect": (600, 300, 200, 130), "label": "Bar",
                 "look": ("Bar", "Bottles clink every time the wind shakes the train. "
                          "The barman went to bed hours ago.")},
                {"rect": (690, 240, 70, 60), "label": "Gramophone",
                 "look": ("Gramophone", "A record of Odile Fontaine singing La Traviata. "
                          "Signed by herself. Twice.")},
                {"rect": (245, 110, 170, 130), "label": "Window",
                 "look": ("Window", "Snow, snow and more snow. The mountains glow in the "
                          "moonlight.")},
            ],
        },
        "dining": {
            "name": "Dining Car", "draw": "train_dining", "wall": (72, 50, 36),
            "doors": [{"rect": LEFT_DOOR, "sign": "LOUNGE CAR", "to": "lounge"},
                      {"rect": RIGHT_DOOR, "sign": "SLEEPING CAR", "to": "sleeper"}],
            "people": [("baron", 300, 550, False), ("teo", 580, 550, False)],
            "spots": [
                {"rect": (680, 325, 70, 34), "label": "Serving cart", "clue": "order"},
                {"rect": (420, 318, 100, 30), "label": "Chess board",
                 "look": ("Chess Board", "The Baron's chess game. White is winning. So is "
                          "black. He plays against himself.")},
                {"rect": (180, 320, 160, 110), "label": "Table",
                 "look": ("Table", "Half a strudel and a cold cup of tea. Dr. Hassan "
                          "sat here at dinner.")},
                {"rect": (640, 110, 120, 120), "label": "Window",
                 "look": ("Window", "The snowstorm has buried the tracks. Nobody is "
                          "going anywhere tonight.")},
            ],
        },
        "sleeper": {
            "name": "Sleeping Car", "draw": "sleeper", "wall": (66, 50, 38),
            "doors": [{"rect": LEFT_DOOR, "sign": "DINING CAR", "to": "dining"},
                      {"rect": RIGHT_DOOR, "sign": "LUGGAGE CAR", "to": "luggage"}],
            "people": [("pavel", 230, 550, False), ("hassan", 520, 550, False)],
            "spots": [
                {"rect": (330, 318, 64, 44), "label": "Bag in compartment 2", "clue": "drops"},
                {"rect": (608, 312, 74, 56), "label": "Hatbox in compartment 4",
                 "clue": "egg", "needs": "program",
                 "locked": ("Hatbox", "A hatbox with a 4-digit combination lock. Maybe "
                            "its owner wrote her lucky number down somewhere...")},
                {"rect": (640, 432, 170, 48), "label": "Carpet", "clue": "heels"},
                {"rect": (165, 200, 120, 230), "label": "Compartment 1",
                 "look": ("Compartment 1", "Pavel's tiny compartment. A uniform, a timetable "
                          "and a photo of his cat.")},
                {"rect": (445, 200, 120, 230), "label": "Compartment 3",
                 "look": ("Compartment 3", "The Baron's compartment. Seven suitcases and "
                          "a golden toothbrush.")},
            ],
        },
        "luggage": {
            "name": "Luggage Car", "draw": "luggage", "wall": (52, 54, 58),
            "doors": [{"rect": LEFT_DOOR, "sign": "SLEEPING CAR", "to": "sleeper"}],
            "people": [],
            "spots": [
                {"rect": (676, 238, 40, 40), "label": "Something white", "clue": "feather"},
                {"rect": (262, 360, 44, 40), "label": "Cup", "clue": "cup"},
                {"rect": (640, 140, 90, 290), "label": "Cage door", "clue": "cage"},
                {"rect": (170, 300, 90, 130), "label": "Sleeping guard",
                 "look": ("Mr. Brandt", "The guard is fast asleep and snoring. Even shaking "
                          "him doesn't help.")},
                {"rect": (420, 250, 140, 150), "label": "Empty stand",
                 "look": ("Empty Stand", "A velvet stand inside the cage. This is where the "
                          "Emperor's Egg was.")},
                {"rect": (760, 100, 130, 100), "label": "Window",
                 "look": ("Open Window", "The window is wide open and snow blows in. But "
                          "there are no footprints in the snow outside.")},
            ],
        },
    },
    "clues": {
        "order": ("Order Slip",
                  "'23:30 - one hot chocolate with cream for the guard in the luggage car. "
                  "Paid by: compartment 4.'"),
        "program": ("Opera Program",
                    "A signed program: 'Odile Fontaine - my lucky year: 1896!' Someone "
                    "underlined 1-8-9-6 twice."),
        "telegram": ("Baron's Telegram",
                     "'Your offer for the Emperor's Egg is rejected. - Vienna Museum.' "
                     "Addressed to Baron von Greif."),
        "drops": ("Missing Drops",
                  "Dr. Hassan's medical bag. The bottle of strong sleeping drops is gone."),
        "heels": ("Wet Heel Prints",
                  "Small puddles of melted snow from high heels lead from the luggage car "
                  "to compartment 4."),
        "egg": ("Hidden Egg",
                "1-8-9-6 opens the hatbox. Under a wig: the Emperor's Egg! The hatbox "
                "belongs to compartment 4."),
        "cup": ("Hot Chocolate",
                "A cup next to the sleeping guard. It smells sweet - too sweet. Something "
                "was mixed into the chocolate."),
        "feather": ("White Feather",
                    "A white swan feather caught in the door of the luggage cage."),
        "cage": ("Opened Cage",
                 "The cage was unlocked, not broken. Somebody used the conductor's key."),
    },
    "culprit": "odile",
    "strong": ["order", "heels", "egg", "feather"],
    "weak_text": {
        "drops": "The drops belong to Dr. Hassan. That shows where they came from - not "
                 "who took them.",
        "cage": "The cage was opened with Pavel's key. But who had the key at 23:40?",
        "cup": "The cup shows HOW the guard fell asleep - not who drugged him.",
        "program": "A lucky number in a program proves nothing by itself.",
        "telegram": "A rejected offer is a motive, not a proof.",
    },
    "confession": "Odile Fontaine confesses!",
    "solution": "Odile Fontaine is deep in debt. At dinner she stole Dr. Hassan's "
                "sleeping drops. She ordered a hot chocolate for the guard and poured "
                "the drops in when Teo passed her in the corridor. At 23:40 she took "
                "Pavel's key from his belt, opened the cage and grabbed the egg - leaving "
                "a feather of her boa in the door. She opened the window so it would look "
                "like the thief escaped, walked back with snow on her heels and locked "
                "the egg in her hatbox with her lucky number. Then she 'found' Pavel's key.",
    "suspects": {
        "pavel": {
            "name": "Pavel", "role": "Conductor", "style": "conductor", "accent": GOLD,
            "greeting": "The Snowbound Express has never lost a passenger - or a parcel. "
                        "Until tonight.",
            "topics": [
                {"q": "Who has the luggage car key?",
                 "a": "Only me. It never leaves my belt. Well... at 23:40 I dropped it. "
                      "Madame Fontaine found it and gave it back. Such a kind lady."},
                {"q": "What happened at midnight?",
                 "a": "Mr. Brandt, the guard, didn't answer my knock. I found him asleep "
                      "and the cage open. The egg was gone."},
                {"q": "Can anyone leave the train?",
                 "a": "In this snow? Three metres deep! Whoever took it is still on board."},
                {"q": "The cage was opened with your key!", "req": "cage",
                 "a": "Impossible! It was on my belt the whole... oh. Oh no. The moment I "
                      "'dropped' it."},
            ],
            "innocent": "Pavel's key was taken from his belt at 23:40 - and Madame "
                        "Fontaine 'found' it. Pavel was tricked. He is innocent.",
        },
        "hassan": {
            "name": "Dr. Hassan", "role": "Doctor", "style": "doctor", "accent": (80, 150, 170),
            "greeting": "Doctor Amira Hassan. If anyone is hurt, I can help. Otherwise I'd "
                        "like to sleep.",
            "topics": [
                {"q": "Where were you at midnight?",
                 "a": "In my compartment, reading. The walls are thin. Around 00:05 I heard "
                      "someone walk past in high heels."},
                {"q": "Who sat next to you at dinner?",
                 "a": "Madame Fontaine. She asked many questions about my medicine. I "
                      "thought she was nervous about sleeping on a train."},
                {"q": "Your sleeping drops are missing.", "req": "drops",
                 "a": "Yes! I noticed it this evening. Someone took the bottle from my bag "
                      "in the dining car."},
                {"q": "Could this cup make a guard sleep?", "req": "cup",
                 "a": "That smell... yes. My sleeping drops. Ten drops and he sleeps for "
                      "hours."},
            ],
            "innocent": "Dr. Hassan's drops were stolen at dinner - and the person sitting "
                        "next to her was Madame Fontaine. Dr. Hassan is innocent.",
        },
        "teo": {
            "name": "Teo", "role": "Waiter", "style": "waiter", "accent": SILVER,
            "greeting": "Something to drink, sir? Sorry - I'm a bit nervous tonight.",
            "topics": [
                {"q": "Did you bring the guard anything?",
                 "a": "Yes, a hot chocolate at 23:30. A passenger paid for it. Very "
                      "generous!"},
                {"q": "Who paid for the chocolate?",
                 "a": "I don't remember the name. But it's on the order slip - on my "
                      "serving cart."},
                {"q": "Did you see anything strange?",
                 "a": "At 00:10 Madame Fontaine came in for a glass of water. The hem of "
                      "her dress was wet. Wet, on a train!"},
                {"q": "Did anyone touch the chocolate?", "req": "cup",
                 "a": "Only me! Well... Madame Fontaine stopped me in the corridor to smell "
                      "it. Just for a second."},
            ],
            "innocent": "Teo only carried the chocolate. The order slip shows who paid for "
                        "it. Teo is innocent.",
        },
        "baron": {
            "name": "Baron von Greif", "role": "Art Collector", "style": "baron",
            "accent": (200, 170, 80),
            "greeting": "Yes, I wanted the egg. No, I did not steal it. One buys - one "
                        "does not steal.",
            "topics": [
                {"q": "Where were you at midnight?",
                 "a": "Here, playing chess against myself. Teo can confirm. I won."},
                {"q": "Who else wanted the egg?",
                 "a": "Madame Fontaine asked me what it is worth. She seemed... very "
                      "interested. Opera singers earn less than you think."},
                {"q": "The museum rejected your offer?", "req": "telegram",
                 "a": "Annoying. But a collector who steals can never show his collection. "
                      "Pointless!"},
            ],
            "innocent": "The Baron played chess in the dining car all night - Teo saw him. "
                        "He is innocent.",
        },
        "odile": {
            "name": "Odile Fontaine", "role": "Opera Singer", "style": "singer",
            "accent": (235, 235, 235),
            "greeting": "Darling, are you here for an autograph? ...No? How disappointing.",
            "topics": [
                {"q": "Where were you at midnight?",
                 "a": "Asleep in compartment 4, of course. A voice like mine needs rest."},
                {"q": "You paid for the guard's chocolate.", "req": "order",
                 "a": "A kind gesture! The poor man was cold. Is kindness a crime now?"},
                {"q": "This feather is from your boa.", "req": "feather",
                 "a": "Lots of ladies wear feathers, darling."},
                {"q": "Wet heel prints lead to your door.", "req": "heels",
                 "a": "I... went to look at the snow. It's romantic. Is that forbidden?"},
                {"q": "Why is the egg in your hatbox?", "req": "egg",
                 "a": "Someone put it there! A trap! I'm innocent, darling!"},
            ],
            "innocent": "",
        },
    },
}


# ==========================================================================
# CASE 5 - Circus of Shadows (very hard)
# ==========================================================================

CASE_5 = {
    "title": "Circus of Shadows",
    "question": "Who cut the trapeze rope?",
    "intro": "Circus Lumiere, opening night. During the final act the trapeze rope "
             "snapped. Star acrobat Stella fell - straight into the safety net, unhurt. "
             "But the rope had been cut. Someone wanted the show to fail tonight. Six "
             "suspects, one saboteur - and only one chance to name them.",
    "min_clues": 7, "evidence": 3, "attempts": 1, "glow": 0.0,
    "start": "bigtop",
    "rooms": {
        "bigtop": {
            "name": "Big Top", "draw": "bigtop", "wall": (100, 38, 46), "wall2": (150, 136, 116),
            "doors": [{"rect": LEFT_DOOR, "sign": "BACKSTAGE", "to": "backstage"},
                      {"rect": RIGHT_DOOR, "sign": "CARAVANS", "to": "caravans"}],
            "people": [("krone", 470, 560, False), ("grey", 760, 550, False)],
            "spots": [
                {"rect": (662, 236, 46, 40), "label": "Rope ladder", "clue": "greasepaint"},
                {"rect": (515, 70, 60, 80), "label": "Snapped rope", "clue": "cutrope"},
                {"rect": (190, 372, 44, 28), "label": "Seat A1", "clue": "ticket"},
                {"rect": (330, 290, 300, 60), "label": "Safety net",
                 "look": ("Safety Net", "The net that saved Stella's life. Igor checks it "
                          "every day.")},
                {"rect": (160, 340, 140, 90), "label": "Front row",
                 "look": ("Front Row", "Popcorn everywhere. Someone left in a hurry.")},
            ],
        },
        "backstage": {
            "name": "Backstage", "draw": "backstage", "wall": (66, 52, 40),
            "doors": [{"rect": RIGHT_DOOR, "sign": "BIG TOP", "to": "bigtop"}],
            "people": [("pip", 150, 550, False), ("igor", 560, 550, False)],
            "spots": [
                {"rect": (378, 282, 52, 26), "label": "Knife", "clue": "knife"},
                {"rect": (255, 115, 160, 120), "label": "Make-up mirror", "clue": "mirror"},
                {"rect": (748, 160, 54, 270), "label": "Locker 7", "clue": "locker",
                 "needs": "lockerkey",
                 "locked": ("Locker 7", "Locked. A small sticker on the door shows a red "
                            "clown nose. You need the key.")},
                {"rect": (480, 130, 140, 200), "label": "Costume rack",
                 "look": ("Costume Rack", "Sequins, feathers, a lion costume... and a very "
                          "sad-looking unicorn.")},
                {"rect": (640, 160, 106, 270), "label": "Lockers 5 and 6",
                 "look": ("Lockers", "Igor's and Lia's lockers. Both open, both boring.")},
            ],
        },
        "fortune": {
            "name": "Fortune Teller's Tent", "draw": "fortune", "wall": (44, 26, 52),
            "doors": [{"rect": LEFT_DOOR, "sign": "CARAVANS", "to": "caravans"}],
            "people": [("zora", 480, 450, True)],
            "spots": [
                {"rect": (392, 360, 56, 22), "label": "Book on the table", "clue": "zorabook"},
                {"rect": (180, 115, 120, 160), "label": "Poster", "clue": "prediction"},
                {"rect": (455, 318, 52, 50), "label": "Crystal ball",
                 "look": ("Crystal Ball", "It glows softly. You see... your own nose. Very "
                          "mysterious.")},
                {"rect": (520, 360, 80, 25), "label": "Tarot cards",
                 "look": ("Tarot Cards", "The top card: THE TOWER. A tower struck by "
                          "lightning, people falling.")},
            ],
        },
        "caravans": {
            "name": "Caravans", "draw": "caravans", "wall": (14, 14, 34),
            "doors": [{"rect": LEFT_DOOR, "sign": "BIG TOP", "to": "bigtop"},
                      {"rect": RIGHT_DOOR, "sign": "FORTUNE TELLER", "to": "fortune"}],
            "people": [("lia", 470, 555, False)],
            "spots": [
                {"rect": (330, 392, 48, 46), "label": "Flower pot", "clue": "lockerkey"},
                {"rect": (690, 402, 44, 34), "label": "Bag on the steps", "clue": "chalk"},
                {"rect": (170, 200, 230, 200), "label": "Caravan with a red nose",
                 "look": ("Pip's Caravan", "A red nose is painted on the door. It's locked "
                          "and the curtains are closed.")},
                {"rect": (540, 210, 230, 190), "label": "Caravan with a light",
                 "look": ("Lia's Caravan", "Through the window you see a mat, weights and a "
                          "poster of Stella - with darts in it.")},
            ],
        },
    },
    "clues": {
        "cutrope": ("Cut Rope",
                    "The rope was cut almost through with a sharp blade - hours before the "
                    "show. Then it was rubbed with dust to hide the cut."),
        "greasepaint": ("White Face Paint",
                        "Greasy white smudges on the rope ladder up to the trapeze. Not "
                        "chalk - it's face paint, like clowns wear."),
        "ticket": ("VIP Ticket",
                   "Seat A1, front row. On the back, in pencil: 'Bonus when the show is "
                   "ruined. - G.'"),
        "knife": ("Igor's Knife",
                  "The strongman's knife, lying on the make-up table. Tiny rope fibres "
                  "stick to the blade."),
        "mirror": ("Writing on the Mirror",
                   "Pip's make-up mirror. Written in white face paint: 'A1 - after the "
                   "show - 5000'."),
        "locker": ("Envelope in Locker 7",
                   "Pip's locker: an envelope with 5,000 and a business card - 'Circus "
                   "Noir, C. Grey'."),
        "zorabook": ("Zora's Appointment Book",
                     "'18:30 - Pip. Asked if the trapeze will hold tonight. Strange "
                     "question for a clown.'"),
        "prediction": ("Zora's Poster",
                       "'Madame Zora predicts: tonight, a star will fall!'"),
        "lockerkey": ("Small Key",
                      "A small key marked '7', hidden in a flower pot next to the caravan "
                      "with the red nose."),
        "chalk": ("Chalk Bag",
                  "Lia's chalk bag, half empty. Acrobats use chalk for their hands."),
    },
    "culprit": "pip",
    "strong": ["greasepaint", "mirror", "locker", "zorabook"],
    "weak_text": {
        "cutrope": "The cut rope proves it was sabotage - not who did it.",
        "ticket": "The ticket points at Mr. Grey and a promise. But who actually climbed "
                  "up and cut the rope?",
        "knife": "The knife belongs to Igor. But whose hands were holding it?",
        "prediction": "A fortune teller's prediction is no proof in court.",
        "lockerkey": "A key alone proves nothing. What does it open?",
        "chalk": "Every acrobat uses chalk. This proves nothing.",
    },
    "confession": "Pip the clown confesses!",
    "solution": "Pip was going to lose his job after this season. Mr. Grey of Circus Noir "
                "offered him 5,000 and his own show if he ruined opening night. Pip asked "
                "Madame Zora if the trapeze would hold, borrowed Igor's knife at 17:00 and "
                "climbed the rope ladder - leaving white face paint on it - to cut the "
                "rope almost through. The money waited in his locker, and he wrote the "
                "deal on his mirror so he wouldn't forget it. (Mr. Grey will have to "
                "explain himself to the police, too.)",
    "suspects": {
        "krone": {
            "name": "Krone", "role": "Ringmaster", "style": "ringmaster", "accent": RED,
            "greeting": "Maximilian Krone, Ringmaster! The show must go on - but who wants "
                        "to destroy my show?",
            "topics": [
                {"q": "Is Stella insured?",
                 "a": "Of course! But without Stella there is no Circus Lumiere. I'd be "
                      "ruined, not rich."},
                {"q": "Who wants to hurt your circus?",
                 "a": "Mr. Grey of Circus Noir. He wants to buy us cheap. He sat in seat A1 "
                      "tonight, grinning like a shark."},
                {"q": "Is anyone leaving the circus?",
                 "a": "Pip. I told him last week that this is his last season. He took "
                      "it... badly."},
                {"q": "Is this Mr. Grey's ticket?", "req": "ticket",
                 "a": "Seat A1 - yes, I gave him that seat myself. 'Bonus when the show is "
                      "ruined'? That snake!"},
            ],
            "innocent": "Without Stella the ringmaster is ruined. He wanted to protect the "
                        "show, not destroy it. Krone is innocent.",
        },
        "pip": {
            "name": "Pip", "role": "Clown", "style": "clown", "accent": RED,
            "greeting": "Honk honk! Sorry, sorry. Not the moment for jokes, eh?",
            "topics": [
                {"q": "Where were you before the show?",
                 "a": "Making balloon animals for the kids! All afternoon. Ask anyone. Well, "
                      "ask the balloons."},
                {"q": "You borrowed Igor's knife.", "req": "knife",
                 "a": "For a balloon string! You can't cut balloon strings with your teeth, "
                      "can you?"},
                {"q": "Why is face paint on the ladder?", "req": "greasepaint",
                 "a": "Face paint? No, no. That's chalk! Lia's chalk! Yes."},
                {"q": "What does 'A1 - 5000' mean?", "req": "mirror",
                 "a": "It's... a phone number! Of my aunt! She lives in... A1."},
                {"q": "Why does Circus Noir pay you 5,000?", "req": "locker",
                 "a": "...They promised me my own show. Krone was going to fire me! I only "
                      "wanted Stella to miss one night!"},
            ],
            "innocent": "",
        },
        "lia": {
            "name": "Lia", "role": "Acrobat", "style": "acrobat", "accent": PINK,
            "greeting": "Before you ask: yes, I want Stella's spot. No, I would never cut a "
                        "rope. Ropes are sacred.",
            "topics": [
                {"q": "Where were you before the show?",
                 "a": "Training in my caravan from 17:00 to 19:30. Igor saw me through the "
                      "window - I stood on my hands for an hour."},
                {"q": "Who climbs the rope ladder?",
                 "a": "Only Stella, me and Igor. Nobody else would dare. Well, nobody "
                      "sane."},
                {"q": "Your chalk bag is half empty.", "req": "chalk",
                 "a": "Because I use it every day! Every acrobat does. Even Stella."},
                {"q": "What is on the rope ladder?", "req": "greasepaint",
                 "a": "That's not chalk - chalk is dusty. That's greasy white face paint. "
                      "Only one person here wears that."},
            ],
            "innocent": "Igor watched Lia train in her caravan the whole time the rope could "
                        "have been cut. Lia is innocent.",
        },
        "zora": {
            "name": "Madame Zora", "role": "Fortune Teller", "style": "fortune",
            "accent": PURPLE,
            "greeting": "I knew you would come, detective. The cards told me. Also, I saw "
                        "you walking over.",
            "topics": [
                {"q": "Who visited you today?",
                 "a": "Only one customer before the show. It's all in my appointment book."},
                {"q": "Can you see who did it?",
                 "a": "The crystal shows... a red nose. Or it's a reflection of the lamp. "
                      "The crystal is very old."},
                {"q": "You predicted a falling star!", "req": "prediction",
                 "a": "The cards showed THE TOWER - sudden disaster. And a clown asked me if "
                      "the trapeze would hold. I can add two and two."},
            ],
            "innocent": "Zora only repeated what a clown had asked her. Her 'prediction' was "
                        "good guessing. She is innocent.",
        },
        "igor": {
            "name": "Igor", "role": "Strongman", "style": "strongman", "accent": BLUE,
            "greeting": "Igor checks the ropes every morning. This morning: perfect! "
                        "Tonight: snap! Igor is very angry.",
            "topics": [
                {"q": "When did you check the rope?",
                 "a": "At 10:00. It was perfect. Somebody cut it after that."},
                {"q": "Who has the locker keys?",
                 "a": "Every artist has their own key. Pip always loses his. He hides it in "
                      "his flower pots."},
                {"q": "Did you see Lia before the show?",
                 "a": "Yes, through her window. On her hands, for an hour. Crazy woman."},
                {"q": "Is this your knife?", "req": "knife",
                 "a": "Yes. Pip borrowed it at 17:00 for a balloon. He brought it back at "
                      "19:00. Two hours for one balloon?"},
            ],
            "innocent": "Igor's knife was with Pip from 17:00 to 19:00 - exactly when the "
                        "rope was cut. Igor is innocent.",
        },
        "grey": {
            "name": "Mr. Grey", "role": "Owner, Circus Noir", "style": "rival",
            "accent": SILVER,
            "greeting": "Cornelius Grey, Circus Noir. I'm only a guest. A very... "
                        "interested guest.",
            "topics": [
                {"q": "Where were you before the show?",
                 "a": "Dinner in town, then seat A1 from 19:30. Lovely show. Shame about "
                      "the ending."},
                {"q": "Do you want to buy this circus?",
                 "a": "Every circus has its price. After tonight, Lumiere's price will be "
                      "much lower."},
                {"q": "'Bonus when the show is ruined'?", "req": "ticket",
                 "a": "My handwriting? Could be anybody's. I want my lawyer."},
                {"q": "Your card was in Pip's locker.", "req": "locker",
                 "a": "Pip? Never heard of him. ...Is he the one with the nose?"},
            ],
            "innocent": "Mr. Grey paid for the sabotage - but he never touched the rope. "
                        "You need the person who cut it. (The police will talk to Mr. Grey "
                        "later.)",
        },
    },
}


# ==========================================================================
# Look & feel of every case
#   scene      - picture behind the case intro (city, hotel, manor, train, carnival)
#   weather    - rain, snow or confetti
#   tint       - colour laid over every room (r, g, b, strength)
#   wall_style - plain, wainscot, wallpaper, brick, train, metal, tent, drape, night
#   floor      - tiles, wood, carpet, concrete, planks, sawdust, grass, stone
#   door       - wood, train or flap
#   enemy      - moving obstacle: polisher, trolley, dog, suitcase or ball
#   enemies    - how many of them are in every room
#   enemy_speed / enemy_mode - pixels per second, "patrol" (left-right) or "bounce"
# Rooms can override wall_style, floor and floor_color.
# ==========================================================================

CASE_1["theme"] = {"scene": "city", "weather": "rain", "tint": (20, 35, 70, 30),
                   "wall_style": "wainscot", "floor": "tiles",
                   "floor_color": (30, 31, 35), "door": "wood",
                   "enemy": "polisher", "enemy_name": "runaway floor polisher",
                   "enemies": 1, "enemy_speed": 90, "enemy_mode": "patrol"}
CASE_1["rooms"]["office"].update(wall_style="wallpaper", floor="wood",
                                 floor_color=(48, 36, 28))
CASE_1["rooms"]["storage"].update(wall_style="brick", floor="concrete",
                                  floor_color=(40, 40, 42))

CASE_2["theme"] = {"scene": "hotel", "weather": "rain", "tint": (80, 50, 10, 30),
                   "wall_style": "wallpaper", "floor": "carpet",
                   "floor_color": (74, 30, 34), "door": "wood",
                   "enemy": "trolley", "enemy_name": "rolling luggage trolleys",
                   "enemies": 2, "enemy_speed": 115, "enemy_mode": "patrol"}
CASE_2["rooms"]["kitchen"].update(wall_style="plain", floor="tiles",
                                  floor_color=(48, 50, 50))
CASE_2["rooms"]["fuseroom"].update(wall_style="brick", floor="concrete",
                                   floor_color=(36, 36, 38))

CASE_3["theme"] = {"scene": "manor", "weather": "rain", "tint": (50, 10, 20, 30),
                   "wall_style": "wainscot", "floor": "wood",
                   "floor_color": (50, 34, 24), "door": "wood", "lightning": True,
                   "enemy": "dog", "enemy_name": "professor's guard dogs",
                   "enemies": 2, "enemy_speed": 150, "enemy_mode": "patrol"}
CASE_3["rooms"]["dining"].update(wall_style="wallpaper")
CASE_3["rooms"]["lab"].update(wall_style="plain", floor="tiles",
                              floor_color=(40, 44, 48))
CASE_3["rooms"]["greenhouse"].update(wall_style="plain", floor="stone",
                                     floor_color=(44, 46, 42))

CASE_4["theme"] = {"scene": "train", "weather": "snow", "tint": (15, 30, 60, 25),
                   "wall_style": "train", "floor": "carpet",
                   "floor_color": (64, 24, 30), "door": "train",
                   "enemy": "suitcase", "enemy_name": "suitcases sliding around the shaking train",
                   "enemies": 3, "enemy_speed": 150, "enemy_mode": "bounce"}
CASE_4["rooms"]["luggage"].update(wall_style="metal", floor="planks",
                                  floor_color=(54, 44, 34))

CASE_5["theme"] = {"scene": "carnival", "weather": "confetti", "tint": (60, 10, 70, 28),
                   "wall_style": "tent", "floor": "sawdust",
                   "floor_color": (84, 68, 48), "door": "flap",
                   "enemy": "ball", "enemy_name": "bouncing circus balls",
                   "enemies": 4, "enemy_speed": 185, "enemy_mode": "bounce"}
CASE_5["rooms"]["backstage"].update(wall_style="wainscot", floor="planks",
                                    floor_color=(56, 44, 34))
CASE_5["rooms"]["fortune"].update(wall_style="drape", floor="carpet",
                                  floor_color=(50, 26, 50))
CASE_5["rooms"]["caravans"].update(wall_style="night", floor="grass",
                                   floor_color=(26, 36, 26))

# ==========================================================================
# Case files - the background story shown before every case (press F in game)
#   item_label / item / art / about - what was stolen (art = picture to draw)
#   client    - who asked the detective for help
#   timeline  - what we know about the evening
#   bios      - one line about every suspect
#   epilogue  - what happened after the case was solved
# ==========================================================================

CASE_1["story"] = {
    "item_label": "THE STOLEN ITEM", "item": "The Moonlit Night", "art": "painting",
    "about": "Painted in 1889 by Elias Varn, Greyhaven's most famous painter. It shows "
             "the harbour under a full moon. Varn finished it the night before he "
             "vanished at sea - it is his very last work. Every school child in "
             "Greyhaven has seen it. Value: about 2 million.",
    "client": "Greyhaven City Museum. Director Helga Weber called the police at 22:30.",
    "timeline": [("21:00", "Leon arrives to see the painting."),
                 ("21:30", "Leon leaves. Ole locks the front door."),
                 ("22:05", "Ole goes up to the roof after a phone call."),
                 ("22:10", "The security camera switches off."),
                 ("22:20", "The camera switches back on."),
                 ("22:25", "Ole finds the empty frame.")],
    "bios": {"karl": "Has cleaned the museum for 25 years. Knows every corner.",
             "weber": "Director for 6 years. Always elegant, always busy.",
             "leon": "A young painter. Can't stand the painter of the Moonlit Night.",
             "ole": "Night guard. Friendly, a bit nervous."},
    "epilogue": "The Moonlit Night was back on the wall the next morning. Ole got a pay "
                "rise - and Karl finally got a new mop.",
}

CASE_2["story"] = {
    "item_label": "THE STOLEN ITEM", "item": "The Ice Star", "art": "necklace",
    "about": "A necklace with 99 small diamonds and one big star-shaped diamond in the "
             "middle. It once belonged to a Russian princess, then to the Countess's "
             "grandmother. The Countess wears it only once a year - at her winter party "
             "in Hotel Aurora. 'Priceless', says the Countess. About 3 million, says "
             "everyone else.",
    "client": "Countess Valentina di Rocca, 78. She has spent every winter at the Aurora "
              "for 50 years.",
    "timeline": [("18:00", "Mia, the pianist, arrives at the hotel - very early."),
                 ("22:00", "The Countess's winter party begins."),
                 ("22:30", "The Ice Star is placed in a glass case for the guests."),
                 ("23:00", "Blackout! The whole hotel goes dark."),
                 ("23:05", "The lights come back. The glass case is empty.")],
    "bios": {"countess": "Rich, generous and a little dramatic.",
             "finch": "Runs the hotel. Worried about its good name.",
             "bruno": "The hotel chef. Loud, proud, flour everywhere.",
             "mia": "A young pianist. Plays every night in the ballroom."},
    "epilogue": "The Countess got her Ice Star back - and finally insured it. Bruno baked "
                "a new three-layer cake to celebrate.",
}

CASE_3["story"] = {
    "item_label": "THE STOLEN ITEM", "item": "The Ravenwood Formula", "art": "formula",
    "about": "Twelve pages of notes for a new battery - ten times stronger than any "
             "battery today. Professor Ravenwood worked on it for eleven years. With it, "
             "an electric car could drive across the whole country without stopping. "
             "Companies would pay millions for it.",
    "client": "Professor Ada Ravenwood, inventor. Brilliant, forgetful - and very angry "
              "right now.",
    "timeline": [("20:00", "Dinner begins. A thunderstorm starts outside."),
                 ("20:15", "Lily photographs the locked lab door."),
                 ("20:30", "Some guests leave the table for a short time."),
                 ("20:45", "The butler clears the table."),
                 ("21:00", "The professor goes to her lab. The safe is open - the "
                           "formula is gone.")],
    "bios": {"nora": "The professor's assistant for 3 years.",
             "felix": "The professor's nephew. Mostly interested in cake.",
             "hargreaves": "Butler for 30 years. Notices everything.",
             "lily": "Journalist. Here for the story of the year.",
             "victor": "Business partner. Owns half of the professor's company."},
    "epilogue": "The formula is safe again. The professor gave Nora a raise and a new "
                "hairpin. SolarCorp is now under investigation.",
}

CASE_4["story"] = {
    "item_label": "THE STOLEN ITEM", "item": "The Emperor's Egg", "art": "egg",
    "about": "A golden egg the size of an apple, covered in 300 rubies and emeralds. "
             "It was made in 1896 as an Easter present for an empress. When you open "
             "it, a tiny golden train rolls out. Now it travels to an exhibition in "
             "Venice - by train, of course. Value: about 5 million.",
    "client": "The Vienna Museum, which lent the egg to Venice. Its guard, Mr. Brandt, "
              "was supposed to protect it.",
    "timeline": [("19:00", "The Snowbound Express leaves Vienna."),
                 ("21:00", "Dinner in the dining car."),
                 ("22:30", "Snowstorm! The train stops high in the mountains."),
                 ("23:30", "The guard gets a hot chocolate."),
                 ("00:00", "Pavel finds the guard asleep and the cage empty.")],
    "bios": {"pavel": "Conductor for 20 years. Carries the only luggage car key.",
             "hassan": "A doctor on her way to a conference in Venice.",
             "teo": "Young waiter. His first winter on the Express.",
             "baron": "Rich art collector. Wanted to buy the egg.",
             "odile": "Famous opera singer. Travels with eleven suitcases."},
    "epilogue": "The snowplough arrived at dawn. The egg reached Venice just in time, "
                "and Teo got a medal for his honest answers.",
}

CASE_5["story"] = {
    "item_label": "WHAT WAS SABOTAGED", "item": "Stella's Golden Trapeze", "art": "trapeze",
    "about": "Stella's act is the highlight of Circus Lumiere: a triple somersault "
             "twelve metres above the ring. Tonight the trapeze rope snapped in the "
             "middle of her jump. Only the safety net saved her. Without Stella, the "
             "circus would have to close for good.",
    "client": "Stella Moreau, star acrobat. Unhurt but shaken - and determined to find "
              "out who did it.",
    "timeline": [("10:00", "Igor checks all ropes. Everything is fine."),
                 ("17:00", "The ring is empty while the artists get ready."),
                 ("19:30", "The show begins. Mr. Grey takes seat A1."),
                 ("21:40", "The rope snaps during Stella's jump.")],
    "bios": {"krone": "Owner and ringmaster. Loves his circus.",
             "pip": "The circus clown. Makes the children laugh.",
             "lia": "Acrobat. Always second behind Stella.",
             "zora": "Fortune teller. Says she can see the future.",
             "igor": "Strongman. Checks every rope and net.",
             "grey": "Owner of the rival Circus Noir. Visiting tonight."},
    "epilogue": "Circus Noir was closed down. In the next show Stella flew higher than "
                "ever, and the audience cheered louder than ever.",
}

CASES = [CASE_1, CASE_2, CASE_3, CASE_4, CASE_5]
