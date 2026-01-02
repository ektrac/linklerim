import csv
import subprocess

def get_manifest_url(youtube_url):
    try:
        # yt-dlp -g komutunu çalıştır
result = subprocess.run(
    ["yt-dlp", "-g", "--user-agent", "Mozilla/5.0", youtube_url],
    capture_output=True,
    text=True,
    check=True
        )
        # Birden fazla satır dönebilir (video + ses ayrı olabilir)
        urls = result.stdout.strip().split("\n")
        return urls[0] if urls else None
    except subprocess.CalledProcessError as e:
        print(f"Hata: {youtube_url} için manifest alınamadı -> {e}")
        return None

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
