#!/usr/bin/env python3
import csv
import subprocess
import os

COOKIES_FILE = os.path.join(os.environ.get("GITHUB_WORKSPACE", "."), "cookies.txt")

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"[yt-dlp hata] cmd={' '.join(cmd)} code={e.returncode}")
        print(f"STDOUT:\n{e.stdout.strip()}")
        print(f"STDERR:\n{e.stderr.strip()}")
        return []

def get_manifest_url(youtube_url):
    base = ["yt-dlp", "--geo-bypass", "--cookies", COOKIES_FILE]
    tries = [
        base + ["-v", "-g", youtube_url],
        base + ["-f", "bestvideo+bestaudio", "--get-url", youtube_url],
        base + ["-f", "best[ext=mp4]", "--get-url", youtube_url],
        base + ["-f", "bestaudio", "--get-url", youtube_url],
    ]
    for cmd in tries:
        urls = run_cmd(cmd)
        if urls:
            return urls[0]
    print(f"Hata: {youtube_url} için oynatılabilir link alınamadı")
    return None

def generate_m3u(csv_file, m3u_file):
    with open(csv_file, newline='', encoding='utf-8') as f, open(m3u_file, 'w', encoding='utf-8') as out:
        reader = csv.reader(f)
        out.write("#EXTM3U\n")
        for row in reader:
            if len(row) < 2:
                print(f"Satır hatalı: {row}")
                continue
            name, url = row[0].strip(), row[1].strip()
            manifest_url = get_manifest_url(url)
            if manifest_url:
                out.write(f"#EXTINF:-1,{name}\n{manifest_url}\n")
            else:
                print(f"Hata: {url} için oynatılabilir link bulunamadı.")

if __name__ == "__main__":
    outfile = os.path.join(os.environ.get("GITHUB_WORKSPACE", "."), "playlist.m3u")
    generate_m3u("input.csv", outfile)
    print(f"playlist.m3u oluşturuldu: {outfile}")
