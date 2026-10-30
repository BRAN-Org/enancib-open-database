# ENANCIB Open Database

<p align="center">
  <a href="https://doi.org/10.5281/zenodo.23593583"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.23593583.svg" alt="Zenodo DOI"></a>
  <a href="#-síntese-do-acervo--governança"><img src="https://img.shields.io/badge/Confiabilidade-Auditado%20e%20Validado-brightgreen" alt="Confiabilidade"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/Licen%C3%A7a-CC_BY--NC--SA_4.0-lightgrey.svg" alt="CC BY-NC-SA 4.0"></a>
  <a href="#-como-usar-os-dados"><img src="https://img.shields.io/badge/Formatos-SQLite_%7C_CSV_%7C_JSON-blue.svg" alt="Formatos"></a>
</p>

Base de dados bibliométrica aberta e acervo histórico completo dos 6.998 trabalhos científicos apresentados nos anais das 25 edições do Encontro Nacional de Pesquisa e Pós-Graduação em Ciência da Informação (ENANCIB, 1994–2026), principal conferência de Ciência da Informação no Brasil, disponibilizado pela BRAN Org sob princípios FAIR e BOAI.

---

## 📊 Síntese do Acervo & Governança

> [!NOTE]
> **Status de Confiabilidade:** 🟢 **Auditado e Validado**  
> 📌 **Diagnóstico Metodológico:** Acervo exaustivo cobrindo todas as 25 edições históricas do ENANCIB (1994–2026). Todos os 6.998 artigos científicos foram catalogados com integridade criptográfica SHA-256 individual, 6.965 textos completos em PDF preservados localmente (3,49 GB) com conferência direta contra os anais originais, 96,7% de cobertura de resumos e mapeamento canônico dos 12 Grupos de Trabalho (GT 1 ao GT 12).

| Métrica / Atributo | Detalhes do Acervo |
| :--- | :--- |
| **Período Histórico** | 1994–2026 (25 Edições Históricas) |
| **Total de Trabalhos** | **6.998 artigos científicos catalogados** |
| **Textos Completos (PDF)** | 6.965 artigos com texto completo em PDF preservado (3,49 GB) |
| **Integridade Criptográfica** | Hash SHA-256 por arquivo e rastreabilidade estrita (`provenance.json`) |
| **Formatos Disponíveis** | SQLite3 (`.sqlite`), CSV (UTF-8 BOM), JSON, BibTeX (`.bib`), RIS (`.ris`) |
| **Licença dos Dados** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (Uso acadêmico; vedada ingestão por IA comercial) |

---

## 📥 Download do Pacote Consolidado

O acervo bruto, o banco relacional completo e os arquivos individuais estão arquivados permanentemente no **CERN / Zenodo** sob DOI imutável:

- 🔗 **DOI Permanente:** [https://doi.org/10.5281/zenodo.23593583](https://doi.org/10.5281/zenodo.23593583)
- 📦 **Conteúdo do .zip:** Banco SQLite3 (`enancib_articles.sqlite`), planilhas CSV consolidadas (`enancib_articles.csv`), metadados estruturados JSON, referências BibTeX/RIS e coleção completa de PDFs em texto completo.

```bash
# Download direto do pacote completo via terminal
curl -LO "https://zenodo.org/records/23593583/files/enancib-open-database-zenodo.zip"
unzip enancib-open-database-zenodo.zip
```

---

## ⚡ Como Usar os Dados

### Python (Pandas)
```python
import pandas as pd

df = pd.read_json("data/enancib_articles.json")
print(f"Total: {len(df)} artigos | Período: {df['year'].min()} a {df['year'].max()}")
```

### SQLite3 (SQL no terminal)
```bash
sqlite3 data/enancib_articles.sqlite "SELECT year, COUNT(*) as total FROM articles GROUP BY year ORDER BY year;"
```

---

## 🌐 API REST Pública

Endpoints públicos e gratuitos (sem necessidade de chave de autenticação):

| Método | Endpoint | Finalidade |
| :--- | :--- | :--- |
| `GET` | `/api/v1/articles` | Busca textual (`?q=`), filtros facetados (`?year=`, `?author=`) e paginação |
| `GET` | `/api/v1/articles/:key` | Consulta individual por ID ou DOI |
| `GET` | `/api/v1/articles/stats` | Métricas consolidadas, rankings de autores e palavras-chave |
| `GET` | `/api/v1/articles/export?format=csv` | Download instantâneo dos dados filtrados em CSV (BOM UTF-8) |

> **Executar localmente:** `npm install && npm start` (disponível em `http://localhost:3000`).

---

## 📖 Como Citar Este Dataset

```bibtex
@misc{enancib_open_database_2026,
  author       = {BRAN Org},
  title        = {ENANCIB Open Database},
  year         = {2026},
  howpublished = {Zenodo},
  doi          = {10.5281/zenodo.23593583},
  url          = {https://doi.org/10.5281/zenodo.23593583}
}
```

**ABNT:**
> BRAN ORG. **ENANCIB Open Database**. Genebra: CERN / Zenodo, 2026. DOI: 10.5281/zenodo.23593583. Disponível em: &lt;https://doi.org/10.5281/zenodo.23593583&gt;.
