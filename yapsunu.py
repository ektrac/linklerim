import csv
import subprocess
import sys
import time
from pathlib import Path

INPUT_FILE = "input.csv"
OUTPUT_FILE = "playlist.m3u"
COOKIES_FILE = "cookies.txt"  # non-login cookies varsa aynı dizinde
RETRY = 2                     # kısa retry denemeleri
TIMEOUT = 45                  # saniye

def run_ytdlp(cmd):
    # Komutları görünür kıl: debug için log yaz
    print(f"[cmd] {' '.join(cmd)}")
    res = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=TIMEOUT
    )
    if res.stdout.strip():
        print("[stdout]")
        print(res.stdout)
    if res.stderr.strip():
        print("[stderr]")
        print(res.stderr, file=sys.stderr)
    return res

def build_cmd(base, url):
    cmd = ["yt-dlp", "-v"] + base + [url]
    if COOKIES_FILE and Path(COOKIES_FILE).exists():
        cmd[1:1] = ["--cookies", COOKIES_FILE]
    # Bazı ortamlarda UA/referrer yardımcı olabilir
    cmd[1:1] = ["--user-agent", "Mozilla/5.0", "--referer", "https://www.youtube.com/"]
    return cmd

def get_urls_youtube(url):
    # Format fallbacks: en üstte birleşik, sonra progressive, sonra en iyisi
    formats = [
        ["-f", "bestvideo+bestaudio/best", "-g"],
        ["-f", "best[ext=mp4]/best", "-g"],
        ["-f", "best", "-g"]
    ]
    for base in formats:
        for attempt in range(RETRY + 1):
            res = run_ytdlp(build_cmd(base, url))
            if res.returncode == 0:
                urls = [u for u in res.stdout.strip().split("\n") if u]
                if urls:
                    return urls
            else:
                # Bazı nsig hataları geçici olabilir; kısacık bekle
                time.sleep(1.0)
    return []

def get_urls_twitch(url):
    # Twitch çoğu zaman HLS manifest döndürür; best genellikle yeterli
    formats = [
        ["-f", "best", "-g"],
        ["-f", "best", "-g", "--compat-options", "youtube-dl"]
    ]
    for base in formats:
        for attempt in range(RETRY + 1):
            res = run_ytdlp(build_cmd(base, url))
            if res.returncode == 0:
                urls = [u for u in res.stdout.strip().split("\n") if u]
                if urls:
                    return urls
            else:
                time.sleep(1.0)
    return []

def get_stream_urls(url):
    if "youtube.com" in url or "youtu.be" in url:
        return get_urls_youtube(url)
    if "twitch.tv" in url:
        return get_urls_twitch(url)
    # Diğer alanlar için düz best
    base = ["-f", "best", "-g"]
    res = run_ytdlp(build_cmd(base, url))
    if res.returncode == 0:
        return [u for u in res.stdout.strip().split("\n") if u]
    return []

def main():
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        print(f"{INPUT_FILE} bulunamadı.", file=sys.stderr)
        sys.exit(1)

    lines = ["#EXTM3U"]
    with input_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # başlık: title,url
        for title, url in reader:
            title = title.strip()
            url = url.strip()
            urls = get_stream_urls(url)
            if urls:
                lines.append(f'#EXTINF:-1 tvg-name="{title}" group-title="Auto", {title}')
                lines.append("#EXTVLCOPT:http-user-agent=Mozilla/5.0")
                # YouTube referrer pek çok player için faydalı, Twitch’e de zarar vermez
                lines.append("#EXTVLCOPT:http-referrer=https://www.youtube.com/")
                lines.extend(urls)
            else:
                print(f"Uyarı: {title} için uygun link bulunamadı.", file=sys.stderr)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"{OUTPUT_FILE} oluşturuldu.")

if __name__ == "__main__":
    main()
