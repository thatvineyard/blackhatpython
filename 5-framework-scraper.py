import os
import queue
import shutil
import tempfile
import requests
import zipfile

# cd dvwp
# docker-compose up --build
# docker-compose run --rm wp-cli install-wp
# python3 .\5-framework-scraper.py

threads = 0
target = "http://127.0.0.1:31337/"
download_link = "https://wordpress.org/latest.zip"
zip = "wordpress-6.6.2.zip"
temp_folder = "temp"
filters = [".jpg", ".gif", "png", ".css"]

def unzip_to_temp_folder(zip_file_path):
      temp_dir = tempfile.mkdtemp(dir=os.curdir)    
      with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # Extract all contents into the temporary directory
        zip_ref.extractall(temp_dir)    
        return temp_dir

def generate_paths(directory):
    web_paths = queue.Queue()
    count = 0

    for r, d, f in os.walk(directory):
      dir = remove_first_occurrence(r, directory)
      for files in f:
        remote_path = windows_to_url_path(os.path.join(dir, files))
        if remote_path.startswith("."):
          remote_path = remote_path[1:]
        if os.path.splitext(files)[1] not in filters:
          web_paths.put(remote_path)
          count += 1
    return web_paths, count
  
def test_remote(paths):
  
  hit_ok = []
  hit_nok = []
  
  while not paths.empty():
    path = paths.get()
    url = f"{target}{path}"
    try:
      response = requests.get(url)
      if response.status_code == 200:
        print("O", end="", flush=True)
        hit_ok.append(url)
      if response.status_code != 404:
        print("o", end="", flush=True)
        hit_nok.append(url)
      else:
        print("x", end="", flush=True)
    except Exception as e:
      pass
  
  return hit_ok, hit_nok
    
def remove_first_occurrence(main_string, substring):
    index = main_string.find(substring)
    if index != -1:
        return main_string[:index] + main_string[index + len(substring):]
    else:
        return main_string

def windows_to_url_path(windows_path):
    url_path = windows_path.replace("\\", "/")
    return url_path

def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        exit(1)

zip_file_path = os.path.join(os.curdir, zip)

download_file(download_link, zip_file_path)

temp_folder = unzip_to_temp_folder(zip_file_path)

paths, count = generate_paths(os.path.join(temp_folder, "wordpress"))

print(f"{count} paths")

ok, nok = test_remote(paths)

for path in ok:
  print(f"200 {path}")
for path in nok:
  print(f"nok {path}")


shutil.rmtree(temp_folder)
