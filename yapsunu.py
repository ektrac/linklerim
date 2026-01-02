import csv
import subprocess

def get_manifest_url(url):
    try:
        if "youtube.com" in url or "youtu.be" in url:
            cmd = ["yt-dlp", "-f", "bestvideo+bestaudio/best", "-g", url]
        elif "twitch.tv" in url:
            cmd = ["yt-dlp", "-f", "best", "-g", url]
        else:
            cmd = ["yt-dlp", "-f", "best", "-g", url]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        urls = [u for u in result.stdout.strip().split("\n") if u]
        # Eğer video+audio iki link dönerse, playlist’e ikisini de yazabilirsin
        return urls
    except subprocess.CalledProcessError as e:
        print(f"Hata: {url} için manifest alınamadı -> {e}")
        return []

rows = []
with open("input.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)  # başlık satırını atla
    for title, url in reader:
        rows.append((title.strip(), url.strip()))

lines = ["#EXTM3U"]
for title, url in rows:
    manifest = get_manifest_url(url)
    if manifest:
        lines.append(f'#EXTINF:-1 tvg-name="{title}" group-title="YouTube", {title}')
        lines.append(manifest)

with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("playlist.m3u oluşturuldu.")
