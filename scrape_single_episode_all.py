#!/usr/bin/env python3
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import time
from html import unescape

import requests

OBF_KEY = "849959193z"
SALT = "738849914a"
STREAM_KEY = "951169923"
BASE_URL = "https://panel.wibuku.app"
PIXELDRAIN_API = "https://pixeldrain.com/api/file/"

USER_ID = "45adc097-cd90-4385-9ab4-5c9aff614feb"
DEVICE_ID = "a48283e3c7f2e983"
INITIAL_SESSION = "00020204020100050304479932197342"
APP_VERSION = "00016277351"
BAN_WAIT_BUFFER_SECONDS = 30
SLEEP_SECONDS = 0
DETAIL_FILE = "seires_animedetail.json"
THREADS = 15

# Ambil dari main.py
OLD_HASH = "MTUzMDAzMTcwODQ1NDgyMDA3MjAwMzE3MjU0NjEzMTM2MDAyMzkyMDIyMjMwMzU5MTUzMjUxMjAwNzIwMDM0MDE5MTY0ODIwMjIyMzAzMTM2MDAxMzYyMDA3MjAwMzA1MDIxMDI5MTYzMzIwMDM1MjAwMTUzMDAzMTAxNDQ1MjkyMDA3MjAyOTU4MDcwNjM5NDkyNTI2NTE2MjMzMjcxMTU3MjUyNjUwNTgzMzI3MzYwNDUwNDU2MjQxMzY0MjUyNTQ1NTI3NjQ2MjU1MjYzOTA5NTAzODUwNTc1MDI2NjMyMDU1MjY1NTQxMjUzODAyMTYzMzQyMzMxMzU1NDUwMjM4MjkyMDQ5MjA1MDMyMTk0MTI5MDY1NDYwMjk0NjM1MzA2MDM4NTQ2MzUwMDk0NDEwMjIxMDM5NDkyNTI2NTE2MjMzMjcxMTU3MjUyNjUwNTgzMzI3MzYyMDIyMjMwMzQ5MzY0MjUyMjQ1NTQ1MzM1OTM2MzA1MjA5MDg0NTAzMTYwODA5MDI0NzUwMTAxMTA5NTAzODI1MjAzMjA1NDkyMDM2NTMwMzEyMTQ0MjYzNDE1NTMyMjkyMDA3MjAwMzQ5NjAwMTE4NjIzMjM4NjM2MTE0MDExOTQ2MzY0MjYzNTkxNTA1Mjk0MzI5NDI2MzEwMzYzMDI5MDQyOTQyMTM1OTE0NTMzNTEwMDcyMDMxMTI1NTQyNjMzMDU1NDUwMzEzMzYzODE5MTMzNjUzMzUwNjA4MDExOTA2MDgzMDYyNDY2MDM4NTI0NjYwMDExOTEzMzYwMTYzMTAyMjQyMzMxMjYwMDUzMTU4MjUyNzM5NDkwNzI2NDg1NzA3MjczOTM4MjUyNjQ4MDkyOTIwNDkyMDU1MzIxMzQ5MjkwNjY0NTgzMzEwMzY1OTMzMTAyNTU4MjUwNjUxMTAyMjIzMDM1NDUwMzI0ODIwMDcwNjM5MDkzMzEwNDgwOTI1MjcyOTU5MjUyNzI1NDMyOTQyNTQ1OTA4MDUyOTA0Mjk0MTUyNDMxNTIzNTk1OTA4Mzk2MzQ3MDUyMDE2NTc2MDI3MzU1MDAyNDUwMzY0NDUzOTYyNTQ2MDEwNTU2MjAyNTkxNDQyMjUwMTUyMTIwMjQ1MTY0ODE0NjMxNDM0MTkyNzQ4NTk2MDYzMTEzMDE0MTA1MTIwMjg0ODAwMTEwNjE5MzA1NTI3NTk1MTU4MDYzNDE5MTU2NDE2Mjk2MjIzMzM2MTMzNTExMjEyMjY2NDQxNDE1NjQ1MzAyNjU1MTA1NDU0MTI0NTY0NDU1MjI1MzYwNDI3MzYyNzQyMzQwNjU5NDIzODQyMzM1NzI1MjIxMjMwNjE0NTUzNTQ2MDMwNTEyNzE2NDIxMDMyNDg2NDIyMDQ1ODMzMDMxODI1NTY1MDI2NTkyMzUyMjY1MzM4NTYzMjI0MjQ0MDM3MDIzOTU5NDgzODIxNDcxNDMyMzU2MTIyMzcyNzEyMzgwOTA3MDkyMTM1NTIyOTA1MzAzMTMzMDU1OTQ0MzQyMzE4MzIxMjIzMTc1MzM5MTIwNzMxMjIxNjQzMTgzMTQwNTIzNDA2MTYxNzY0MTQyMjYyNDUwNTEzMTc2MDI0MzYwODA4MTYyNzU1NDkzNjQ2MzMyOTM1MzEzODEyNTYyMjE4MjYxODQzMzk1MzIzMzAxODUwMDkwNTE0MTQ1OTU5Mjk1MzAxNTAxMDE2MTIyMDYwNTk1NDQ5MzA2MzMxNTYwMTExNDQwMzM5NTI1NDA3MjY0NjM0NDc1NDYzMzExMzYwNTA1NjQyMDkyOTM0NjE1NjU5MzYyMTIxMzE0OTQ1MjA1NjM3MjEyMzU0MjgzNjI1MDcxODU1MDYxOTQ1MDMzNjUyMTIzMTEyMzUyNDYyMzE1MTI5NjAzMzEwNDQ2MzA0NDg1NDU3NjIyNjE5NDUzODQyNTMyMDU2MTczNTM4NDUyODU1NjAwMzE4MjQwNDEzMTExNTU2NDg2NDUwMzM1MjQ5MzI1MTAzMTkyMzA5NTMwNTM1NDMyOTE5MDUxMzEwMDE0OTYzMzAwNjI0MjI2MzU5MzAxNTA1MTE2NDAyNTg1MDIzMTE2MDA2MzMyOTM1MDM0NDMzMjQ1MzM1MjczMTU1MjUxOTAxNDU2NDUzMzAzOTQ0MTUzNTQ5MDQ2MjU0NDgxNTA4MDEzMDQ1NDUyNTQyNTQzMDUyMTgyMzQxNjQ2MTE4NTE0NDA5NTAzNDE1MDc1NTQ0MjUyNDYyMTgxMTE2NTM1NTIyMjY0NjEwMTcyMjEyNDIwOTU0MTg2MzY0NjIwNzM3MDMxMDU3MTgxNjU1MjYzOTEzNDQ0NjMwNTUxOTM1MzM0MzA4MzgxNzA3MTcwMjI2MDEyMzU1MTU1ODMwMDIyODA5NTA2NDY0MTkyOTMzNDc2MDQwNjQ0NDYzMjU0MzA4MzA1MTUzMjU1MTU1MTYyMjUwMjA1MTU1NTgxMzIzNjM2MDYzNTczMjM1MzAzNzU4NDQ1NDA2MDc1NzA4NDkxODU2MjIyNjIyNDc0MTA2MzQwMzQ2NTMzOTM3MDkzMTMxNTc1MjUyMTY1NzA4MzgzNzU3MzE1MjMxMTYzNzM4MzE1NzU5NTk4NDk5NTkxOTN6LkdVSjZTak9hM3pndmhkZTFyRlZpLUxDcU1URGZJeThYTlBCYzcyRUtrbXNSV250UXdZQTlIcFpfNHgwYnU1bG8="


def extract_first(pattern, text):
    m = re.search(pattern, text)
    return m.group(1) if m else None


def http_get(url):
    return requests.get(url, timeout=10).text


def resolve_pdrain(link: str) -> str:
    file_id = extract_first(r"/u/([^/?#]+)", link) or extract_first(r"/file/([^/?#]+)", link)
    if not file_id:
        return link
    return f"{PIXELDRAIN_API}{file_id}?download"


def resolve_pillar(link: str) -> str:
    try:
        html = http_get(link)
        direct = extract_first(r'<source[^>]+src=["\']([^"\']+)', html)
        if direct:
            return unescape(direct).replace("\\/", "/")
        fallback = extract_first(r'(https?://[^"\']+\.mp4)', html)
        return fallback if fallback else link
    except Exception:
        return link


def resolve_kraken(link: str) -> str:
    try:
        html = http_get(link)
        direct = extract_first(r'(https?://[^"\']+\.mp4)', html)
        return direct if direct else link
    except Exception:
        return link


def resolve_link(link: str, tipe: str) -> str:
    if tipe == "pdrain":
        return resolve_pdrain(link)
    if tipe == "neomc":
        return resolve_pillar(link)
    if tipe == "kfiles":
        return resolve_kraken(link)
    return link


class DeviceHashGenerator:
    def __init__(self, old_hash: str):
        self.old_hash = old_hash

    def reverse_obfuscation_once(self, obf_text: str) -> str:
        left, right = obf_text.split(OBF_KEY, 1)
        return "".join(right[int(left[i:i + 2])] for i in range(0, len(left), 2))

    def obfuscate_once(self, text: str) -> str:
        charset = []
        index_map = []
        for ch in text:
            if ch not in charset:
                charset.append(ch)
            index_map.append(f"{charset.index(ch):02d}")
        return "".join(index_map) + OBF_KEY + "".join(charset)

    def regenerate_token(self) -> str:
        step1 = base64.b64decode(self.old_hash).decode()
        raw = self.reverse_obfuscation_once(step1)
        pos = raw.rfind(SALT)
        jwt_token = raw[:pos]
        nano_time = str(int(time.time() * 1000))
        new_raw = jwt_token + SALT + nano_time
        obf = self.obfuscate_once(new_raw)
        return base64.b64encode(obf.encode()).decode()


def permute_once(s: str, key: str = STREAM_KEY) -> str:
    if key not in s:
        raise ValueError("Key tidak ditemukan")
    left, right = s.split(key, 1)
    return "".join(right[int(left[i:i + 2])] for i in range(0, len(left), 2))


def decode_stream_link(enc: str) -> str:
    stage1 = permute_once(enc)
    stage2 = permute_once(stage1)
    decoded = base64.b64decode(stage2)
    return decoded.decode("utf-8", errors="replace")


def parse_ban_seconds(error_text: str) -> int:
    m = re.search(r"\((\d+)\s*Menit\)", error_text, flags=re.IGNORECASE)
    if not m:
        return 0
    return int(m.group(1)) * 60


def wait_with_countdown(total_seconds: int):
    for remain in range(total_seconds, 0, -1):
        mins = remain // 60
        secs = remain % 60
        print(f"\r[+] Menunggu unblock: {mins:02d}:{secs:02d}", end="", flush=True)
        time.sleep(1)
    print("\r[+] Menunggu unblock: selesai      ")


def login(generator: DeviceHashGenerator) -> str:
    url = f"{BASE_URL}/user/login"
    headers = {
        "Host": "panel.wibuku.app",
        "device_hash": generator.regenerate_token(),
        "user": USER_ID,
        "session": INITIAL_SESSION,
        "device": DEVICE_ID,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded",
    }
    payload = {"version": APP_VERSION}
    res = requests.post(url, headers=headers, data=payload, timeout=20)
    res.raise_for_status()
    body = res.json()
    return body["data"]["user"]["session"]


def fetch_episode_meta(episode_id: int, session: str, generator: DeviceHashGenerator):
    url = f"{BASE_URL}/anime/episodemeta/{episode_id}?mode=0"
    headers = {
        "Host": "panel.wibuku.app",
        "device_hash": generator.regenerate_token(),
        "user": USER_ID,
        "session": session,
        "device": DEVICE_ID,
        "User-Agent": "Mozilla/5.0",
        "Accept-Encoding": "gzip",
    }
    res = requests.post(url, headers=headers, timeout=20)
    res.raise_for_status()
    return res.json()


def load_all_series_from_local_json():
    with open(DETAIL_FILE, "r", encoding="utf-8") as f:
        payload = json.load(f)

    rows = payload.get("data", [])
    series = []
    for row in rows:
        sid = row.get("id")
        data = row.get("data") or {}
        episodes = data.get("episodes", [])
        if sid is None or not isinstance(episodes, list):
            continue
        series.append(
            {
                "series_id": int(sid),
                "title": data.get("title"),
                "title2": data.get("title2"),
                "episodes": episodes,
            }
        )
    return series


def build_sources(raw_sources):
    sources = []
    for s in raw_sources:
        enc_link = s.get("link")
        tipe = s.get("type")
        quality = s.get("quality")
        decoded_link = None
        link_asli = None
        error = None

        try:
            decoded_link = decode_stream_link(enc_link) if enc_link else None
            link_asli = resolve_link(decoded_link, tipe) if decoded_link else None
        except Exception as e:
            error = str(e)

        sources.append(
            {
                "type": tipe,
                "quality": quality,
                "link_encoded": enc_link,
                "decoded_link": decoded_link,
                "link_asli": link_asli,
                "error": error,
            }
        )
    return sources


def scrape_episode(episode_id: int, session: str, generator: DeviceHashGenerator):
    while True:
        body = fetch_episode_meta(episode_id, session, generator)
        if body.get("status") == "banned":
            err = body.get("error", "banned")
            wait_seconds = parse_ban_seconds(err)
            if wait_seconds <= 0:
                raise RuntimeError(err)
            wait_seconds += BAN_WAIT_BUFFER_SECONDS
            print(f"[!] BANNED ep_id={episode_id} | tunggu {wait_seconds} detik")
            wait_with_countdown(wait_seconds)
            session = login(generator)
            print("[+] Login OK (retry setelah ban)")
            continue

        raw_sources = body.get("data", {}).get("stream_sources", [])
        if not isinstance(raw_sources, list):
            raw_sources = []
        return build_sources(raw_sources), session


def scrape_single(series_info, session, generator, output_file, threads=THREADS):
    episodes = series_info["episodes"]
    result = {
        "status": "success",
        "mode": "single",
        "series_id": series_info["series_id"],
        "title": series_info.get("title"),
        "title2": series_info.get("title2"),
        "total_episode": len(episodes),
        "episodes": [],
    }

    print(f"[+] Total episode: {len(episodes)}")
    if threads <= 1:
        for idx, ep in enumerate(episodes, start=1):
            ep_id = ep.get("id")
            ep_name = ep.get("name")
            if ep_id is None:
                continue

            sources, session = scrape_episode(int(ep_id), session, generator)
            result["episodes"].append(
                {
                    "episode_id": int(ep_id),
                    "episode_name": ep_name,
                    "stream_sources": sources,
                }
            )

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"[{idx}/{len(episodes)}] OK ep_id={ep_id} stream_sources={len(sources)}")
            if idx < len(episodes):
                time.sleep(SLEEP_SECONDS)
        return

    print(f"[+] Parallel mode ON, threads={threads}")
    futures = {}
    done = 0
    total = len(episodes)
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for ep in episodes:
            ep_id = ep.get("id")
            ep_name = ep.get("name")
            if ep_id is None:
                continue
            fut = executor.submit(scrape_episode, int(ep_id), session, generator)
            futures[fut] = {"episode_id": int(ep_id), "episode_name": ep_name}

        for fut in as_completed(futures):
            meta = futures[fut]
            sources, _ = fut.result()
            result["episodes"].append(
                {
                    "episode_id": meta["episode_id"],
                    "episode_name": meta["episode_name"],
                    "stream_sources": sources,
                }
            )
            done += 1
            result["episodes"].sort(key=lambda x: x["episode_id"], reverse=True)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"[{done}/{total}] OK ep_id={meta['episode_id']} stream_sources={len(sources)}")


def scrape_all(series_list, session, generator, output_file, threads=THREADS):
    total_series = len(series_list)
    total_episode = sum(len(s.get("episodes", [])) for s in series_list)
    result = {
        "status": "success",
        "mode": "all",
        "total_series": total_series,
        "total_episode": total_episode,
        "series": [],
    }

    done_episode = 0
    print(f"[+] Total series: {total_series} | total episode: {total_episode}")

    for sidx, s in enumerate(series_list, start=1):
        episodes = s.get("episodes", [])
        out_series = {
            "series_id": s["series_id"],
            "title": s.get("title"),
            "title2": s.get("title2"),
            "total_episode": len(episodes),
            "episodes": [],
        }
        print(f"\n[Series {sidx}/{total_series}] id={s['series_id']} eps={len(episodes)}")

        if threads <= 1:
            for eidx, ep in enumerate(episodes, start=1):
                ep_id = ep.get("id")
                ep_name = ep.get("name")
                if ep_id is None:
                    continue

                sources, session = scrape_episode(int(ep_id), session, generator)
                out_series["episodes"].append(
                    {
                        "episode_id": int(ep_id),
                        "episode_name": ep_name,
                        "stream_sources": sources,
                    }
                )
                done_episode += 1
                print(
                    f"[Series {sidx}/{total_series} | Ep {eidx}/{len(episodes)} | Total {done_episode}/{total_episode}] "
                    f"OK ep_id={ep_id} stream_sources={len(sources)}"
                )

                with open(output_file, "w", encoding="utf-8") as f:
                    tmp = dict(result)
                    tmp["series"] = result["series"] + [out_series]
                    json.dump(tmp, f, indent=2, ensure_ascii=False)

                if eidx < len(episodes):
                    time.sleep(SLEEP_SECONDS)
        else:
            print(f"[+] Series {s['series_id']} parallel threads={threads}")
            futures = {}
            with ThreadPoolExecutor(max_workers=threads) as executor:
                for ep in episodes:
                    ep_id = ep.get("id")
                    ep_name = ep.get("name")
                    if ep_id is None:
                        continue
                    fut = executor.submit(scrape_episode, int(ep_id), session, generator)
                    futures[fut] = {"episode_id": int(ep_id), "episode_name": ep_name}

                for fut in as_completed(futures):
                    meta = futures[fut]
                    sources, _ = fut.result()
                    out_series["episodes"].append(
                        {
                            "episode_id": meta["episode_id"],
                            "episode_name": meta["episode_name"],
                            "stream_sources": sources,
                        }
                    )
                    done_episode += 1
                    print(
                        f"[Series {sidx}/{total_series} | Total {done_episode}/{total_episode}] "
                        f"OK ep_id={meta['episode_id']} stream_sources={len(sources)}"
                    )
                    out_series["episodes"].sort(key=lambda x: x["episode_id"], reverse=True)
                    with open(output_file, "w", encoding="utf-8") as f:
                        tmp = dict(result)
                        tmp["series"] = result["series"] + [out_series]
                        json.dump(tmp, f, indent=2, ensure_ascii=False)

        result["series"].append(out_series)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Scrape episode stream sources")
    parser.add_argument("series_id", nargs="?", type=int, help="Series ID untuk mode single")
    parser.add_argument("--all", action="store_true", help="Scrape semua series dari seires_animedetail.json")
    parser.add_argument("--threads", type=int, default=THREADS, help="Jumlah thread paralel (default: 15)")
    parser.add_argument("-o", "--output", default=None, help="Output file JSON")
    args = parser.parse_args()

    if args.all and args.series_id is not None:
        raise SystemExit("Pakai salah satu: series_id (single) atau --all")
    if not args.all and args.series_id is None:
        raise SystemExit("Masukkan series_id atau pakai --all")

    series_list = load_all_series_from_local_json()
    index = {s["series_id"]: s for s in series_list}

    generator = DeviceHashGenerator(OLD_HASH)
    session = login(generator)
    print("[+] Login OK")

    if args.all:
        output_file = args.output or "all_series_episode_links.json"
        scrape_all(series_list, session, generator, output_file, threads=max(1, args.threads))
    else:
        if args.series_id not in index:
            raise SystemExit(f"Series id {args.series_id} tidak ditemukan di {DETAIL_FILE}")
        output_file = args.output or f"single_series_{args.series_id}_episodes.json"
        scrape_single(index[args.series_id], session, generator, output_file, threads=max(1, args.threads))

    print(f"[+] Saved: {output_file}")


if __name__ == "__main__":
    main()
