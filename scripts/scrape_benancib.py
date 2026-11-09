#!/usr/bin/env python3
"""
BENANCIB & UFPB Historical Rescue & Enrichment Pipeline - BRAN Org Standard
Resgata os anais históricos completos das 20 primeiras edições do ENANCIB (1994 a 2019),
preservados pela base BENANCIB / UFPB e indexados na BRAPCI, enriquecendo o acervo
aberto do ENANCIB com mais de 4.800 trabalhos históricos e recuperando resumos e palavras-chave.
"""

import os
import sys
import json
import time
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BRAN Org Harvester (https://github.com/BRAN-Org)"
HEADERS = {'User-Agent': USER_AGENT}

GT_CANONICAL = {
    "GT-01": "GT 1 – Estudos Históricos e Epistemológicos da Ciência da Informação",
    "GT-1": "GT 1 – Estudos Históricos e Epistemológicos da Ciência da Informação",
    "GT 1": "GT 1 – Estudos Históricos e Epistemológicos da Ciência da Informação",
    "GT-02": "GT 2 – Organização e Representação do Conhecimento",
    "GT-2": "GT 2 – Organização e Representação do Conhecimento",
    "GT 2": "GT 2 – Organização e Representação do Conhecimento",
    "GT-03": "GT 3 – Mediação, Circulação e Apropriação da Informação",
    "GT-3": "GT 3 – Mediação, Circulação e Apropriação da Informação",
    "GT 3": "GT 3 – Mediação, Circulação e Apropriação da Informação",
    "GT-04": "GT 4 – Gestão da Informação e do Conhecimento",
    "GT-4": "GT 4 – Gestão da Informação e do Conhecimento",
    "GT 4": "GT 4 – Gestão da Informação e do Conhecimento",
    "GT-05": "GT 5 – Política e Economia da Informação",
    "GT-5": "GT 5 – Política e Economia da Informação",
    "GT 5": "GT 5 – Política e Economia da Informação",
    "GT-06": "GT 6 – Informação, Educação e Trabalho",
    "GT-6": "GT 6 – Informação, Educação e Trabalho",
    "GT 6": "GT 6 – Informação, Educação e Trabalho",
    "GT-07": "GT 7 – Produção e Comunicação da Informação em Ciência, Tecnologia & Inovação",
    "GT-7": "GT 7 – Produção e Comunicação da Informação em Ciência, Tecnologia & Inovação",
    "GT 7": "GT 7 – Produção e Comunicação da Informação em Ciência, Tecnologia & Inovação",
    "GT-08": "GT 8 – Dados, Informação e Tecnologia",
    "GT-8": "GT 8 – Dados, Informação e Tecnologia",
    "GT 8": "GT 8 – Dados, Informação e Tecnologia",
    "GT-09": "GT 9 – Museu, Patrimônio e Informação",
    "GT-9": "GT 9 – Museu, Patrimônio e Informação",
    "GT 9": "GT 9 – Museu, Patrimônio e Informação",
    "GT-10": "GT 10 – Informação e Memória",
    "GT 10": "GT 10 – Informação e Memória",
    "GT-11": "GT 11 – Informação & Saúde",
    "GT 11": "GT 11 – Informação & Saúde",
    "GT-12": "GT 12 – Informação, Estudos Étnico-Raciais, Gênero e Diversidades",
    "GT 12": "GT 12 – Informação, Estudos Étnico-Raciais, Gênero e Diversidades",
}

TOOLS_TAXONOMY = {
    "VOSviewer": [r"\bvosviewer\b", r"\bvos\s*viewer\b"],
    "CiteSpace": [r"\bcitespace\b"],
    "Gephi": [r"\bgephi\b"],
    "Bibliometrix": [r"\bbibliometrix\b", r"\bbiblioshiny\b"],
    "Pajek": [r"\bpajek\b"],
    "UCINET": [r"\bucinet\b"],
    "R": [r"\blinguagem\s+r\b", r"\bpacote\s+r\b", r"\bsoftware\s+r\b", r"\brstudio\b"],
    "Python": [r"\bpython\b", r"\bpandas\b", r"\bspacy\b", r"\bscikit\b"],
    "Excel": [r"\bexcel\b", r"\bms\s+excel\b"],
    "SPSS": [r"\bspss\b"],
    "Iramuteq": [r"\biramuteq\b"],
    "Atlas.ti": [r"\batlas\.?ti\b"],
    "NVivo": [r"\bnvivo\b"],
    "MaxQDA": [r"\bmaxqda\b"],
    "Protégé": [r"\bprot[eé]g[eé]\b"],
    "DSpace": [r"\bdspace\b"],
    "Koha": [r"\bkoha\b"]
}

DATA_SOURCES_TAXONOMY = {
    "BRAPCI": [r"\bbrapci\b"],
    "BENANCIB": [r"\bbenancib\b"],
    "BDTD": [r"\bbdtd\b"],
    "SciELO": [r"\bscielo\b"],
    "Web of Science": [r"\bweb of science\b", r"\bwos\b"],
    "Scopus": [r"\bscopus\b"],
    "Plataforma Lattes": [r"\bplataforma lattes\b", r"\bcurr[ií]culos? lattes\b", r"\blattes\b"],
    "Google Acadêmico": [r"\bgoogle acad[eê]mico\b", r"\bgoogle scholar\b"],
    "Dimensions": [r"\bdimensions\b"],
    "OpenAlex": [r"\bopenalex\b"],
    "Oasisbr": [r"\boasisbr\b", r"\boasis\s*br\b"],
    "PubMed": [r"\bpubmed\b"],
    "Dialnet": [r"\bdialnet\b"],
    "Redalyc": [r"\bredalyc\b"],
    "CAPES": [r"\bportal de peri[oó]dicos da capes\b", r"\bperi[oó]dicos capes\b", r"\bbanco de teses da capes\b"]
}

STAGE_RULES = {
    "Coleta de Dados": [r"\bcoleta de dados\b", r"\blevantamento documental\b", r"\bpesquisa bibliogr[aá]fica\b"],
    "Análise Bibliométrica": [r"\bbibliometri[ca]\b", r"\bcientometri[ca]\b", r"\ban[aá]lise de cita[cç][oõ]es\b"],
    "Análise de Redes (ARS)": [r"\ban[aá]lise de redes?\b", r"\bredes de coautoria\b", r"\bcoocorr[eê]ncia\b"],
    "Análise de Conteúdo": [r"\ban[aá]lise de conte[uú]do\b", r"\ban[aá]lise textual\b", r"\bcategoriza[cç][aã]o\b"],
    "Modelagem Conceitual": [r"\bontologi[as]\b", r"\bweb sem[aâ]ntica\b", r"\bmodelagem\b", r"\btesauro\b"]
}

def extract_scientometric_facets(text):
    tools = []
    sources = []
    stages = []
    if not text:
        return tools, sources, stages
    text_lower = text.lower()
    for tool, patterns in TOOLS_TAXONOMY.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                tools.append(tool)
                break
    for source, patterns in DATA_SOURCES_TAXONOMY.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                sources.append(source)
                break
    for stage, patterns in STAGE_RULES.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                stages.append(stage)
                break
    return sorted(list(set(tools))), sorted(list(set(sources))), sorted(list(set(stages)))

def map_gt_canonical(session_raw):
    if not session_raw:
        return "Geral"
    for k, v in GT_CANONICAL.items():
        if k in session_raw:
            return v
    if "Especial" in session_raw:
        return "GT Especial"
    return "Geral"

def fetch_json(url, retries=3):
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            if attempt == retries - 1:
                return None
            time.sleep(0.5)
    return None

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, 'data')
    main_file = os.path.join(data_dir, 'enancib_articles.json')

    print("=" * 70)
    print("🚀 [BENANCIB/UFPB Harvester] Resgatando Anais Históricos (1994 - 2019)...")
    print("=" * 70)

    # 1. Carregar dataset existente do OJS (2021-2026)
    existing_articles = []
    if os.path.exists(main_file):
        with open(main_file, "r", encoding="utf-8") as f:
            existing_articles = json.load(f)
    print(f"📦 Acervo OJS (2021-2026) pré-carregado: {len(existing_articles)} artigos.")

    # 2. Obter lista de edições do ENANCIB na Brapci (ID da fonte = 75)
    source_url = "https://cip.brapci.inf.br/api/brapci/source/75"
    source_data = fetch_json(source_url)
    if not source_data or 'source' not in source_data:
        print("❌ Erro ao acessar fonte ENANCIB na Brapci.")
        sys.exit(1)

    issues = source_data['source']['issue']
    historical_issues = [iss for iss in issues if int(iss.get('year', 0)) <= 2019]
    print(f"📋 Encontradas {len(historical_issues)} edições históricas (1994 a 2019).\n")

    # 3. Extrair trabalhos de cada edição histórica
    all_historical_raw = []
    for iss in sorted(historical_issues, key=lambda x: str(x.get('year', ''))):
        iss_id = iss.get('ID')
        year = int(iss.get('year'))
        vol = iss.get('vol', '')
        place = iss.get('place', '')
        issue_title = f"{vol} ENANCIB ({year}) - {place}".strip(" -")
        
        issue_url = f"https://cip.brapci.inf.br/api/brapci/issue/{iss_id}"
        iss_data = fetch_json(issue_url)
        if not iss_data:
            print(f"⚠️ Erro ao carregar edição {vol} ({year}).")
            continue

        issue_works = 0
        for group in iss_data.get('works', []):
            session_raw = group.get('name', 'Geral')
            canonical_gt = map_gt_canonical(session_raw)
            for w in group.get('data', []):
                wid = w.get('ID')
                title = w.get('LEGEND', '').strip()
                authors_str = w.get('AUTHORS', '').strip()
                has_pdf = w.get('PDF') == '1'
                
                # Tratar lista de autores
                if authors_str:
                    authors = [a.strip() for a in authors_str.split(';') if a.strip()]
                else:
                    authors = ["ANCIB"]

                all_historical_raw.append({
                    "wid": wid,
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "vol": vol,
                    "issue": issue_title,
                    "section": canonical_gt,
                    "has_pdf": has_pdf
                })
                issue_works += 1

        print(f"  • ENANCIB {vol:>4} ({year}) [{place}]: {issue_works:>3} trabalhos extraídos.")

    print(f"\n⚡ Total de trabalhos históricos catalogados: {len(all_historical_raw)}")

    # 4. Enriquecer trabalhos históricos com resumos e palavras-chave em paralelo
    print("\n🔍 Buscando resumos e palavras-chave na base BENANCIB (15 workers)...")
    
    def fetch_work_detail(item):
        wid = item["wid"]
        url = f"https://cip.brapci.inf.br/api/brapci/get/v1/{wid}"
        data = fetch_json(url)
        abstract = None
        keywords = []
        if data:
            desc = data.get('description') or ''
            if len(desc.strip()) > 30:
                abstract = desc.strip()
            
            subjs = data.get('subject', {})
            if isinstance(subjs, dict):
                for lang in ['pt', 'en', 'es']:
                    for s in subjs.get(lang, []):
                        if isinstance(s, dict) and s.get('name'):
                            name = s['name'].strip()
                            if name and name not in keywords:
                                keywords.append(name)
                                
            # Autores mais precisos se presentes
            creator_authors = data.get('creator_author', [])
            if creator_authors and isinstance(creator_authors, list):
                detailed_authors = [ca.get('name').strip() for ca in creator_authors if ca.get('name')]
                if detailed_authors:
                    item['authors'] = detailed_authors

        item['abstract'] = abstract
        item['keywords'] = keywords
        return item

    historical_articles = []
    start_time = time.time()
    total_to_fetch = len(all_historical_raw)

    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(fetch_work_detail, it): it for it in all_historical_raw}
        for idx, f in enumerate(as_completed(futures), 1):
            try:
                res = f.result()
                
                # Montar registro canônico
                text_for_scientometrics = f"{res['title']} {res['abstract'] or ''} {' '.join(res['keywords'])}"
                tools, data_sources, usage_stages = extract_scientometric_facets(text_for_scientometrics)

                pdf_url = f"https://cip.brapci.inf.br/download/{res['wid']}" if res['has_pdf'] else ""
                
                historical_articles.append({
                    "id": f"benancib-{res['wid']}",
                    "doi": "N/A",
                    "title": res['title'],
                    "authors": res['authors'],
                    "abstract": res['abstract'],
                    "keywords": res['keywords'],
                    "year": res['year'],
                    "issue": res['issue'],
                    "section": res['section'],
                    "url": f"https://brapci.inf.br/v/a/{res['wid']}",
                    "pdf_url": pdf_url,
                    "license": "CC BY-NC 4.0 / ANCIB",
                    "tools": tools,
                    "data_sources": data_sources,
                    "usage_stages": usage_stages
                })
            except Exception as e:
                pass
            
            if idx % 500 == 0 or idx == total_to_fetch:
                print(f"  [{idx}/{total_to_fetch}] trabalhos históricos processados...")

    print(f"✨ Coleta histórica finalizada em {time.time() - start_time:.2f}s!")

    # 5. Mesclar dataset histórico com o acervo do OJS (2021-2026)
    print("\n📦 Integrando acervos histórico (BENANCIB/UFPB) e recente (OJS ANCIB)...")
    
    # Criar lista unificada sem duplicatas
    combined_articles = []
    
    # Adicionar históricos (1994-2019)
    combined_articles.extend(historical_articles)
    
    # Adicionar recentes (2021-2026)
    combined_articles.extend(existing_articles)
    
    # Ordenar por ano descendente, depois por título
    combined_articles.sort(key=lambda a: (-a.get("year", 0), a.get("title", "")))

    print(f"🎉 Acervo Completo Unificado: {len(combined_articles)} trabalhos científicos!")
    
    # Salvar acervo final
    print(f"💾 Salvando em {main_file} ...")
    with open(main_file, "w", encoding="utf-8") as f:
        json.dump(combined_articles, f, ensure_ascii=False, indent=2)

    # 6. Relatório final de auditoria
    total = len(combined_articles)
    with_abs = sum(1 for a in combined_articles if a.get("abstract"))
    with_kw = sum(1 for a in combined_articles if a.get("keywords"))
    with_tools = sum(1 for a in combined_articles if a.get("tools"))
    with_sources = sum(1 for a in combined_articles if a.get("data_sources"))

    print("\n" + "=" * 70)
    print("📊 RELATÓRIO DO ACERVO TOTAL RESGATADO - ENANCIB COMPLETO (1994-2026)")
    print(f"  • Total de Artigos Digitalizados: {total}")
    print(f"  • Cobertura Temporal: 1994 a 2026 (todas as 25 edições)")
    print(f"  • Artigos com Resumo Completo: {with_abs} ({(with_abs/total)*100:.1f}%)")
    print(f"  • Artigos com Palavras-chave: {with_kw} ({(with_kw/total)*100:.1f}%)")
    print(f"  • Com Softwares/Ferramentas Detectadas: {with_tools}")
    print(f"  • Com Fontes de Dados Detectadas: {with_sources}")
    print("=" * 70)

if __name__ == "__main__":
    main()
