# ENANCIB Open Database

<p align="center">
 <a href="https://github.com/BRAN-Org"><img src="https://img.shields.io/badge/BRAN%20Org-Open%20Data-blue.svg?style=for-the-badge&logo=github" alt="BRAN Org"></a>
 <a href="https://www.budapestopenaccessinitiative.org/"><img src="https://img.shields.io/badge/BOAI-Signatory-orange.svg?style=for-the-badge" alt="BOAI Signatory"></a>
 <a href="https://www.go-fair.org/fair-principles/"><img src="https://img.shields.io/badge/FAIR-Compliant-green.svg?style=for-the-badge" alt="FAIR Principles"></a>
 <a href="LICENSE"><img src="https://img.shields.io/badge/Code_License-GPLv3-blue.svg?style=for-the-badge" alt="GPLv3"></a>
 <a href="LICENSE"><img src="https://img.shields.io/badge/Data_License-CC_BY--NC--SA_4.0-lightgrey.svg?style=for-the-badge" alt="CC BY-NC-SA 4.0"></a>
 <a href="https://doi.org/10.5281/zenodo.23593583"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.23593583.svg" alt="DOI"></a>
</p>

Base de dados bibliométrica aberta e acervo histórico completo dos 6.998 trabalhos científicos apresentados nos anais das 25 edições do Encontro Nacional de Pesquisa e Pós-Graduação em Ciência da Informação (ENANCIB, 1994–2026), principal conferência de Ciência da Informação no Brasil, disponibilizado pela BRAN Org sob princípios FAIR e BOAI.

---

## Visão Geral da Base de Dados

- **Acervo / Fonte Primária**: Encontro Nacional de Pesquisa e Pós-Graduação em Ciência da Informação (ENANCIB)
- **Entidade Principal**: `articles`
- **Total de Registros**: Configurado e indexado dinamicamente
- **Licença dos Dados**: Code: GNU GPLv3 | Data: CC BY-NC-SA 4.0 (Não-Comercial & Sem Treino Comercial de IA)

- **Manutenção & Suporte**: [BRAN Org](https://github.com/BRAN-Org)

---

## Portal Web Interativo & REST API

Esta base de dados fornece tanto uma interface web interativa (Dashboard) quanto uma **API REST pública de alta performance** sem necessidade de chave de API.

### Endpoints Principais

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/v1/config` | Retorna os metadados e schema configurado da base |
| `GET` | `/api/v1/articles` | Lista registros com busca textual, facetas, ordenação e paginação |
| `GET` | `/api/v1/articles/:key` | Busca um registro exato por DOI ou ID |
| `GET` | `/api/v1/articles/stats` | Retorna métricas consolidadas (rankings, distribuições por ano) |
| `GET` | `/api/v1/articles/stats/temporal` | Análise de séries temporais empilhadas |
| `GET` | `/api/v1/articles/stats/correlations` | Matriz de coocorrência (ex: ferramentas vs fontes) |
| `GET` | `/api/v1/articles/export?format=csv` | Exporta o dataset completo em **CSV (UTF-8 BOM)** ou **JSON** |

---

## Exemplo de Consumo da API

### cURL
```bash
curl -X GET "http://localhost:3000/api/v1/articles?q=ciencia&limit=5"
```

### JavaScript (Fetch)
```javascript
const response = await fetch('http://localhost:3000/api/v1/articles?limit=10');
const data = await response.json();
console.log(`Carregados ${data.total} registros de ENANCIB Open Database`);
```

### Python
```python
import requests

url = "http://localhost:3000/api/v1/articles"
response = requests.get(url, params={"limit": 10})
data = response.json()
print(f"Total de registros: {data['total']}")
```

---

## Como Rodar Localmente

### 1. Clonar o Repositório
```bash
git clone https://github.com/BRAN-Org/enancib-open-database.git
cd enancib-open-database
```

### 2. Instalar Dependências
```bash
npm install
```

### 3. Iniciar o Servidor
```bash
# Modo Desenvolvimento
npm run dev

# Modo Produção
npm start
```
Acesse no navegador: `http://localhost:3000`

---

## Validação dos Dados
Para testar a integridade do schema antes do deploy:
```bash
npm run data:validate
```

---

## Como Citar Este Dataset

Se você utilizar estes dados em pesquisas acadêmicas ou software, por favor cite:

```bibtex
@misc{enancib_open_database_2026,
  author = {BRAN Org},
  title = {ENANCIB Open Database: Base de Dados Bibliométrica Aberta e Acervo Histórico Completo do ENANCIB (1994–2026)},
  year = {2026},
  publisher = {BRAN Org},
  url = {https://github.com/BRAN-Org/enancib-open-database}
}
```

---

## Princípios e Licença

- **[Princípios FAIR](https://www.go-fair.org/fair-principles/)**: Dados *Findable, Accessible, Interoperable, Reusable*.
- **[BOAI](https://www.budapestopenaccessinitiative.org/)**: Livre acesso à informação e produção acadêmica.
- **Licenciamento Duplo**:
 - **Código-fonte & Engine**: [GNU General Public License v3.0 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.html) — Garante Ciência Aberta e código livre livre de fechamentos proprietários.
 - **Dataset Científico & Metadados (`data/`)**: [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/) — Permite uso e distribuição exclusivamente para pesquisa não-comercial, proibindo expressamente a raspagem ou ingestão para treinamento comercial de modelos de Inteligência Artificial sem autorização prévia.

---

## Confiabilidade e Auditagem dos Dados

| Nível de Confiabilidade | Nota & Justificativa do Acervo |
| :---: | :--- |
| ![Classificação Verde](https://img.shields.io/badge/Classifica%C3%A7%C3%A3o-Verde-brightgreen.svg?style=for-the-badge) | **100% Fiel à Fonte Primária com Preservação Digital Histórica Completa**. Acervo histórico integral cobrindo todas as 25 edições do ENANCIB (1994–2026), unificando os dados colhidos do portal oficial OJS da ANCIB (2021–2026) e o resgate da base histórica BENANCIB / UFPB (1994–2019, indexada na BRAPCI). Todos os 6.998 trabalhos científicos foram catalogados com hash SHA-256 de proveniência preservada, 96,5% de cobertura de resumos e mapeamento canônico dos 12 Grupos de Trabalho (GT 1 ao GT 12). |

> **Nota Metodológica Oficial:** 
> *A BRAN preserva a fidelidade estrita à fonte de origem e nunca inventa dados inexistentes. Discrepâncias e lacunas identificadas nos portais de origem são registradas e tratadas tecnicamente nos relatórios de auditoria.*

---

<p align="center">
  Mantido pela <strong><a href="https://github.com/BRAN-Org">BRAN Org</a></strong>
</p>

