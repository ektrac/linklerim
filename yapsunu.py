#!/usr/bin/env python3
import csv
import subprocess
import os

def get_manifest_url(youtube_url):
    # Önce -g dene (verbose)
    try:
        result = subprocess.run(
            ["yt-dlp", "-v", "-g", youtube_url],
            capture_output=True,
            text=True,
            check=True
        )
        urls = result.stdout.strip().split("\n")
        if urls:
            return urls[0]
    except subprocess.CalledProcessError as e:
        print(f"[yt-dlp -g hata] URL={youtube_url}")
        print(f"Komut: {' '.join(e.cmd)}")
        print(f"Çıkış kodu: {e.returncode}")
        print(f"STDOUT:\n{e.stdout.strip()}")
        print(f"STDERR:\n{e.stderr.strip()}")

    # Fallback: doğrudan oynatılabilir URL denemeleri
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
        except subprocess.CalledProcessError as e:
            print(f"[yt-dlp fallback hata] cmd={' '.join(cmd)}")
            print(f"Çıkış kodu: {e.returncode}")
            print(f"STDOUT:\n{e.stdout.strip()}")
            print(f"STDERR:\n{e.stderr.strip()}")

    print(f"Hata: {youtube_url} için oynatılabilir link alınamadı")
    return None

def generate_m3u(csv_file, m3u_file):
    with open(csv_file, newline='', encoding='utf-8') as f, open(m3u_file, 'w', encoding='utf-8') as out:
        reader = csv.reader(f)
        out.write("#EXTM3U\n")
        for row in reader:
            if not row:
                continue
            name, url = row[0], row[1]
            manifest_url = get_manifest_url(url)
            if manifest_url:
                out.write(f"#EXTINF:-1,{name}\n{manifest_url}\n")
            else:
                print(f"Hata: {url} için oynatılabilir link bulunamadı.")

if __name__ == "__main__":
    outfile = os.path.join(os.environ.get("GITHUB_WORKSPACE", "."), "playlist.m3u")
    generate_m3u("input.csv", outfile)
    print(f"playlist.m3u oluşturuldu: {outfile}")
