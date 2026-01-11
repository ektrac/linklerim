import csv
import subprocess
import sys
from pathlib import Path
from datetime import datetime

INPUT_FILE = "input.csv"
OUTPUT_FILE = "KendiListem.m3u"
COOKIES_FILE = "cookies.txt"  # varsa anonim/non-login cookies.txt

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def run(cmd):
    log(f"Komut: {' '.join(cmd)}")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if res.stdout.strip():
            log("STDOUT:")
            print(res.stdout)
        if res.stderr.strip():
            log("STDERR:")
            print(res.stderr, file=sys.stderr)
        log(f"Exit code: {res.returncode}")
        return res
    except FileNotFoundError as e:
        log("HATA: Node.js bulunamadı veya PATH'te değil.")
        print(e, file=sys.stderr)
        return None
    except subprocess.CalledProcessError as e:
        log("Komut başarısız oldu.")
        print(e, file=sys.stderr)
        return None

def get_stream_url(youtube_url):
    cmd = [
        "yt-dlp",
        "--js-runtimes", "node",  # Node.js runtime kullan
        "--cookies", cookies.txt, # buraya cookies parametresi eklendi
        "-f", "625+140/625+bestaudio/best[ext=mp4]/best",
        "-g", youtube_url
    ]
    if COOKIES_FILE and Path(COOKIES_FILE).exists():
        cmd[1:1] = ["--cookies", COOKIES_FILE]

    log(f"Stream URL alınıyor: {youtube_url}")
    res = run(cmd)
    if res and res.returncode == 0:
        urls = [u for u in res.stdout.strip().split("\n") if u]
        if urls:
            log(f"Bulunan URL sayısı: {len(urls)}")
            return urls[0]
        else:
            log("Uyarı: Çıktı boş")
    else:
        log("Hata: Stream URL alınamadı")
    return None

def main():
    log("Süreç başladı")
    input_path = Path(INPUT_FILE)
    if not input_path.exists():
        log(f"{INPUT_FILE} bulunamadı.")
        sys.exit(1)

    lines = ["#EXTM3U"]
    success = 0
    fail = 0

    with input_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        log(f"CSV başlık: {header}")
        rows = list(reader)
        log(f"Toplam satır: {len(rows)}")

        for idx, (title, grup, url) in enumerate(rows, start=1):
            log(f"[{idx}/{len(rows)}] İşleniyor: {title} ({grup})")
            final_link = get_stream_url(url.strip())
            if final_link:
                lines.append(f'#EXTINF:-1 tvg-name="{title.strip()}" group-title="{grup.strip()}", {title.strip()}')
                lines.append("#EXTVLCOPT:http-user-agent=Mozilla/5.0")
                lines.append("#EXTVLCOPT:http-referrer=https://www.youtube.com/")
                lines.append(final_link)
                success += 1
                log(f"[{idx}] OK: Playlist’e eklendi")
            else:
                fail += 1
                log(f"[{idx}] FAIL: Uygun link bulunamadı")

    log(f"Playlist yazılıyor: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    log("Süreç tamamlandı")
    log(f"Özet → Başarılı: {success} | Başarısız: {fail} | Toplam: {success+fail}")
    print(f"{OUTPUT_FILE} oluşturuldu.")

if __name__ == "__main__":
    main()
