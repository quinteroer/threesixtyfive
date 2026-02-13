#!/usr/bin/env python3
"""
Song Swap Script
Swaps two songs in a loveData .js or .json file by day number.
Supports JS files with a variable declaration wrapper like:
    const loveData = { ... };
"""

import json
import sys
import os


def load_data(file_path):
    """
    Load data from a .json or .js file.
    For .js files, strips the JS variable declaration wrapper (e.g. 'const loveData = ...;')
    Returns (data_dict, js_prefix, js_suffix) — prefix/suffix are None for plain JSON.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    if file_path.lower().endswith(".js"):
        # Extract everything between the first '{' and last '}'
        start = raw.index("{")
        end   = raw.rindex("}") + 1
        prefix   = raw[:start]   # e.g. "const loveData = "
        suffix   = raw[end:]     # e.g. ";\n"
        json_str = raw[start:end]
        return json.loads(json_str), prefix, suffix
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f), None, None


def save_data(file_path, data, js_prefix=None, js_suffix=None):
    """
    Save data back to file, restoring the JS wrapper if present.
    """
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    with open(file_path, "w", encoding="utf-8") as f:
        if js_prefix is not None:
            f.write(js_prefix + json_str + (js_suffix or ""))
        else:
            f.write(json_str)


def find_song(data, song_name):
    """
    Search for a song by name (case-insensitive partial match).
    Returns (day_key, song_entry) or (None, None) if not found.
    Prompts user to choose if multiple matches exist.
    """
    song_name_lower = song_name.strip().lower()
    matches = []

    for day_key, entry in data.items():
        original = entry.get("metadata", {}).get("original_name", "")
        matched  = entry.get("metadata", {}).get("matched_name", "")
        if song_name_lower in original.lower() or song_name_lower in matched.lower():
            matches.append((day_key, entry))

    if not matches:
        return None, None

    if len(matches) == 1:
        return matches[0]

    # Multiple matches — ask user to pick
    print(f"\n  Multiple matches found for '{song_name}':")
    for i, (day_key, entry) in enumerate(matches, 1):
        day_num = int(day_key.replace("day", ""))
        artist  = entry.get("metadata", {}).get("original_artist", "Unknown")
        name    = entry.get("metadata", {}).get("original_name", "Unknown")
        print(f"    [{i}] Day {day_num}: {name} — {artist}")

    while True:
        choice = input("  Enter the number of the song you want: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(matches):
            return matches[int(choice) - 1]
        print("  Invalid choice. Please try again.")


def swap_songs(data, day_key_a, day_key_b):
    """
    Swap the song content between two day entries.
    The day 'title' (Day N label) and 'message' fields stay fixed to their slot.
    Only song data travels: src, song_embed, PID, metadata.
    """
    song_fields = ["src", "song_embed", "PID", "metadata"]

    song_data_a = {field: data[day_key_a].get(field) for field in song_fields}
    song_data_b = {field: data[day_key_b].get(field) for field in song_fields}

    for field in song_fields:
        data[day_key_a][field] = song_data_b[field]
        data[day_key_b][field] = song_data_a[field]


def main():
    # ── Pre-loaded file path ──────────────────────────────────────────────────
    # Edit this to your file path so you're not prompted each run.
    PRELOADED_FILE_PATH = "C:/VCU/zzz/isabella_shortcuts/valentines_calender/threesixtyfive/staging/assets/calendar_data.js"
    # ─────────────────────────────────────────────────────────────────────────

    print("=" * 60)
    print("         🎵  Song Swap Tool  🎵")
    print("=" * 60)

    # Resolve file path
    file_path = PRELOADED_FILE_PATH.strip()
    if not file_path:
        file_path = input("\nEnter path to JS/JSON file: ").strip()
    else:
        print(f"\nUsing preloaded file: {file_path}")

    if not os.path.isfile(file_path):
        print(f"\n❌  File not found: '{file_path}'")
        sys.exit(1)

    data, js_prefix, js_suffix = load_data(file_path)
    total_days = len(data)
    print(f"✅  Loaded {total_days} entries.\n")

    # ── Get target day number ─────────────────────────────────────────────────
    while True:
        day_input = input("Enter the DAY NUMBER you want to place the song in: ").strip()
        if day_input.isdigit() and 1 <= int(day_input) <= total_days:
            target_day = int(day_input)
            break
        print(f"  Please enter a number between 1 and {total_days}.")

    target_key = f"day{target_day}"
    if target_key not in data:
        print(f"\n❌  Day {target_day} not found in data.")
        sys.exit(1)

    current_entry       = data[target_key]
    current_song_name   = current_entry.get("metadata", {}).get("original_name", "Unknown")
    current_artist      = current_entry.get("metadata", {}).get("original_artist", "Unknown")
    print(f"\n  Day {target_day} currently holds: '{current_song_name}' by {current_artist}")

    # ── Get song to place there ───────────────────────────────────────────────
    print()
    song_query = input("Enter the SONG NAME you want to move to that day: ").strip()
    if not song_query:
        print("❌  No song name entered.")
        sys.exit(1)

    source_key, source_entry = find_song(data, song_query)
    if source_key is None:
        print(f"\n❌  Could not find a song matching '{song_query}'.")
        sys.exit(1)

    source_day    = int(source_key.replace("day", ""))
    source_name   = source_entry.get("metadata", {}).get("original_name", "Unknown")
    source_artist = source_entry.get("metadata", {}).get("original_artist", "Unknown")

    if source_key == target_key:
        print(f"\n⚠️   '{source_name}' is already on Day {target_day}. No swap needed.")
        sys.exit(0)

    # ── Confirm swap ──────────────────────────────────────────────────────────
    print(f"\n  Swap summary:")
    print(f"    Day {source_day}: '{source_name}' by {source_artist}  →  Day {target_day}")
    print(f"    Day {target_day}: '{current_song_name}' by {current_artist}  →  Day {source_day}")
    confirm = input("\n  Proceed? (y/n): ").strip().lower()

    if confirm != "y":
        print("  Swap cancelled.")
        sys.exit(0)

    # ── Perform swap & save ───────────────────────────────────────────────────
    swap_songs(data, source_key, target_key)
    save_data(file_path, data, js_prefix, js_suffix)

    print(f"\n✅  Done! Swapped:")
    print(f"    '{source_name}'  →  Day {target_day}")
    print(f"    '{current_song_name}'  →  Day {source_day}")
    print(f"\n  Saved to: {file_path}")


if __name__ == "__main__":
    main()