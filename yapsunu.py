import csv
import subprocess
import sys
from pathlib import Path

INPUT_FILE = "input.csv"
OUTPUT_FILE = "playlist.m3u"
COOKIES_FILE = "cookies.txt"

def get_stream_urls(url):
    if "youtube.com" in url or "youtu.be" in url:
        cmd = ["yt-dlp", "--cookies", COOKIES_FILE, "-f", "bestvideo+bestaudio/best", "-g", url]
    elif "twitch.tv" in url:
        cmd = ["yt-dlp", "--cookies", COOKIES_FILE, "-f", "best", "-g", url]
    else:
        cmd = ["yt-dlp", "--cookies", COOKIES_FILE, "-f", "best", "-g", url]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return [u for u in result.stdout.strip().split("\n") if u]
    except subprocess.CalledProcessError as e:
        print(f"Hata: {url} için link alınamadı -> {e}", file=sys.stderr)
        return []

def main():
    lines = ["#EXTM3U"]
    with open(INPUT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for title, url in reader:
            urls = get_stream_urls(url.strip())
            if urls:
                lines.append(f'#EXTINF:-1 tvg-name="{title}" group-title="Auto", {title}')
                lines.append("#EXTVLCOPT:http-user-agent=Mozilla/5.0")
                lines.append("#EXTVLCOPT:http-referrer=https://www.youtube.com/")
                for u in urls:
                    lines.append(u)
            else:
                print(f"Uyarı: {title} için uygun link bulunamadı.", file=sys.stderr)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"{OUTPUT_FILE} oluşturuldu.")

if __name__ == "__main__":
    main()
