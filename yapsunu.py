#!/usr/bin/env python3
import csv
import subprocess

def get_manifest_url(youtube_url):
    # Fallback denemeleri: en iyi video+ses → mp4 → sadece ses
    formats = [
        ["yt-dlp", "-f", "bestvideo+bestaudio", "--get-url", youtube_url],
        ["yt-dlp", "-f", "best[ext=mp4]", "--get-url", youtube_url],
        ["yt-dlp", "-f", "bestaudio", "--get-url", youtube_url],
    ]
    for cmd in formats:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            urls = result.stdout.strip().split("\n")
            if urls:
                return urls[0]
        except subprocess.CalledProcessError:
            continue
    print(f"Hata: {youtube_url} için oynatılabilir link alınamadı")
    return None

def generate_m3u(csv_file, m3u_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        with open(m3u_file, 'w', encoding='utf-8') as out:
            out.write("#EXTM3U\n")
            for row in reader:
                if not row:
                    continue
                name, url = row[0], row[1]
                manifest_url = get_manifest_url(url)
                if manifest_url:
                    out.write(f"#EXTINF:-1,{name}\n{manifest_url}\n")

if __name__ == "__main__":
    generate_m3u("input.csv", "playlist.m3u")
    print("playlist.m3u oluşturuldu.")
