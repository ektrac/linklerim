#!/usr/bin/env python3
import csv, subprocess, os, json

COOKIES_FILE = os.path.join(os.environ.get("GITHUB_WORKSPACE", "."), "cookies.txt")

def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return r.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[yt-dlp hata] cmd={' '.join(cmd)} code={e.returncode}")
        print(f"STDOUT:\n{e.stdout.strip()}")
        print(f"STDERR:\n{e.stderr.strip()}")
        return ""

def get_hls_url(url):
    base = ["yt-dlp", "--cookies", COOKIES_FILE, "--dump-json", url]
    try:
        r = subprocess.run(base, capture_output=True, text=True, check=True)
        data = json.loads(r.stdout)
        # Öncelik: HLS manifest
        if "hls_manifest_url" in data:
            return data["hls_manifest_url"]
        for f in data.get("formats", []):
            if f.get("protocol") == "m3u8" and f.get("url"):
                return f["url"]
        # Fallback: en iyi mp4
        for f in data.get("formats", []):
            if f.get("ext") == "mp4" and f.get("url"):
                return f["url"]
    except subprocess.CalledProcessError as e:
        print(f"[yt-dlp dump-json hata] {url} code={e.returncode}\nSTDERR:\n{e.stderr.strip()}")
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
            if not url.startswith("http"):
                print(f"Geçersiz URL: {url}")
                continue
            hls = get_hls_url(url)
            if hls:
                out.write(f"#EXTINF:-1,{name}\n{hls}\n")
            else:
                print(f"Hata: {url} için oynatılabilir link bulunamadı.")

if __name__ == "__main__":
    outfile = os.path.join(os.environ.get("GITHUB_WORKSPACE", "."), "playlist.m3u")
    generate_m3u("input.csv", outfile)
    print(f"playlist.m3u oluşturuldu: {outfile}")
