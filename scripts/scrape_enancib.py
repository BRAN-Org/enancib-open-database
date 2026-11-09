#!/usr/bin/env python3
"""
ENANCIB Harvester & Scientometric Pipeline - BRAN Org Standard
Script de extração, auditoria e curadoria metodológica dos anais do
Encontro Nacional de Pesquisa e Pós-Graduação em Ciência da Informação (ENANCIB).

Extrai metadados completos (título, autores, ano, resumo, palavras-chave, GTs, URLs e PDFs)
via protocolo aberto OAI-PMH e aplica taxonomia cientométrica para identificar
ferramentas metodológicas e fontes de dados utilizadas nas pesquisas.
"""

import os
import sys
import json
import time
import re
import urllib.request
import xml.etree.ElementTree as ET

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

OAI_BASE_URL = "https://enancib.ancib.org/enancib/pt_BR/oai"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BRAN Org Harvester (https://github.com/BRAN-Org)"
HEADERS = {'User-Agent': USER_AGENT}

# Dicionários de taxonomia cientométrica
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

def fetch_xml(url, retries=5, delay=1.0):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=40) as resp:
                return resp.read()
        except Exception as e:
            if attempt == retries - 1:
                print(f"❌ Erro ao acessar {url}: {e}")
                raise
            time.sleep(delay * (attempt + 1))

def normalize_author(raw_author):
    if not raw_author:
        return ""
    author = raw_author.strip()
    author = re.sub(r'<[^>]+>', '', author)
    author = re.sub(r'\s+', ' ', author)
    if ',' in author:
        parts = [p.strip() for p in author.split(',', 1)]
        if len(parts) == 2 and parts[1]:
            author = f"{parts[1]} {parts[0]}"
    return author

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

def harvest_enancib():
    print("🚀 [BRAN Harvester] Conectando ao repositório OAI-PMH do ENANCIB...")
    print(f"🔗 Endpoint: {OAI_BASE_URL}\n")
    
    # 1. Recuperar mapeamento dos Grupos de Trabalho (Sets)
    sets_xml = fetch_xml(f"{OAI_BASE_URL}?verb=ListSets")
    tree_sets = ET.fromstring(sets_xml)
    ns = {
        'o': 'http://www.openarchives.org/OAI/2.0/',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }
    
    set_map = {}
    for s in tree_sets.findall('.//o:set', ns):
        spec_elem = s.find('o:setSpec', ns)
        name_elem = s.find('o:setName', ns)
        if spec_elem is not None and name_elem is not None:
            spec = spec_elem.text.strip()
            name = name_elem.text.strip()
            set_map[spec] = name
            
    print(f"📋 {len(set_map)} Conjuntos / GTs identificados.")
    
    # 2. Iterar sobre todos os registros via ListRecords & resumptionToken
    url = f"{OAI_BASE_URL}?verb=ListRecords&metadataPrefix=oai_dc"
    batch_num = 0
    raw_articles = []
    
    start_time = time.time()
    
    while url:
        batch_num += 1
        raw_xml = fetch_xml(url)
        tree = ET.fromstring(raw_xml)
        records = tree.findall('.//o:record', ns)
        
        for r in records:
            header = r.find('o:header', ns)
            if header is None or header.get('status') == 'deleted':
                continue
                
            ident_elem = header.find('o:identifier', ns)
            ident = ident_elem.text.strip() if ident_elem is not None else ""
            
            # Extrair id numérico
            id_match = re.search(r'article/(\d+)', ident)
            numeric_id = id_match.group(1) if id_match else ident.split(':')[-1]
            
            # Identificar Grupo de Trabalho (GT)
            specs = [s.text.strip() for s in header.findall('o:setSpec', ns) if s.text]
            gt_spec = next((s for s in specs if 'GT' in s), None)
            if not gt_spec:
                gt_spec = next((s for s in specs if s != 'enancib' and s != 'enancib:ART'), 'enancib:ART')
            section = set_map.get(gt_spec, gt_spec)
            
            # Metadados Dublin Core
            metadata = r.find('o:metadata', ns)
            if metadata is None:
                continue
                
            title_elem = metadata.find('.//dc:title', ns)
            title = title_elem.text.strip() if (title_elem is not None and title_elem.text) else ""
            if not title:
                continue
            
            # Limpar título
            title = re.sub(r'\s+', ' ', title).strip()
            
            # Autores
            authors = []
            for creator in metadata.findall('.//dc:creator', ns):
                if creator.text:
                    norm = normalize_author(creator.text)
                    if norm and norm not in authors:
                        authors.append(norm)
            if not authors:
                authors = ["ANCIB"]
                
            # Resumo
            abstract_elem = metadata.find('.//dc:description', ns)
            abstract = abstract_elem.text.strip() if (abstract_elem is not None and abstract_elem.text) else ""
            abstract = re.sub(r'\s+', ' ', abstract).strip()
            
            # Palavras-chave
            keywords = []
            for subj in metadata.findall('.//dc:subject', ns):
                if subj.text:
                    parts = re.split(r'[;,\.\n]+', subj.text)
                    for p in parts:
                        cleaned = p.strip()
                        if cleaned and len(cleaned) > 2 and cleaned not in keywords:
                            keywords.append(cleaned)
                            
            # Identificadores e Links
            identifiers = [i.text.strip() for i in metadata.findall('.//dc:identifier', ns) if i.text]
            relations = [rel.text.strip() for rel in metadata.findall('.//dc:relation', ns) if rel.text]
            
            article_url = next((i for i in identifiers if '/article/view/' in i), f"https://enancib.ancib.org/enancib/article/view/{numeric_id}")
            pdf_url = next((rel for rel in relations if '/article/view/' in rel or '/article/download/' in rel), f"https://enancib.ancib.org/enancib/article/download/{numeric_id}/{numeric_id}")
            doi_candidate = next((i for i in identifiers if '10.' in i or 'doi.org' in i), "N/A")
            
            # Data / Ano
            dates = [d.text.strip() for d in metadata.findall('.//dc:date', ns) if d.text]
            sources = [src.text.strip() for src in metadata.findall('.//dc:source', ns) if src.text]
            
            issue_title = "Encontro Nacional de Pesquisa em Ciência da Informação (ENANCIB)"
            year = None
            
            for src in sources:
                if 'enancib' in src.lower():
                    src_clean = re.sub(r'\s+', ' ', src).strip()
                    m_year = re.search(r'\((\d{4})\)', src_clean) or re.search(r'\b(20\d\d)\b', src_clean)
                    if m_year:
                        year = int(m_year.group(1))
                    if ':' in src_clean:
                        issue_title = src_clean.split(':', 1)[1].strip()
                    else:
                        issue_title = src_clean
                    break
                    
            if not year and dates:
                m_year = re.search(r'\b(20\d\d)\b', dates[0])
                if m_year:
                    year = int(m_year.group(1))
                    
            if not year:
                year = 2024
                
            # Enriquecimento cientométrico
            full_searchable_text = f"{title} {abstract} {' '.join(keywords)}"
            tools, data_sources, usage_stages = extract_scientometric_facets(full_searchable_text)
            
            raw_articles.append({
                "id": str(numeric_id),
                "doi": doi_candidate,
                "title": title,
                "authors": authors,
                "abstract": abstract if abstract else None,
                "keywords": keywords,
                "year": year,
                "issue": issue_title,
                "section": section,
                "url": article_url,
                "pdf_url": pdf_url,
                "license": "CC BY-NC 4.0",
                "tools": tools,
                "data_sources": data_sources,
                "usage_stages": usage_stages
            })
            
        print(f"📦 Lote {batch_num}: {len(raw_articles)} artigos processados até agora...")
        
        resumption = tree.find('.//o:resumptionToken', ns)
        if resumption is not None and resumption.text:
            token = resumption.text.strip()
            url = f"{OAI_BASE_URL}?verb=ListRecords&resumptionToken={token}"
            time.sleep(0.3)
        else:
            url = None

    elapsed = time.time() - start_time
    print(f"\n⚡ Coleta finalizada em {elapsed:.2f} segundos!")
    print(f"📊 Total de registros coletados: {len(raw_articles)}")
    
    # Ordenar por ano descendente, depois por título
    raw_articles.sort(key=lambda a: (-a.get("year", 0), a.get("title", "")))
    
    return raw_articles

def audit_dataset_integrity(articles):
    total = len(articles)
    with_doi = sum(1 for a in articles if a.get("doi") and a.get("doi") != "N/A")
    with_abstract = sum(1 for a in articles if a.get("abstract"))
    with_keywords = sum(1 for a in articles if a.get("keywords") and len(a["keywords"]) > 0)
    with_tools = sum(1 for a in articles if a.get("tools") and len(a["tools"]) > 0)
    with_sources = sum(1 for a in articles if a.get("data_sources") and len(a["data_sources"]) > 0)
    
    years = {}
    for a in articles:
        y = a.get("year", "N/A")
        years[y] = years.get(y, 0) + 1
        
    gts = {}
    for a in articles:
        gt = a.get("section", "N/A")
        gts[gt] = gts.get(gt, 0) + 1

    print("=" * 65)
    print("📊 RELATÓRIO DE AUDITORIA DE INTEGRIDADE - ENANCIB")
    print(f"  • Total de Artigos Digitalizados: {total}")
    print(f"  • Com Resumo Completo: {with_abstract} ({(with_abstract/total)*100:.1f}%)")
    print(f"  • Com Palavras-chave Estruturadas: {with_keywords} ({(with_keywords/total)*100:.1f}%)")
    print(f"  • Com Softwares / Ferramentas Detectadas: {with_tools} ({(with_tools/total)*100:.1f}%)")
    print(f"  • Com Fontes de Dados Detectadas: {with_sources} ({(with_sources/total)*100:.1f}%)")
    print(f"  • Com DOI Registrado: {with_doi}")
    print("\n📅 Distribuição por Ano:")
    for y in sorted(years.keys()):
        print(f"    - {y}: {years[y]} artigos")
    print("\n🏛️ Grupos de Trabalho (GTs):")
    for gt, count in sorted(gts.items(), key=lambda x: -x[1]):
        print(f"    - {gt}: {count} artigos")
    print("=" * 65)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    articles = harvest_enancib()
    audit_dataset_integrity(articles)
    
    output_path = os.path.join(data_dir, 'enancib_articles.json')
    print(f"\n💾 Gravando acervo em: {output_path} ...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Acervo ENANCIB com {len(articles)} artigos salvo com sucesso!")

if __name__ == '__main__':
    main()
