import asyncio
import aiohttp
import aiofiles
import pandas as pd
import os

BASE_URLS = {
   "F": "https://play.pokemonshowdown.com/sprites/ani-back/",
   "S": "https://play.pokemonshowdown.com/sprites/ani/"
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, os.pardir, "datasets", "pokemon.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, os.pardir, "webpage", "static", "img", "sprites")
MAX_CONCURRENT = 20
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def download_sprite(session: aiohttp.ClientSession, sem: asyncio.Semaphore, name: str, suffix: str, base_url: str):
   # Generate the key for the URL based on the name
   key: str = name.lower().replace(" ", "-")
   if key.startswith("mega-"):
      key = f"{key[5:]}-mega"
   if key.endswith("-small-size"):
      key = f"{key[:len(key) - 11]}-small"
   if key.endswith("-average-size"):
      key = f"{key[:len(key) - 13]}"
   if key.endswith("-large-size"):
      key = f"{key[:len(key) - 11]}-large"
   if key.endswith("-super-size"):
      key = f"{key[:len(key) - 11]}-super"
   if key.endswith("-x-mega"):
      key = f"{key[:len(key) - 7]}-megax"
   if key.endswith("-y-mega"):
      key = f"{key[:len(key) - 7]}-megay"
   # Construct the URL and filename
   url: str = f"{base_url}{key}.gif"
   filename: str = f"{name}_{suffix}.gif"
   save_path: str = os.path.join(OUTPUT_DIR, filename)
   # Check if the file already exists
   if os.path.exists(save_path):
      return
   # Download the sprite
   async with sem:
      try:
         async with session.get(url, timeout=10) as resp:
            if resp.status == 200:
               content = await resp.read()
               async with aiofiles.open(save_path, "wb") as f:
                  await f.write(content)
                  print(f"Downloaded: {filename}")
            else:
               print(f"Not found ({resp.status}): {url}")
      except Exception as e:
         print(f"Error downloading {url}: {e}")

async def main():
   # Read the CSV file and get the list of Pokémon names
   df: pd.DataFrame = pd.read_csv(CSV_PATH)
   pokemon_names: list[str] = df['Name'].tolist()
   timeout = aiohttp.ClientTimeout(total=15)
   conn = aiohttp.TCPConnector(limit=None)
   # Download sprites concurrently
   async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
      sem = asyncio.Semaphore(MAX_CONCURRENT)
      tasks = []
      for name in pokemon_names:
         for suffix, base_url in BASE_URLS.items():
               tasks.append(download_sprite(session, sem, name, suffix, base_url))
      await asyncio.gather(*tasks)

if __name__ == "__main__":
   # Run the main function
   print("Starting sprite download...")
   asyncio.run(main())
