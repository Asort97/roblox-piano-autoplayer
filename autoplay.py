import argparse
import re
import sys
import time
from typing import Iterable

from pynput.keyboard import Controller, Key, KeyCode, Listener

TOKEN_RE = re.compile(r"\[[^\]]+\]|[^\s]+")


def parse_tokens(sheet_text: str) -> Iterable[str]:
    return TOKEN_RE.findall(sheet_text)


def press_char(ctrl: Controller, ch: str) -> None:
    if not ch:
        return
    ctrl.press(KeyCode.from_char(ch))
    ctrl.release(KeyCode.from_char(ch))


def play_chord(ctrl: Controller, chars: str) -> None:
    keys = [KeyCode.from_char(ch) for ch in chars if ch.strip()]
    for key in keys:
        ctrl.press(key)
    for key in reversed(keys):
        ctrl.release(key)


def play_tokens(
    ctrl: Controller,
    tokens: Iterable[str],
    delay: float,
    intra_delay: float,
    stop_flag,
) -> None:
    for token in tokens:
        if stop_flag[0]:
            return
        if token.startswith("[") and token.endswith("]"):
            play_chord(ctrl, token[1:-1])
        else:
            if len(token) == 1:
                press_char(ctrl, token)
            else:
                for ch in token:
                    if stop_flag[0]:
                        return
                    press_char(ctrl, ch)
                    if intra_delay > 0:
                        time.sleep(intra_delay)
        if delay > 0:
            time.sleep(delay)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Play Roblox piano sheets by emulating key presses."
    )
    parser.add_argument(
        "sheet",
        nargs="?",
        default="song.txt",
        help="Path to a text file with piano sheets (default: song.txt)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Delay between tokens in seconds (default: 0.2)",
    )
    parser.add_argument(
        "--intra-delay",
        type=float,
        default=0.0,
        help="Delay between characters inside a non-bracket token (default: 0)",
    )
    parser.add_argument(
        "--countdown",
        type=int,
        default=5,
        help="Seconds to wait before playback starts (default: 5)",
    )
    args = parser.parse_args()

    try:
        sheet_text = open(args.sheet, "r", encoding="utf-8").read()
    except OSError as exc:
        print(f"Failed to read sheet file: {exc}", file=sys.stderr)
        return 1

    tokens = list(parse_tokens(sheet_text))
    if not tokens:
        print("Sheet is empty or no tokens were found.", file=sys.stderr)
        return 1

    print("Focus the Roblox window now. Press Esc to stop.")
    if args.countdown > 0:
        for i in range(args.countdown, 0, -1):
            print(f"Starting in {i}...")
            time.sleep(1)

    ctrl = Controller()
    stop_flag = [False]

    def on_press(key):
        if key == Key.esc:
            stop_flag[0] = True
            return False
        return True

    with Listener(on_press=on_press) as listener:
        play_tokens(ctrl, tokens, args.delay, args.intra_delay, stop_flag)
        listener.stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())