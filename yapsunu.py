#!/usr/bin/env python3
import csv, subprocess, time

def run_cmd(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        # Ayrıntılı hata logu
        print(f"[yt-dlp error] cmd={' '.join(cmd)} code={e.returncode}\nSTDERR:\n{e.stderr.strip()}")
        return None

def get_playable_url(youtube_url):
    # Sıra: en iyi video+ses → mp4 tek parça → sadece ses
    tries = [
        ["yt-dlp", "-f", "bestvideo+bestaudio", "--get-url", youtube_url],
        ["yt-dlp", "-f", "best[ext=mp4]", "--get-url", youtube_url],
        ["yt-dlp", "-f", "bestaudio", "--get-url", youtube_url],
    ]
    for cmd in tries:
        r = run_cmd(cmd)
        if r and r.stdout.strip():
            return r.stdout.strip().split("\n")[0]
    # Son çare: manifest denemesi (bazı içeriklerde yardımcı olur)
    r = run_cmd(["yt-dlp", "-g", youtube_url])
    if r and r.stdout.strip():
        return r.stdout.strip().split("\n")[0]
    return None

def generate_m3u(csv_file, m3u_file):
    with open(csv_file, newline='', encoding='utf-8') as f, open(m3u_file, 'w', encoding='utf-8') as out:
        reader = csv.reader(f)
        out.write("#EXTM3U\n")
        for row in reader:
            if not row: 
                continue
            name, url = row[0], row[1]
            playable = get_playable_url(url)
            if playable:
                out.write(f"#EXTINF:-1,{name}\n{playable}\n")
            else:
                print(f"Hata: {url} için oynatılabilir link/manifest alınamadı.")

if __name__ == "__main__":
    generate_m3u("input.csv", "playlist.m3u")
    print("playlist.m3u oluşturuldu.")
