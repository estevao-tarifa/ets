# ETS — Quickstart

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado
- Chave de API Groq gratuita: [console.groq.com](https://console.groq.com) (sem cartão de crédito)

## Setup

```bash
git clone https://github.com/estevao-tarifa/ets
cd ets
cp .env.example .env
# Edite .env e coloque sua chave: LLM_API_KEY=gsk_...
docker compose up
```

Aguarde o build (~2 min na primeira vez). Quando ver `ETS backend started`, abra:

```
http://localhost:8000
```

## Primeiros passos

1. **Configurar LLM**: a tela de Settings abre automaticamente. Selecione **Groq**, modelo `llama3-8b-8192`, cole sua chave, clique **Testar conexão** e depois **Salvar**.
2. **Criar matéria**: no Painel, digite o nome (ex: "Cálculo I") e clique **Criar matéria**.
3. **Upload de PDF**: clique **Upload PDF** na matéria criada. O sistema processa em background — a barra de progresso mostra cada etapa.
4. **Ver grafo**: após o processamento, clique **Grafo** para visualizar os conceitos extraídos.
5. **Estudar**: clique **Estudar** para iniciar uma sessão. Registre acertos, erros e dúvidas com 1 clique. Encerre com autoavaliação 1–5.
6. **Flashcards**: acesse **Flashcards** para revisar os cartões pendentes com repetição espaçada (SM-2).

## Notas

- Os dados (banco SQLite + PDFs) ficam em `./data/` — não são perdidos no restart.
- Nenhuma GPU necessária: tudo roda em CPU.
- Sistema single-tenant: 1 usuário por instalação.
- Para usar outro provedor, edite `LLM_PROVIDER`, `LLM_API_KEY` e `LLM_MODEL` no `.env`.
