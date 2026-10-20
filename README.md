# BRAN Web Database Template

<p align="center">
 <a href="https://github.com/BRAN-Org"><img src="https://img.shields.io/badge/BRAN%20Org-Open%20Data-blue.svg?style=for-the-badge&logo=github" alt="BRAN Org"></a>
 <a href="https://www.budapestopenaccessinitiative.org/"><img src="https://img.shields.io/badge/BOAI-Signatory-orange.svg?style=for-the-badge" alt="BOAI Signatory"></a>
 <a href="https://www.go-fair.org/fair-principles/"><img src="https://img.shields.io/badge/FAIR-Compliant-green.svg?style=for-the-badge" alt="FAIR Principles"></a>
 <a href="LICENSE"><img src="https://img.shields.io/badge/Code_License-GPLv3-blue.svg?style=for-the-badge" alt="GPLv3"></a>
 <a href="LICENSE"><img src="https://img.shields.io/badge/Data_License-CC_BY--NC--SA_4.0-lightgrey.svg?style=for-the-badge" alt="CC BY-NC-SA 4.0"></a>
</p>

Template leve, modular e reproduzível para criação de **APIs REST públicas** e **Dashboards Interativos** para bases de dados acadêmicas e científicas brasileiras no ecossistema da **[BRAN Org](https://github.com/BRAN-Org)** (inspirado na arquitetura do [EBBC-OpenData](https://github.com/GabrielBaiano/EBBC-OpenData)).

---

## Recursos Principais

- **Zero-Build & Alta Performance**: Desenvolvido em Node.js com ES Modules (`"type": "module"`), sem necessidade de transpiladores ou dependências pesadas (`express` e `cors`).
- **Totalmente Agnosticismo a Dados**: Configure o esquema dos dados, nome da entidade, campos de busca, filtros e estatísticas através de um único arquivo de configuração (`config/dataset.config.json`).
- **REST API Completa**:
 - `GET /api/v1/:entity`: Busca textual global, filtros por facetas, ordenação e paginação.
 - `GET /api/v1/:entity/stats`: Estatísticas agregadas calculadas dinamicamente.
 - `GET /api/v1/:entity/:key` e `/api/v1/:entity/by-key/*`: Busca exata por DOI ou ID (suporta barras brutas e URLs).
 - `GET /api/v1/:entity/export`: Exportação em streaming nos formatos **JSON** e **CSV** (com BOM UTF-8 para exibição nativa no Excel).
- **Dashboard Web Interativo (Portal)**:
 - **Métricas e Gráficos**: Visualizações vetoriais nativas e responsivas em SVG powered by [`pure-svg-charts`](https://github.com/GabrielBaiano/pure-svg-charts) (evoluções temporais, rankings, rosca/donut com suporte a exportação em vetor SVG e imagem PNG).
 - **Explorador Avançado**: Tabela com busca em tempo real, filtros laterais por faceta e exportações instantâneas.
 - **API Sandbox**: Gerador dinâmico de snippets de código em **JavaScript (Fetch)**, **Python (Requests)** e **cURL**.
 - **Temas Visuais**: Suporte a *Glass Dark*, *Neon Cyberpunk* e *Apple Minimalist*.
- **Pronto para Deploy na Vercel**: Inclui arquivo `vercel.json` configurado para publicação em 1 clique.

---

## Estrutura do Projeto

```
bran-web-database-template/
├── config/
│ └── dataset.config.json # Configuração central do dataset, entidade, licença e filtros
├── data/
│ └── sample_dataset.json # Arquivos de dados em formato JSON (auto-carregados)
├── public/
│ ├── css/style.css # Design system e temas
│ ├── js/
│ │ ├── app.js # Lógica do painel e interação da API Sandbox
│ │ ├── charts.js # Componente de gráficos vetoriais nativos em SVG
│ │ └── pure-svg-charts.bundle.js # Motor vetorial autônomo pure-svg-charts
│ └── index.html # Interface do Portal Web
├── scripts/
│ ├── convert_csv_to_json.js # Script utilitário para converter CSV em JSON
│ └── validate_dataset.js # Validador de esquemas e campos obrigatórios
├── src/
│ ├── config.js # Loader de configurações
│ ├── dataManager.js # Indexação em memória, busca, filtros e paginação
│ ├── exportEngine.js # Motor de exportação streaming (JSON / CSV com BOM)
│ ├── statsEngine.js # Agregador de métricas e distribuições
│ └── routes.js # Rotas da API REST configuráveis
├── tests/
│ ├── unit.test.js # Testes unitários nativos (node --test)
│ └── api.test.js # Testes de integração HTTP
├── server.js # Servidor Express principal
└── vercel.json # Configuração para deploy na Vercel
```

---

## Como Usar Este Template para um Novo Dataset

### 1. Clonar e Instalar Dependências
```bash
git clone https://github.com/BRAN-Org/bran-web-database-template.git meu-novo-dataset
cd meu-novo-dataset
npm install
```

### 2. Configurar o Dataset (`config/dataset.config.json`)
Edite o arquivo `config/dataset.config.json` para definir as informações específicas da sua base de dados:

```json
{
 "dataset": {
 "title": "Nome da Sua Base de Dados",
 "description": "Descrição sucinta dos metadados e acervo público.",
 "doi": "", // Opcional (Preencher apenas se fornecido)
 "license": "Code: GNU GPLv3 | Data: CC BY-NC-SA 4.0",
 "entityName": "publicacoes",
 "primaryKey": "doi"
 },
 "schema": {
 "searchFields": ["title", "abstract", "authors", "keywords"],
 "facets": [
 { "key": "year", "label": "Ano de Publicação", "type": "number" },
 { "key": "author", "label": "Autor", "type": "string", "targetField": "authors" }
 ]
 }
}
```

### 3. Adicionar Seus Dados
Coloque um ou mais arquivos `.json` com a estrutura dos registros dentro da pasta `data/`.

Se os seus dados estiverem em **CSV**, utilize o conversor automático incluído no template:
```bash
npm run data:convert ./caminho/para/meu_arquivo.csv meu_dataset.json
```

Para validar a integridade dos dados antes do deploy:
```bash
npm run data:validate
```

### 4. Executar Localmente
```bash
# Modo desenvolvimento (com auto-reload)
npm run dev

# Modo produção
npm start
```
Acesse a aplicação no navegador em: `http://localhost:3000`

---

## Testes Automatizados

O template utiliza o executor nativo de testes do Node.js (`node --test`), sem necessidade de dependências externas como Jest ou Mocha:

```bash
npm test
```

---

## Deploy (Vercel / Render)

### Deploy na Vercel
1. Instale a CLI da Vercel (`npm i -g vercel`) ou conecte o repositório no painel web da Vercel.
2. Execute o comando:
 ```bash
 vercel
 ```
O arquivo `vercel.json` incluído cuidará de direcionar a API REST e a interface estática automaticamente.

## Sincronização Automática com Repositórios Filhos (Auto-Sync)

Quando o repositório modelo `BRAN-Org/bran-web-database-template` for atualizado com novas funcionalidades, melhorias de UI ou correções na API, é possível **atualizar automaticamente todos os repositórios derivados da organização** (ex: `EBBC-OpenData`):

### Como Funciona a Sincronização Automática:
1. **GitHub Action (`template-sync.yml`)**: O repositório filho contém a Action em `.github/workflows/template-sync.yml`.
2. **Pull Request Automático**: Toda segunda-feira (ou ao disparar manualmente via `workflow_dispatch`), o GitHub Action verifica se há novos commits no template central `BRAN-Org/bran-web-database-template`.
3. **Preservação dos Dados Locais**: O mecanismo mescla as alterações no código da infraestrutura (`src/`, `public/`, `server.js`), mantendo **100% intactos** os arquivos de dados locais (`data/`, `mock/`, `dataset.config.json`).
4. **Revisão e Merge**: A equipe da BRAN Org recebe um Pull Request pronto com o título `chore(sync): Atualizações automáticas do BRAN Web Database Template` para aprovar em 1 clique.

---

## Confiabilidade e Auditagem dos Dados

| Nível de Confiabilidade | Nota & Justificativa do Acervo |
| :---: | :--- |
| {{RELIABILITY_BADGE}} | {{RELIABILITY_JUSTIFICATION}} |

---

## Princípios e Licença

Este template foi construído em conformidade com as diretrizes internacionais de Ciência Aberta:
- **[Princípios FAIR](https://www.go-fair.org/fair-principles/)**: Dados *Findable, Accessible, Interoperable, Reusable*.
- **[BOAI](https://www.budapestopenaccessinitiative.org/)**: Livre acesso e reutilização do conhecimento acadêmico.
- **Licenciamento Duplo**:
 - **Código-fonte & Engine**: [GNU General Public License v3.0 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.html) — Garante Ciência Aberta e código livre livre de fechamentos proprietários.
 - **Dataset Científico & Metadados (`data/`)**: [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/) — Permite uso e distribuição exclusivamente para pesquisa não-comercial, proibindo expressamente a raspagem ou ingestão para treinamento comercial de modelos de Inteligência Artificial sem autorização prévia.

---

## Submissão de Dados

Possui dados acadêmicos ou acervos científicos que gostaria de disponibilizar publicamente pela BRAN Org? Preencha o formulário de submissão:

 **[Formulário de Submissão de Datasets](https://forms.gle/jNBuP1mjyUXc6v1fA)**

---

<p align="center">
 Desenvolvido com pela <strong>BRAN Org</strong>
</p>