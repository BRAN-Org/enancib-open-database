#!/usr/bin/env python3
"""
BRAN Org - ENANCIB Full PDF Corpus Harvester
Downloads all full-text PDFs from:
- BENANCIB / Brapci (1994–2019): ~4,828 historical articles
- OJS ANCIB (2021–2026): ~2,162 recent articles
"""

import os
import sys
import json
import time
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "enancib_articles.json")
OUT_DIR = os.path.join(BASE_DIR, "data", "pdfs")
os.makedirs(OUT_DIR, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 BRAN Org Harvester"
HEADERS = {"User-Agent": USER_AGENT}

def download_single(item):
    pdf_url = item.get("pdf_url")
    if not pdf_url:
        return item["id"], False, "Sem URL de PDF"

    art_id = re.sub(r"[^a-zA-Z0-9_-]", "_", str(item["id"]))
    year = str(item.get("year", "sem_ano"))
    year_dir = os.path.join(OUT_DIR, year)
    os.makedirs(year_dir, exist_ok=True)

    dest_file = os.path.join(year_dir, f"{art_id}.pdf")
    if os.path.exists(dest_file) and os.path.getsize(dest_file) > 1024:
        return item["id"], True, "Cache"

    # Normalize OJS URL
    if "enancib.ancib.org" in pdf_url:
        url = pdf_url.replace("/view/", "/download/")
    else:
        url = pdf_url

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = resp.read()
                if len(data) > 1000:
                    with open(dest_file, "wb") as f:
                        f.write(data)
                    return item["id"], True, "OK"
        except Exception as e:
            time.sleep(1.5 * (attempt + 1))
            continue
    return item["id"], False, "Falha"

def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)

    brapci_items = [x for x in items if "brapci" in x.get("pdf_url", "")]
    ancib_items = [x for x in items if "enancib.ancib" in x.get("pdf_url", "")]

    print(f"Total de registros ENANCIB: {len(items)}")
    print(f"  • Brapci / BENANCIB (1994–2019): {len(brapci_items)} PDFs")
    print(f"  • OJS ANCIB (2021–2026): {len(ancib_items)} PDFs")
    print(f"Diretório de destino: {OUT_DIR}")

    # 1. Download Brapci with 12 workers (fast)
    print("\n🚀 Iniciando download do acervo BENANCIB/Brapci (12 workers)...")
    b_success = 0
    b_fail = 0
    start_b = time.time()
    with ThreadPoolExecutor(max_workers=12) as ex:
        futures = {ex.submit(download_single, it): it for it in brapci_items}
        for idx, f in enumerate(as_completed(futures), 1):
            aid, ok, msg = f.result()
            if ok:
                b_success += 1
            else:
                b_fail += 1
            if idx % 200 == 0 or idx == len(brapci_items):
                rate = idx / (time.time() - start_b)
                print(f"  [Brapci {idx}/{len(brapci_items)}] Sucesso: {b_success}, Falhas: {b_fail} ({rate:.1f} PDFs/s)")

    # 2. Download ANCIB with 4 workers (gentle)
    print("\n🚀 Iniciando download do acervo OJS ANCIB (4 workers)...")
    a_success = 0
    a_fail = 0
    start_a = time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(download_single, it): it for it in ancib_items}
        for idx, f in enumerate(as_completed(futures), 1):
            aid, ok, msg = f.result()
            if ok:
                a_success += 1
            else:
                a_fail += 1
            if idx % 100 == 0 or idx == len(ancib_items):
                rate = idx / (time.time() - start_a)
                print(f"  [ANCIB {idx}/{len(ancib_items)}] Sucesso: {a_success}, Falhas: {a_fail} ({rate:.1f} PDFs/s)")

    total_files = sum(len(files) for _, _, files in os.walk(OUT_DIR))
    print("\n" + "="*50)
    print(f"✅ Concluído! Total de PDFs baixados no disco: {total_files}")
    print("="*50)

if __name__ == "__main__":
    main()
