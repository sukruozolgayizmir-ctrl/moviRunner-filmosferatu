# MoviRunner x Filmosferatu - Cinema Culture

Maliyet: 0 (GitHub Pages, public repo, kart tanimlama yok).

## Kurulum
1. `baslat.bat` dosyasina cift tikla (Python, ffmpeg, yt-dlp eksikse kurar; kurulum sonrasi dosyayi tekrar calistir).
2. Bitince bu klasorde `videos/` ve `videos.json` olusur (en cok begenilen 24 video, WebM).
3. GitHub Desktop ile bu klasoru `moviRunner-filmosferatu` adiyla PUBLIC repo olarak yayinla.
4. GitHub > Settings > Pages > Deploy from a branch > main / (root).

## Limitler (GitHub Pages)
Site 1 GB, aylik 100 GB yumusak trafik, tek dosya 100 MB. Kart istenirse DUR.

## Tum kanal icin
`py sync_videos.py --all` (boyut tavani varsayilan 900 MB).
