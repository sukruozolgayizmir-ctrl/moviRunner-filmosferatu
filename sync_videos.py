"""
MoviRunner x Filmosferatu - kanal videolarini WebM'e cevirir, videos.json uretir.

KURULUM (bir kez, PowerShell):
  winget install Gyan.FFmpeg
  pip install -U yt-dlp
KULLANIM (index.html ile ayni klasorde):
  py sync_videos.py              # en cok begenilen 24 video (varsayilan)
  py sync_videos.py --all        # kanallardaki tum videolar
  py sync_videos.py --only fs    # sadece Filmosferatu Shorts (hizli)
  py sync_videos.py --json-only  # indirmeden, hazir olanlarla videos.json yaz
  py sync_videos.py --max-mb 900 # GitHub Pages ~1 GB siniri icin toplam boyut tavani
Tekrar calistirinca yalnizca yeni videolari ekler (mevcut dosyalari atlar).
Cikti: videos/<id>.webm, videos/<id>.webp (poster), videos.json
"""
import argparse, json, subprocess, sys, datetime
from pathlib import Path

CHANNELS = {"mr": "https://www.youtube.com/@MoviRunner/videos",
            "fs": "https://www.youtube.com/@Filmosferatu/videos"}
# vidIQ verisine gore (16.11.2026) en cok begenilen videolar, begeniye gore sirali
TOP = {
    "mr": ["bQt7pxt-cz8", "aho-y0J6z-E", "wjza4YtBLzE", "wVqWj7PUkso", "GTyuaSsJQkQ", "ZyYvfPd8p9M",
           "7OHrfjlGY-0", "h9Fivq6os04", "EByog3MGqJk", "You5NW2Mh_w", "eCvrO6ksfds", "0i10l7MqN_I",
           "mfd_h6Tv3bE", "R_Il2t-ww04", "K9O2y9hy4a0", "NviGhkeJgSE", "qjrtC8xUYus", "LHaqU8uj7Ec", "wCPwaR8jq9U", "sx1uyYPyB1M", "f5wnamjzEBA", "ukpMMvegnaM", "t59hfxSEzZk", "z8zGPYs1_jE"],
    "fs": ["Hi3y0O1u0zU", "k589XlYTMVg", "Sck3Rp8hi7I", "ZUOAltX5UV4", "a7YLeocaLf8", "yWXMrGwNxWM",
           "SOX3Zln17xI", "F654DDaeHgE", "llcsltX-Pgs", "lgYS9Ljw4Jo", "tVhJE0qnBMY", "bBHCATssIlw",
           "TFTz7CCr6mk", "Wj9Wbhid75Q", "EW3nkyuqMl8", "LXFJUaVIj_4", "HyZYfziuESY", "Vso5chbEGng", "8Zpk_6wGu28", "gwF0J0q0E2Q", "S5uE3p7QK1g", "7-abqk5xxOg", "UH6rj0TFGhk", "HFbbQ9Ltp_s"],
}
OUT = Path("videos"); OUT.mkdir(exist_ok=True)
MAX_FILE_MB = 95  # GitHub tek dosya siniri 100 MB

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def ids_of(url):
    r = run(["yt-dlp", "--flat-playlist", "--print", "id", url])
    return [x.strip() for x in r.stdout.splitlines() if len(x.strip()) == 11]

def info_of(vid):
    r = run(["yt-dlp", "-J", "--skip-download", f"https://www.youtube.com/watch?v={vid}"])
    return json.loads(r.stdout) if r.returncode == 0 else None

def build(vid):
    webm, poster = OUT / f"{vid}.webm", OUT / f"{vid}.webp"
    part = OUT / f"{vid}.part.webm"; part.unlink(missing_ok=True)
    if webm.exists():
        return True
    tmp = OUT / f"{vid}.src.mkv"
    print("  indiriliyor...", flush=True)
    r = run(["yt-dlp", "-f", "bv*[height<=720]+ba/b[height<=720]", "--merge-output-format", "mkv",
             "-o", str(tmp), f"https://www.youtube.com/watch?v={vid}"])
    src = next(OUT.glob(f"{vid}.src.*"), None)
    if r.returncode != 0 or not src:
        print("  indirme basarisiz:", vid); return False
    print("  WebM'e cevriliyor (uzun videoda dakikalar surebilir)...", flush=True)
    r = run(["ffmpeg", "-y", "-i", str(src), "-c:v", "libvpx-vp9", "-crf", "32", "-b:v", "1800k",
             "-maxrate", "2600k", "-bufsize", "5200k", "-g", "96", "-keyint_min", "48",
             "-tile-columns", "2", "-row-mt", "1", "-deadline", "good", "-cpu-used", "4", "-vf", "scale=-2:'min(720,ih)'",
             "-c:a", "libopus", "-b:a", "96k", "-cues_to_front", "1", str(part)])
    src.unlink(missing_ok=True)
    if r.returncode != 0:
        print("  donusturme basarisiz:", vid); part.unlink(missing_ok=True); return False
    part.replace(webm)
    if webm.stat().st_size > MAX_FILE_MB * 1024 * 1024:
        print(f"  {vid} {MAX_FILE_MB} MB'i asiyor, atlandi"); webm.unlink(); return False
    run(["ffmpeg", "-y", "-ss", "3", "-i", str(webm), "-frames:v", "1",
         "-vf", "scale=640:-2", str(poster)])
    return True

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--max-mb", type=int, default=850)
    ap.add_argument("--only", choices=["mr", "fs"], help="Yalnizca bir kanal: mr=MoviRunner, fs=Filmosferatu (Shorts daha hizli biter)")
    ap.add_argument("--json-only", action="store_true", help="Indirme yapma; videos klasorunde hazir olanlarla videos.json yaz")
    ap.add_argument("--all", action="store_true", help="Yalnizca TOP degil, kanaldaki tum videolari isle")
    a = ap.parse_args()
    today = datetime.date.today().isoformat(); total = 0; data = {}
    for key, url in CHANNELS.items():
        if a.only and key != a.only: continue
        data[key] = []
        for vid in (ids_of(url) if a.all else TOP[key]):
            if total >= a.max_mb * 1024 * 1024:
                print("Boyut tavanina ulasildi, durduruldu."); break
            print(key, vid)
            if a.json_only:
                if not (OUT / f"{vid}.webm").exists(): continue
            elif not build(vid): continue
            total += (OUT / f"{vid}.webm").stat().st_size
            inf = info_of(vid) or {}
            item = {"id": vid, "title": inf.get("title", vid), "tag": (inf.get("tags") or [""])[0],
                    "webm": f"videos/{vid}.webm",
                    "stats": {"views": str(inf.get("view_count", "")), "likes": str(inf.get("like_count", "")),
                              "comments": str(inf.get("comment_count", "")), "asOf": today}}
            if (OUT / f"{vid}.webp").exists(): item["poster"] = f"videos/{vid}.webp"
            data[key].append(item)
    Path("videos.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Bitti. Toplam {total/1048576:.0f} MB. videos.json yazildi.")

if __name__ == "__main__":
    sys.exit(main())
