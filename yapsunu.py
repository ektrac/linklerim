import csv
import subprocess
import sys
from pathlib import Path

INPUT_FILE = "input.csv"
OUTPUT_FILE = "playlist.m3u"
COOKIES_FILE = "cookies.txt"  # varsa anonim/non-login cookies.txt, yoksa None bırak

def get_stream_url(youtube_url):
    # Önce HLS video+audio dene, yoksa progressive fallback
    cmd = ["yt-dlp", "-f", "625+140/625+bestaudio/best[ext=mp4]/best", "-g", youtube_url]
    if COOKIES_FILE and Path(COOKIES_FILE).exists():
        cmd[1:1] = ["--cookies", COOKIES_FILE]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        urls = [u for u in result.stdout.strip().split("\n") if u]
        if urls:
            # Eğer tek link dönerse direkt al
            if len(urls) == 1:
                return urls[0]
            # Eğer iki link dönerse (video+audio), VLC genelde mux edebiliyor
            return urls[0]
    except subprocess.CalledProcessError as e:
        print(f"Hata: {youtube_url} için link alınamadı -> {e}", file=sys.stderr)
        return None

def main():
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        print(f"{INPUT_FILE} bulunamadı.", file=sys.stderr)
        sys.exit(1)

    lines = ["#EXTM3U"]

    with input_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # başlık satırını atla
        for title, grup, url in reader:
            title = title.strip()
            url = url.strip()
            final_link = get_stream_url(url)
            if final_link:
                lines.append(f'#EXTINF:-1 tvg-name="{title}" group-title="{grup}", {title}')
                lines.append("#EXTVLCOPT:http-user-agent=Mozilla/5.0")
                lines.append("#EXTVLCOPT:http-referrer=https://www.youtube.com/")
                lines.append(final_link)
            else:
                print(f"Uyarı: {title} için uygun link bulunamadı.", file=sys.stderr)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"{OUTPUT_FILE} oluşturuldu.")

if __name__ == "__main__":
    main()
