#!/usr/bin/env python3
"""
ENANCIB PDF Corpus Downloader
Script opcional para pesquisadores que desejam baixar os PDFs de texto completo
dos artigos do ENANCIB para mineracao de texto e analise de PLN offline.
"""

import os
import sys
import json
import time
import argparse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BRAN Org PDF Harvester"
HEADERS = {'User-Agent': USER_AGENT}

def download_single_pdf(item, output_dir, timeout=30):
    pdf_url = item.get('pdf_url')
    if not pdf_url:
        return item['id'], False, "Sem URL de PDF"
    
    art_id = item['id'].replace('/', '_').replace(':', '_')
    year = str(item.get('year', 'sem_ano'))
    year_dir = os.path.join(output_dir, year)
    os.makedirs(year_dir, exist_ok=True)
    
    file_path = os.path.join(year_dir, f"{art_id}.pdf")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 1024:
        return item['id'], True, "Já existente"
    
    req = urllib.request.Request(pdf_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            if len(data) < 1000:
                return item['id'], False, "Arquivo vazio ou inválido"
            with open(file_path, 'wb') as f:
                f.write(data)
        return item['id'], True, "Baixado com sucesso"
    except Exception as e:
        return item['id'], False, str(e)

def main():
    parser = argparse.ArgumentParser(description="Download em lote de PDFs do acervo ENANCIB")
    parser.add_argument("--year", type=int, help="Filtrar por ano específico (ex: 2023)")
    parser.add_argument("--workers", type=int, default=5, help="Número de threads simultâneas (default: 5)")
    parser.add_argument("--limit", type=int, default=None, help="Limite máximo de PDFs para baixar")
    parser.add_argument("--output", default="data/pdfs", help="Diretório de destino (default: data/pdfs)")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(project_root, "data", "enancib_articles.json")
    out_dir = os.path.join(project_root, args.output)

    if not os.path.exists(data_file):
        print(f"❌ Arquivo não encontrado: {data_file}")
        sys.exit(1)

    with open(data_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    if args.year:
        articles = [a for a in articles if a.get('year') == args.year]

    to_download = [a for a in articles if a.get('pdf_url')]
    if args.limit:
        to_download = to_download[:args.limit]

    print("=" * 60)
    print(f"📥 [ENANCIB PDF Downloader]")
    print(f"  • Total de PDFs a verificar/baixar: {len(to_download)}")
    print(f"  • Destino local: {out_dir}")
    print(f"  • Threads simultâneas: {args.workers}")
    print("=" * 60)

    os.makedirs(out_dir, exist_ok=True)
    success = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(download_single_pdf, art, out_dir): art for art in to_download}
        for idx, fut in enumerate(as_completed(futures), 1):
            art_id, ok, msg = fut.result()
            if ok:
                success += 1
            else:
                failed += 1
            if idx % 100 == 0 or idx == len(to_download):
                print(f"  [{idx}/{len(to_download)}] Sucessos: {success} | Falhas/Ignorados: {failed}")

    print("\n✅ Concluído!")
    print(f"  • Baixados com sucesso: {success}")
    print(f"  • Falhas: {failed}")

if __name__ == "__main__":
    main()
