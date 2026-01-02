import csv
import subprocess
import sys
from pathlib import Path

INPUT_FILE = "input.csv"
OUTPUT_FILE = "playlist.m3u"
COOKIES_FILE = "cookies.txt"  # varsa non-login cookies.txt, yoksa None bırak

def get_manifest_urls(url):
    try:
        if "youtube.com" in url or "youtu.be" in url:
            cmd = ["yt-dlp", "--cookies", COOKIES_FILE, "-f", "bestvideo+bestaudio/best", "-g", url]
        elif "twitch.tv" in url:
            cmd = ["yt-dlp", "--cookies", COOKIES_FILE, "-f", "best", "-g", url]
        else:
            cmd = ["yt-dlp", "--cookies", COOKIES_FILE, "-f", "best", "-g", url]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return [u for u in result.stdout.strip().split("\n") if u]
    except subprocess.CalledProcessError as e:
        print(f"Hata: {url} için manifest alınamadı -> {e}", file=sys.stderr)
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
            urls = get_manifest_urls(url.strip())
            if urls:
                lines.append(f'#EXTINF:-1 tvg-name="{title}" group-title="Auto", {title}')
                lines.append("#EXTVLCOPT:http-user-agent=Mozilla/5.0")
                lines.append("#EXTVLCOPT:http-referrer=https://www.youtube.com/")
                # Listeyi tek tek ekle
                lines.extend(urls)
            else:
                print(f"Uyarı: {title} için uygun link bulunamadı.", file=sys.stderr)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"{OUTPUT_FILE} oluşturuldu.")

if __name__ == "__main__":
    main()
