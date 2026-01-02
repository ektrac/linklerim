import csv
import subprocess
import sys
from pathlib import Path

INPUT_FILE = "input.csv"
OUTPUT_FILE = "playlist.m3u"
COOKIES_FILE = "cookies.txt"  # varsa anonim/non-login cookies.txt

def get_stream_urls(url: str):
    # Domain bazlı format seçimi
    if "youtube.com" in url or "youtu.be" in url:
        base = ["-f", "bestvideo+bestaudio/best", "-g"]
    elif "twitch.tv" in url:
        base = ["-f", "best", "-g"]
    else:
        base = ["-f", "best", "-g"]

    cmd = [
        "yt-dlp",
        "--user-agent", "Mozilla/5.0",
        "--referer", "https://www.youtube.com/",
    ] + base + [url]

    if COOKIES_FILE and Path(COOKIES_FILE).exists():
        cmd[1:1] = ["--cookies", COOKIES_FILE]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        urls = [u for u in result.stdout.strip().split("\n") if u]
        return urls
    except subprocess.CalledProcessError as e:
        print(f"Hata: {url} için link alınamadı -> {e}", file=sys.stderr)
        return []

def main():
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        print(f"{INPUT_FILE} bulunamadı.", file=sys.stderr)
        sys.exit(1)

    lines = ["#EXTM3U"]

    with input_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # başlık satırını atla
        for title, url in reader:
            urls = get_stream_urls(url.strip())
            if urls:
                lines.append(f'#EXTINF:-1 tvg-name="{title.strip()}", {title.strip()}')
                lines.append("#EXTVLCOPT:http-user-agent=Mozilla/5.0")
                lines.append("#EXTVLCOPT:http-referrer=https://www.youtube.com/")
                lines.extend(urls)
            else:
                print(f"Uyarı: {title} için uygun link bulunamadı.", file=sys.stderr)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"{OUTPUT_FILE} oluşturuldu.")

if __name__ == "__main__":
    main()
