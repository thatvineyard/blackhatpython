
import queue
import threading
import time
import requests


# cd DVWA
# docker-compose up

agent = "Mozilla/5.0"
extensions = [".php", ".bak", ".orig", ".inc"]
target = "http://localhost:4280"
wordlist = "5-all-words.txt"
threads = 100

kill_threads = False;

last_word = None

def extend_words(wordlist, word):
  if "." in word:
    wordlist.put(f"/{word}")
  else:
    wordlist.put(f"/{word}/")
    
  for extension in extensions:
    wordlist.put(f"/{word}{extension}")

def get_words(resume=None):
  with open(wordlist) as file:
    raw_words = file.read()
    
  found_resume = False
  words = queue.Queue()
  
  for word in raw_words.split():
    if resume is not None:
      if found_resume:
        extend_words(words, word)
      elif word == resume:
        found_resume = True
        print(f"Resuming from {word}")
    else:
      # print(word)
      extend_words(words, word)
  return words

def dir_bruter(words: queue.Queue):
  headers = {'User-Agent': agent}
  while not words.empty() and not kill_threads:
    word = words.get()
    url = f"{target}{word}"
    try:
      r = requests.get(url, headers=headers)
    except requests.exceptions.ConnectionError:
      print("x", end="", flush=True)
      continue

    if r.status_code == 200:
      print(f"\nSuccess ({r.status_code}: {url})")
    elif r.status_code == 404:
      print(".", end="", flush=True)
    else:
      print(f"\n Nok ({r.status_code}: {url})")
      
    global last_word
    last_word = word
      

if __name__ == "__main__":
  words = get_words(resume="De.php")
  input("Press return")
  
  threadlist = []
  for _ in range(threads):
    t = threading.Thread(target=dir_bruter, args=(words,))
    t.daemon = True
    t.start()
    threadlist.append(t)
  
  try:  
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    kill_threads = True
    for thread in threadlist:
      thread.join(0.1)
    if last_word:
      print(f"last word: {last_word}")  

  
  