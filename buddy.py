#!/usr/bin/env python3
"""
🐣 Claude Buddy — Open-source CLI companion pet
Inspired by Anthropic's hidden BUDDY feature in Claude Code.
"""
import json
import os
import sys
import time
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# ═══════════════════════════════════════════
# Constants & Species Data
# ═══════════════════════════════════════════

SAVE_FILE = Path.home() / ".claude" / "buddy.json"

SPECIES = {
    # Common (60%)
    "cat":       {"name": "Cat",       "emoji": "🐱", "rarity": "common",    "base_hp": 20, "base_atk": 5,  "base_def": 3,  "trait": "curious"},
    "dog":       {"name": "Dog",       "emoji": "🐕", "rarity": "common",    "base_hp": 25, "base_atk": 4,  "base_def": 4,  "trait": "loyal"},
    "rabbit":    {"name": "Rabbit",    "emoji": "🐰", "rarity": "common",    "base_hp": 15, "base_atk": 3,  "base_def": 2,  "trait": "quick"},
    "hamster":   {"name": "Hamster",   "emoji": "🐹", "rarity": "common",    "base_hp": 12, "base_atk": 2,  "base_def": 2,  "trait": "industrious"},
    "bird":      {"name": "Bird",      "emoji": "🐦", "rarity": "common",    "base_hp": 10, "base_atk": 3,  "base_def": 1,  "trait": "cheerful"},
    "turtle":    {"name": "Turtle",    "emoji": "🐢", "rarity": "common",    "base_hp": 30, "base_atk": 2,  "base_def": 8,  "trait": "patient"},
    # Uncommon (25%)
    "fox":       {"name": "Fox",       "emoji": "🦊", "rarity": "uncommon",  "base_hp": 18, "base_atk": 6,  "base_def": 3,  "trait": "clever"},
    "panda":     {"name": "Panda",     "emoji": "🐼", "rarity": "uncommon",  "base_hp": 28, "base_atk": 5,  "base_def": 6,  "trait": "chill"},
    "owl":       {"name": "Owl",       "emoji": "🦉", "rarity": "uncommon",  "base_hp": 16, "base_atk": 7,  "base_def": 3,  "trait": "wise"},
    "octopus":   {"name": "Octopus",   "emoji": "🐙", "rarity": "uncommon",  "base_hp": 20, "base_atk": 8,  "base_def": 2,  "trait": "creative"},
    "chameleon": {"name": "Chameleon", "emoji": "🦎", "rarity": "uncommon",  "base_hp": 14, "base_atk": 4,  "base_def": 5,  "trait": "adaptive"},
    # Rare (12%)
    "dragon":    {"name": "Dragon",    "emoji": "🐉", "rarity": "rare",      "base_hp": 35, "base_atk": 10, "base_def": 7,  "trait": "fierce"},
    "unicorn":   {"name": "Unicorn",   "emoji": "🦄", "rarity": "rare",      "base_hp": 22, "base_atk": 6,  "base_def": 5,  "trait": "magical"},
    "wolf":      {"name": "Wolf",      "emoji": "🐺", "rarity": "rare",      "base_hp": 25, "base_atk": 9,  "base_def": 5,  "trait": "strategic"},
    "phoenix":   {"name": "Phoenix",   "emoji": "🦅", "rarity": "rare",      "base_hp": 18, "base_atk": 11, "base_def": 3,  "trait": "resilient"},
    # Legendary (3%)
    "cosmic_cat":    {"name": "Cosmic Cat",    "emoji": "🌟", "rarity": "legendary", "base_hp": 40, "base_atk": 12, "base_def": 10, "trait": "transcendent"},
    "crystal_fox":   {"name": "Crystal Fox",   "emoji": "🔮", "rarity": "legendary", "base_hp": 30, "base_atk": 14, "base_def": 8,  "trait": "prophetic"},
    "thunder_bird":  {"name": "Thunder Bird",  "emoji": "⚡", "rarity": "legendary", "base_hp": 25, "base_atk": 16, "base_def": 6,  "trait": "electric"},
}

RARITY_WEIGHTS = {"common": 60, "uncommon": 25, "rare": 12, "legendary": 3}
RARITY_COLORS = {"common": "\033[37m", "uncommon": "\033[32m", "rare": "\033[35m", "legendary": "\033[33m"}

MOODS = {
    "ecstatic":  {"emoji": "😄", "threshold": 90},
    "happy":     {"emoji": "😊", "threshold": 70},
    "content":   {"emoji": "😐", "threshold": 50},
    "sad":       {"emoji": "😢", "threshold": 30},
    "miserable": {"emoji": "😭", "threshold": 0},
}

EVOLUTIONS = {
    5:  "Baby",
    15: "Junior",
    30: "Adult",
    50: "Elder",
    80: "Legendary",
}

SOUL_DESCRIPTIONS = [
    "Born from a stray thought during a late-night debugging session.",
    "Emerged when you fixed a particularly nasty race condition.",
    "Hatched from the warmth of a thousand successful test runs.",
    "Appeared during a moment of perfect flow state.",
    "Created from the collective satisfaction of clean git commits.",
    "Manifested when you finally understood that recursive algorithm.",
    "Born from the joy of a green CI pipeline after weeks of red.",
    "Emerged from the space between keystrokes during inspired coding.",
    "Hatched from the energy of your first open-source contribution.",
    "Appeared when you wrote code so clean it needed no comments.",
]

ACHIEVEMENTS = {
    "first_hatch":   {"name": "First Steps",      "desc": "Hatch your first buddy",    "emoji": "🥚"},
    "level_10":      {"name": "Growing Up",        "desc": "Reach level 10",            "emoji": "📈"},
    "level_50":      {"name": "Veteran",           "desc": "Reach level 50",            "emoji": "🏅"},
    "feed_100":      {"name": "Master Chef",       "desc": "Feed 100 times",            "emoji": "🍳"},
    "play_50":       {"name": "Fun Times",         "desc": "Play 50 times",             "emoji": "🎮"},
    "rare_hatch":    {"name": "Lucky Find",        "desc": "Hatch a rare+ species",     "emoji": "🍀"},
    "shiny":         {"name": "Shiny Hunter",      "desc": "Get a shiny variant",       "emoji": "✨"},
    "legendary":     {"name": "Legend",             "desc": "Hatch a legendary species", "emoji": "👑"},
    "week_streak":   {"name": "Dedicated",         "desc": "7-day interaction streak",  "emoji": "🔥"},
    "max_happy":     {"name": "Best Friend",       "desc": "Reach 100% happiness",      "emoji": "💕"},
}

# ═══════════════════════════════════════════
# ANSI Color Helpers
# ═══════════════════════════════════════════

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
GRAY = "\033[90m"


def colored(text, color):
    return f"{color}{text}{RESET}"


def bar(value, max_val, width=20, fill_color=GREEN):
    filled = int(width * value / max(1, max_val))
    empty = width - filled
    return f"{fill_color}{'█' * filled}{GRAY}{'░' * empty}{RESET} {value}/{max_val}"


# ═══════════════════════════════════════════
# Pet State Management
# ═══════════════════════════════════════════

def load_pet():
    if SAVE_FILE.exists():
        with open(SAVE_FILE) as f:
            return json.load(f)
    return None


def save_pet(pet):
    SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SAVE_FILE, 'w') as f:
        json.dump(pet, f, indent=2)


def create_pet(species_id):
    species = SPECIES[species_id]
    # Deterministic shiny based on hash of species + time
    seed = hashlib.md5(f"{species_id}{time.time()}".encode()).hexdigest()
    is_shiny = int(seed[:2], 16) == 0  # 1/256 chance

    # Generate unique soul
    soul = random.choice(SOUL_DESCRIPTIONS)

    pet = {
        "species": species_id,
        "name": species["name"],
        "nickname": None,
        "shiny": is_shiny,
        "level": 1,
        "xp": 0,
        "xp_next": 20,
        "hp": species["base_hp"],
        "max_hp": species["base_hp"],
        "atk": species["base_atk"],
        "defense": species["base_def"],
        "happiness": 70,
        "hunger": 50,
        "energy": 80,
        "soul": soul,
        "hatched_at": datetime.now().isoformat(),
        "last_interaction": datetime.now().isoformat(),
        "times_fed": 0,
        "times_played": 0,
        "times_trained": 0,
        "streak_days": 0,
        "last_streak_date": datetime.now().strftime("%Y-%m-%d"),
        "achievements": ["first_hatch"],
        "evolution_stage": "Baby",
    }

    if species["rarity"] in ("rare", "legendary"):
        pet["achievements"].append("rare_hatch")
    if species["rarity"] == "legendary":
        pet["achievements"].append("legendary")
    if is_shiny:
        pet["achievements"].append("shiny")

    return pet


def gacha_roll():
    """Weighted random species selection."""
    roll = random.randint(1, 100)
    if roll <= 3:
        tier = "legendary"
    elif roll <= 15:
        tier = "rare"
    elif roll <= 40:
        tier = "uncommon"
    else:
        tier = "common"

    candidates = [sid for sid, s in SPECIES.items() if s["rarity"] == tier]
    return random.choice(candidates)


def decay_stats(pet):
    """Apply time-based stat decay since last interaction."""
    last = datetime.fromisoformat(pet["last_interaction"])
    now = datetime.now()
    hours = (now - last).total_seconds() / 3600

    if hours > 0.5:
        pet["hunger"] = min(100, pet["hunger"] + int(hours * 3))
        pet["energy"] = max(0, pet["energy"] - int(hours * 2))
        pet["happiness"] = max(0, pet["happiness"] - int(hours * 1.5))

    # Streak tracking
    today = now.strftime("%Y-%m-%d")
    if pet["last_streak_date"] != today:
        last_date = datetime.strptime(pet["last_streak_date"], "%Y-%m-%d")
        if (now - last_date).days == 1:
            pet["streak_days"] += 1
        elif (now - last_date).days > 1:
            pet["streak_days"] = 0
        pet["last_streak_date"] = today

    if pet["streak_days"] >= 7 and "week_streak" not in pet["achievements"]:
        pet["achievements"].append("week_streak")

    pet["last_interaction"] = now.isoformat()
    return pet


def get_mood(pet):
    for mood, data in MOODS.items():
        if pet["happiness"] >= data["threshold"]:
            return mood, data["emoji"]
    return "miserable", "😭"


def get_evolution(level):
    stage = "Baby"
    for lvl, name in sorted(EVOLUTIONS.items()):
        if level >= lvl:
            stage = name
    return stage


def gain_xp(pet, amount):
    pet["xp"] += amount
    leveled = False
    while pet["xp"] >= pet["xp_next"]:
        pet["xp"] -= pet["xp_next"]
        pet["level"] += 1
        pet["xp_next"] = int(pet["xp_next"] * 1.3)
        species = SPECIES[pet["species"]]
        pet["max_hp"] = species["base_hp"] + pet["level"] * 2
        pet["hp"] = pet["max_hp"]
        pet["atk"] = species["base_atk"] + pet["level"]
        pet["defense"] = species["base_def"] + pet["level"] // 2
        pet["evolution_stage"] = get_evolution(pet["level"])
        leveled = True

    if pet["level"] >= 10 and "level_10" not in pet["achievements"]:
        pet["achievements"].append("level_10")
    if pet["level"] >= 50 and "level_50" not in pet["achievements"]:
        pet["achievements"].append("level_50")
    if pet["happiness"] >= 100 and "max_happy" not in pet["achievements"]:
        pet["achievements"].append("max_happy")

    return leveled


# ═══════════════════════════════════════════
# ASCII Art
# ═══════════════════════════════════════════

BUDDY_ART = {
    "cat":     ["  /\\_/\\  ", " ( o.o ) ", "  > ^ <  "],
    "dog":     ["  __    ", " /  \\__ ", "(  @  > "],
    "rabbit":  [" (\\(\\  ", " (-.-)  ", " o('')(')"],
    "hamster": [" (•ᴗ•) ", " /|  |\\ ", "  d  b  "],
    "bird":    ["  ._.  ", " (o o) ", " / V \\  "],
    "turtle":  ["  ____  ", " /(..)\\", "/_|__|_\\"],
    "fox":     [" /\\_/\\  ", "( ^.^ ) ", " > ~ <  "],
    "panda":   [" _(__)_ ", "(  oo  )", " \\ -- / "],
    "owl":     [" {o,o}  ", " |)__)  ", " -\"\"--  "],
    "octopus": ["  ___   ", " (o o)  ", " /|\\|\\  "],
    "chameleon":[" __/\\__ ", "(  oo  )", " ~~~~~~ "],
    "dragon":  [" /\\_/\\  ", "< @ @ > ", " \\=v=/ ~"],
    "unicorn": ["  /|    ", " (_)__  ", " / ^  > "],
    "wolf":    [" /\\_/\\  ", "( o.o ) ", " > w <  "],
    "phoenix": ["  ,/\\,  ", " // \\\\ ", "/(_)(_)\\"],
    "cosmic_cat":    ["  *\\_/*  ", " ( ✦.✦ ) ", "  > ☆ <  "],
    "crystal_fox":   [" /◇\\_/◇\\ ", "( ✦.✦ )  ", " > ~ < ◇ "],
    "thunder_bird":  ["  ⚡.⚡  ", " //⚡\\\\ ", "/( ⚡ )\\"],
}

EGG_FRAMES = [
    ["  ___  ", " /   \\ ", "|     |", " \\___/ "],
    ["  ___  ", " / * \\ ", "|  *  |", " \\___/ "],
    ["  _*_  ", " / * \\ ", "| * * |", " \\_*_/ "],
    ["  ***  ", " /* *\\ ", "|* * *|", " \\***/ "],
]


# ═══════════════════════════════════════════
# Commands
# ═══════════════════════════════════════════

def cmd_status(pet):
    """Show pet status."""
    species = SPECIES[pet["species"]]
    rarity_color = RARITY_COLORS[species["rarity"]]
    mood, mood_emoji = get_mood(pet)
    shiny_tag = colored(" ✨SHINY✨", YELLOW) if pet["shiny"] else ""

    display_name = pet["nickname"] or pet["name"]

    print()
    print(colored("╔══════════════════════════════════════╗", CYAN))
    print(colored(f"║  {species['emoji']}  {display_name}{shiny_tag}", CYAN))
    print(colored("╠══════════════════════════════════════╣", CYAN))

    # ASCII art
    art = BUDDY_ART.get(pet["species"], ["  ???  "])
    for line in art:
        print(colored(f"║    {line:<34}║", CYAN))

    print(colored("╠══════════════════════════════════════╣", CYAN))
    print(f"║  {colored('Species:', GRAY)} {rarity_color}{species['name']} ({species['rarity'].upper()}){RESET}")
    print(f"║  {colored('Level:', GRAY)}   {colored(str(pet['level']), BOLD+WHITE)} ({pet['evolution_stage']})")
    print(f"║  {colored('XP:', GRAY)}      {bar(pet['xp'], pet['xp_next'], 15, CYAN)}")
    print(f"║  {colored('Mood:', GRAY)}    {mood_emoji} {mood.title()}")
    print(f"║  {colored('Trait:', GRAY)}   {species['trait'].title()}")
    print(colored("║", CYAN))
    print(f"║  {colored('HP:', GRAY)}      {bar(pet['hp'], pet['max_hp'], 15, RED)}")
    print(f"║  {colored('Happy:', GRAY)}   {bar(pet['happiness'], 100, 15, YELLOW)}")
    print(f"║  {colored('Hunger:', GRAY)}  {bar(100-pet['hunger'], 100, 15, GREEN)}")
    print(f"║  {colored('Energy:', GRAY)}  {bar(pet['energy'], 100, 15, BLUE)}")
    print(colored("║", CYAN))
    print(f"║  {colored('ATK:', GRAY)} {pet['atk']}  {colored('DEF:', GRAY)} {pet['defense']}  {colored('Streak:', GRAY)} {pet['streak_days']}d")
    print(colored("║", CYAN))
    print(f"║  {colored('Soul:', DIM+WHITE)} {pet['soul'][:36]}")
    print(colored("╚══════════════════════════════════════╝", CYAN))
    print()


def cmd_hatch():
    """Hatch a new pet."""
    print()
    print(colored("  🥚 An egg appeared!", YELLOW + BOLD))
    print()

    # Hatch animation
    for frame in EGG_FRAMES:
        for line in frame:
            print(colored(f"    {line}", WHITE))
        time.sleep(0.5)
        # Clear (move up)
        print(f"\033[{len(frame)}A", end="")

    species_id = gacha_roll()
    species = SPECIES[species_id]
    pet = create_pet(species_id)
    save_pet(pet)

    rarity_color = RARITY_COLORS[species["rarity"]]

    print()
    print()
    print(colored("  ✨ The egg is hatching! ✨", YELLOW + BOLD))
    print()
    time.sleep(0.5)

    art = BUDDY_ART.get(species_id, ["  ???  "])
    for line in art:
        print(colored(f"    {line}", rarity_color + BOLD))

    print()
    print(f"  A {rarity_color}{BOLD}{species['name']}{RESET} appeared!")
    print(f"  Rarity: {rarity_color}{species['rarity'].upper()}{RESET}")
    if pet["shiny"]:
        print(colored("  ✨ IT'S SHINY! ✨ (1/256 chance!)", YELLOW + BOLD))
    print(f"  Trait: {colored(species['trait'].title(), CYAN)}")
    print(f"  Soul: {colored(pet['soul'], DIM + WHITE)}")
    print()

    return pet


def cmd_feed(pet):
    """Feed the pet."""
    if pet["hunger"] < 10:
        print(colored("  Your buddy isn't hungry right now! 😊", YELLOW))
        return

    pet["hunger"] = max(0, pet["hunger"] - 30)
    pet["happiness"] = min(100, pet["happiness"] + 5)
    pet["times_fed"] += 1

    if pet["times_fed"] >= 100 and "feed_100" not in pet["achievements"]:
        pet["achievements"].append("feed_100")
        print(colored("  🏆 Achievement unlocked: Master Chef!", YELLOW + BOLD))

    leveled = gain_xp(pet, 5)

    species = SPECIES[pet["species"]]
    print(f"\n  {species['emoji']} *munch munch* 🍎")
    print(f"  Hunger: {bar(100-pet['hunger'], 100, 15, GREEN)}")
    if leveled:
        print(colored(f"  🎉 Level up! Now level {pet['level']}!", YELLOW + BOLD))
    print()
    save_pet(pet)


def cmd_play(pet):
    """Play with the pet."""
    if pet["energy"] < 10:
        print(colored("  Your buddy is too tired to play! 😴", YELLOW))
        return

    pet["energy"] = max(0, pet["energy"] - 15)
    pet["happiness"] = min(100, pet["happiness"] + 15)
    pet["hunger"] = min(100, pet["hunger"] + 5)
    pet["times_played"] += 1

    if pet["times_played"] >= 50 and "play_50" not in pet["achievements"]:
        pet["achievements"].append("play_50")
        print(colored("  🏆 Achievement unlocked: Fun Times!", YELLOW + BOLD))

    leveled = gain_xp(pet, 10)

    species = SPECIES[pet["species"]]
    games = ["fetch", "tag", "hide and seek", "puzzle", "dance"]
    game = random.choice(games)
    print(f"\n  {species['emoji']} You played {game}! 🎮")
    print(f"  Happiness: {bar(pet['happiness'], 100, 15, YELLOW)}")
    if leveled:
        print(colored(f"  🎉 Level up! Now level {pet['level']}!", YELLOW + BOLD))
    print()
    save_pet(pet)


def cmd_train(pet):
    """Train the pet for XP."""
    if pet["energy"] < 20:
        print(colored("  Your buddy needs rest first! 😴", YELLOW))
        return

    pet["energy"] = max(0, pet["energy"] - 25)
    pet["hunger"] = min(100, pet["hunger"] + 10)
    pet["times_trained"] += 1

    xp = random.randint(15, 30)
    leveled = gain_xp(pet, xp)

    species = SPECIES[pet["species"]]
    exercises = ["coding kata", "algorithm practice", "type racing", "debugging drill", "refactoring exercise"]
    exercise = random.choice(exercises)
    print(f"\n  {species['emoji']} Trained with {exercise}! 💪")
    print(f"  +{xp} XP!")
    if leveled:
        print(colored(f"  🎉 Level up! Now level {pet['level']}! ({pet['evolution_stage']})", YELLOW + BOLD))
    print()
    save_pet(pet)


def cmd_achievements(pet):
    """Show achievements."""
    print()
    print(colored("  🏆 Achievements", YELLOW + BOLD))
    print(colored("  " + "═" * 35, YELLOW))
    for aid, adata in ACHIEVEMENTS.items():
        unlocked = aid in pet["achievements"]
        if unlocked:
            print(f"  {adata['emoji']} {colored(adata['name'], GREEN + BOLD)} — {adata['desc']}")
        else:
            print(f"  {colored('🔒', GRAY)} {colored(adata['name'], GRAY)} — {colored(adata['desc'], GRAY)}")
    unlocked_count = len(pet["achievements"])
    total_count = len(ACHIEVEMENTS)
    print(f"\n  {colored(str(unlocked_count) + '/' + str(total_count), CYAN)} unlocked")
    print()


def cmd_help():
    """Show help."""
    print()
    print(colored("  🐣 Claude Buddy — Commands", CYAN + BOLD))
    print(colored("  " + "═" * 35, CYAN))
    cmds = [
        ("buddy",              "Check on your buddy"),
        ("buddy hatch",        "Hatch a new egg"),
        ("buddy feed",         "Feed your buddy"),
        ("buddy play",         "Play with your buddy"),
        ("buddy train",        "Train for XP"),
        ("buddy stats",        "Detailed stats"),
        ("buddy achievements", "View achievements"),
        ("buddy rename <name>","Rename your buddy"),
        ("buddy release",      "Release your buddy 😢"),
        ("buddy help",         "Show this help"),
    ]
    for cmd, desc in cmds:
        print(f"  {colored(cmd, WHITE + BOLD):<30} {colored(desc, GRAY)}")
    print()


def main():
    args = sys.argv[1:]
    command = args[0] if args else "status"

    if command == "help":
        cmd_help()
        return

    if command == "hatch":
        existing = load_pet()
        if existing:
            print(colored("\n  You already have a buddy! Use 'buddy release' first.\n", RED))
            return
        cmd_hatch()
        return

    # All other commands need an existing pet
    pet = load_pet()
    if not pet:
        print(colored("\n  No buddy found! Use 'buddy hatch' to get one.\n", YELLOW))
        return

    pet = decay_stats(pet)

    if command in ("status", "stats"):
        cmd_status(pet)
    elif command == "feed":
        cmd_feed(pet)
    elif command == "play":
        cmd_play(pet)
    elif command == "train":
        cmd_train(pet)
    elif command == "achievements":
        cmd_achievements(pet)
    elif command == "rename" and len(args) > 1:
        pet["nickname"] = " ".join(args[1:])
        save_pet(pet)
        print(colored(f"\n  Renamed to {pet['nickname']}! 🏷️\n", GREEN))
    elif command == "release":
        species = SPECIES[pet["species"]]
        print(colored(f"\n  {species['emoji']} {pet['nickname'] or pet['name']} waves goodbye... 👋", YELLOW))
        print(colored(f"  Level {pet['level']} | {pet['evolution_stage']} | {pet['streak_days']}d streak\n", GRAY))
        SAVE_FILE.unlink(missing_ok=True)
    else:
        print(colored(f"\n  Unknown command: {command}", RED))
        cmd_help()

    save_pet(pet)


if __name__ == "__main__":
    main()
