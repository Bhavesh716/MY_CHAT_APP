import firebase_admin
from firebase_admin import credentials, db
import time
import threading
import os
import msvcrt
import sys
import signal

# Firebase setup
cred = credentials.Certificate("fb-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://py-chatting-app-default-rtdb.firebaseio.com/'
})

chat_ref = db.reference('chat')
last_seen = set()

def is_palindrome(s):
    s = ''.join(c.lower() for c in s if c.isalnum())
    return s == s[::-1]

# Clean exit function
def exit_chat(username):
    timestamp = str(time.time()).replace('.', '_')
    chat_ref.child(timestamp).set(f"{username}:sos...")
    time.sleep(0.5)
    chat_ref.set({})
    os.system('cls')
    sys.exit()

# Listener
def listen(username):
    global last_seen
    while True:
        messages = chat_ref.get()
        if messages:
            for key in sorted(messages.keys()):
                if key not in last_seen:
                    sender, text = messages[key].split(":", 1)
                    if sender != username:
                        print(f"\n: {text}", flush=True)
                    last_seen.add(key)
        time.sleep(1)

# Signal handler (CTRL+C, CTRL+Z)
def signal_handler(sig, frame):
    exit_chat(username)

signal.signal(signal.SIGINT, signal_handler)  # CTRL+C
#signal.signal(signal.SIGTSTP, signal_handler)  # CTRL+Z (on Unix; might not work on Windows)

# Get user
code = input("Enter a string to be checked: ").strip()

if code == "007":
    username = "ARUU"
elif code == "016":
    username = "BHAVI"
else:
    print("Palindrome ✅" if is_palindrome(code) else "Not a palindrome ❌")
    exit()

threading.Thread(target=listen, args=(username,), daemon=True).start()
print("")

# Chat loop
while True:
    msg = ''
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\x18':  # CTRL+X
                exit_chat(username)
            elif key == b'\r':  # ENTER
                print()
                break
            elif key == b'\x08':  # Backspace
                if msg:
                    msg = msg[:-1]
                    print('\b \b', end='', flush=True)
            else:
                try:
                    decoded = key.decode(errors='ignore')
                    msg += decoded
                    print(decoded, end='', flush=True)
                except:
                    pass

    stripped_msg = msg.strip().lower()
    if stripped_msg in ['end', 'exit']:
        exit_chat(username)
    elif stripped_msg:
        timestamp = str(time.time()).replace('.', '_')
        chat_ref.child(timestamp).set(f"{username}:{msg}")
