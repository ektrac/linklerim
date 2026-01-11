import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime
import time

CHANNEL_URL = "https://www.youtube.com/@DoktorAlekseevTR/videos"  # kanalın videolar sekmesi
OUTPUT_FILE = "channel_playlist.m3u"
COOKIES_FILE = "cookies.txt"  # varsa non-login cookies.txt
RETRY = 2   # geçici hatalarda tekrar deneme sayısı
WAIT = 2    # denemeler arası bekleme süresi (sn)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def run(cmd):
    log(f"Komut: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.stdout.strip():
        log("STDOUT:")
        print(res.stdout)
    if res.stderr.strip():
        log("STDERR:")
        print(res.stderr, file=sys.stderr)
    log(f"Exit code: {res.returncode}")
    return res

def get_video_ids(channel_url):
    log(f"Kanal video listesi çekiliyor: {channel_url}")
    cmd = ["yt-dlp", "--flat-playlist", "-J", channel_url]
    # İsteğe bağlı: ayrıntılı debug için -v ekleyebilirsin
    # cmd.insert(1, "-v")
    res = run(cmd)
    if res.returncode != 0:
        log("Hata: Kanal listesini alamadım.")
        return []
    try:
        data = json.loads(res.stdout)
        entries = data.get("entries", [])
        log(f"Toplam video sayısı: {len(entries)}")
        return [(e.get("id"), e.get("title")) for e in entries if e.get("id")]
    except json.JSONDecodeError:
        log("Hata: JSON parse başarısız.")
        return []

def get_stream_urls(video_url):
    base_cmd = [
        "yt-dlp",
        "--js-runtimes", "node",            # Node.js runtime; lokalde Node kuruluysa önerilir
        "--user-agent", "Mozilla/5.0",
        "--referer", "https://www.youtube.com/",
        "-f", "bestvideo+bestaudio/best",
        "--cookies" "cookies.txt",
        "-g", video_url
    ]
    if COOKIES_FILE and Path(COOKIES_FILE).exists():
        base_cmd[1:1] = ["--cookies", COOKIES_FILE]

    for attempt in range(1, RETRY + 2):
        log(f"Stream URL alınıyor (deneme {attempt}/{RETRY+1}): {video_url}")
        res = run(base_cmd)
        if res.returncode == 0:
            urls = [u for u in res.stdout.strip().split("\n") if u]
            log(f"Bulunan URL sayısı: {len(urls)}")
            if urls:
                return urls
            else:
                log("Uyarı: Çıktı boş görünüyor.")
        else:
            log("Hata: Stream URL alınamadı.")
        if attempt <= RETRY:
            log(f"Bekleniyor: {WAIT} sn sonra tekrar denenecek...")
            time.sleep(WAIT)

    return []

def main():
    log("Süreç başladı")
    log(f"Kanal: {CHANNEL_URL}")
    log(f"Çıktı dosyası: {OUTPUT_FILE}")
    if COOKIES_FILE and Path(COOKIES_FILE).exists():
        log(f"Cookies: {COOKIES_FILE} bulundu ve kullanılacak")
    else:
        log("Cookies dosyası yok, cookies kullanılmayacak")

    videos = get_video_ids(CHANNEL_URL)
    if not videos:
        log("Video bulunamadı veya liste alınamadı, çıkılıyor.")
        sys.exit(1)

    lines = ["#EXTM3U"]
    success = 0
    fail = 0

    total = len(videos)
    for idx, (vid, title) in enumerate(videos, start=1):
        safe_title = title or f"Video {vid}"
        video_url = f"https://www.youtube.com/watch?v={vid}"
        log(f"[{idx}/{total}] İşleniyor: {safe_title}")
        urls = get_stream_urls(video_url)
        if urls:
            lines.append(f'#EXTINF:-1 tvg-name="{safe_title}", {safe_title}')
            lines.append("#EXTVLCOPT:http-user-agent=Mozilla/5.0")
            lines.append("#EXTVLCOPT:http-referrer=https://www.youtube.com/")
            lines.extend(urls)
            success += 1
            log(f"[{idx}] OK: Playlist’e eklendi")
        else:
            fail += 1
            log(f"[{idx}] FAIL: Uygun stream bulunamadı")

    log(f"Playlist yazılıyor: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    log("Süreç tamamlandı")
    log(f"Özet → Başarılı: {success} | Başarısız: {fail} | Toplam: {total}")
    print(f"{OUTPUT_FILE} oluşturuldu.")

if __name__ == "__main__":
    main()
