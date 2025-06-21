import firebase_admin
from firebase_admin import credentials, db
import time
import threading
import curses
import sys
import signal
import os

# Firebase setup
cred = credentials.Certificate("fb-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://py-chatting-app-default-rtdb.firebaseio.com/'
})

chat_ref = db.reference('chat')
shown_keys = set()
username = ""
chat_lines = []

# Exit handler
def exit_chat():
    try:
        curses.endwin()  # Step 1: First end curses properly
    except:
        pass
    sys.exit()


def signal_handler(sig, frame):
    exit_chat()

signal.signal(signal.SIGINT, signal_handler)

# Listen to chat updates
def listen_chat(chat_win, height):
    global shown_keys, chat_lines
    while True:
        messages = chat_ref.get()
        if messages:
            chat_lines = []
            for key in sorted(messages.keys()):
                sender, text = messages[key].split(":", 1)
                alias = "a" if sender == "ARUU" else "b"
                chat_lines.append(f"{alias}: {text}")
                shown_keys.add(key)

            chat_win.clear()
            start = max(0, len(chat_lines) - height)
            for i, line in enumerate(chat_lines[start:]):
                chat_win.addstr(i, 0, line)
            chat_win.refresh()
        time.sleep(1)

# Palindrome checker
def is_palindrome(s):
    s = ''.join(c.lower() for c in s if c.isalnum())
    return s == s[::-1]

# Curses UI
def main(stdscr):
    global username
    curses.curs_set(1)
    stdscr.clear()

    height, width = stdscr.getmaxyx()
    chat_height = height - 5
    chat_win = curses.newwin(chat_height, width, 0, 0)
    divider_win = curses.newwin(1, width, chat_height + 1, 0)
    input_win = curses.newwin(1, width, chat_height + 3, 0)

    # Load old messages
    messages = chat_ref.get()
    chat_lines = []
    if messages:
        for key in sorted(messages.keys()):
            sender, text = messages[key].split(":", 1)
            alias = "a" if sender == "ARUU" else "b"
            chat_lines.append(f"{alias}: {text}")
            shown_keys.add(key)
        start = max(0, len(chat_lines) - chat_height)
        for i, line in enumerate(chat_lines[start:]):
            chat_win.addstr(i, 0, line)
        chat_win.refresh()

    divider_win.addstr(0, 0, "-" * (width - 1))
    divider_win.refresh()

    threading.Thread(target=listen_chat, args=(chat_win, chat_height), daemon=True).start()

    while True:
        input_win.clear()
        prompt = "a: " if username == "ARUU" else "b: "
        input_win.addstr(0, 0, prompt)
        input_win.refresh()
        curses.echo()
        msg = input_win.getstr(0, len(prompt)).decode()
        curses.noecho()

        stripped_msg = msg.strip().lower()
        if stripped_msg in ['end', 'exit']:
            exit_chat()
        elif stripped_msg:
            timestamp = str(time.time()).replace('.', '_')
            chat_ref.child(timestamp).set(f"{username}:{msg}")

# Entry point
if __name__ == "__main__":
    try:
        user_input = input("Enter a string to be checked: ").strip()
        if user_input == "007":
            username = "ARUU"
            curses.wrapper(main)
        elif user_input == "016":
            username = "BHAVI"
            curses.wrapper(main)
        else:
            print("Palindrome ✅" if is_palindrome(user_input) else "Not a palindrome ❌")
    except KeyboardInterrupt:
        exit_chat()


        '''not working below part still kept for futurre reference
        os.system('cls' if os.name == 'nt' else 'clear')  # Step 2: Now clear CMD screen
        try:
            timestamp = str(time.time()).replace('.', '_')
            chat_ref.child(timestamp).set(f"{username}:sos...")  # Step 3: Add SOS msg
            time.sleep(0.5)
            chat_ref.set({})  # Step 4: Clear database
        except:
            pass'''
