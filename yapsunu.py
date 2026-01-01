name: Generate M3U

on:
  schedule:
    - cron: "0 */2 * * *"   # Her 2 saatte bir yenile
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Show CSV
        run: cat input.csv

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install yt-dlp
        run: pip install -U yt-dlp

      - name: Install Node.js (JS runtime for yt-dlp)
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Write cookies
        run: echo "${{ secrets.YTDLP_COOKIES }}" > cookies.txt

      - name: Run script
        run: python yapsunu.py

      - name: Commit and push playlist
        run: |
          git config --global user.name "github-actions"
          git config --global user.email "actions@github.com"
          if [ -f playlist.m3u ]; then
            git add playlist.m3u
            if ! git diff --cached --quiet; then
              git commit -m "Update playlist"
              git pull --rebase
              git push
            else
              echo "No changes, skipping push."
            fi
          else
            echo "playlist.m3u bulunamadı, push atlanıyor."
          fi
