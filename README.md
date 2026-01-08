# Assistant IA Pharmacie (Winpharma)

Assistant IA pour le pilotage RH, achats, ventes, stock basé sur Winpharma via un connecteur REST DataSnap.

## Démarrage rapide

```bash
docker compose up --build
```

Les scripts SQL sont appliqués automatiquement au démarrage de Postgres (copiés dans l'image DB).
Si le conteneur `ia_pharma_db` affiche encore `Permission denied` sur `/docker-entrypoint-initdb.d`,
vérifiez que l'image DB est bien reconstruite (`docker compose build db`) et que le dossier
`sql/` est lisible par Docker (ex: `chmod -R a+rX sql`).
Si vous voyez encore l'erreur de schéma `rag`, reconstruisez sans cache
(`docker compose build db --no-cache`) puis supprimez le volume et relancez
(`docker compose down -v` puis `docker compose up --build`).

## Configuration

Copiez `.env.example` en `.env` et ajustez :

- `PHARMACY_HOSTS` : mapping `code=ip` (ex: `frang=192.168.1.10`).
- `DATABASE_URL` : URL Postgres.
- `EXTRACTOR_URL` : URL du service extractor (appelé par l'API).

## Interface HTML

Ouvrez `http://localhost:8000/` pour accéder à la console web (extraction, KPI, RAG).
La page de configuration est disponible sur `http://localhost:8000/config`.
La page SQL (SELECT) est disponible sur `http://localhost:8000/sql`.

## Extraction Winpharma

Déclenchez une extraction via l'API :

```bash
curl -X POST http://localhost:8000/extract/frang/sales
```

Dataset supportés (placeholders) : `sales`, `products`, `stock`, `purchases`.

## KPI

```bash
curl "http://localhost:8000/kpi/frang/sales?from=2024-01-01&to=2024-01-31"
```

Autres endpoints :

- `GET /kpi/{pharma}/stock_alerts`
- `GET /kpi/{pharma}/purchases`

## RAG (documents internes)

Indexer un dossier :

```bash
curl -X POST http://localhost:8000/rag/index \
  -H 'Content-Type: application/json' \
  -d '{"pharma_id":"frang","path":"/data/docs"}'
```

Uploader des documents via l'interface web : utilisez la section \"Documents\" pour déposer des fichiers puis lancer l'indexation automatique.

Poser une question :

```bash
curl -X POST http://localhost:8000/rag/ask \
  -H 'Content-Type: application/json' \
  -d '{"pharma_id":"frang","question":"Quels sont les top ventes du mois ?"}'
```

## Structure

- `extractor/` : ingestion DataSnap -> staging
- `api/` : FastAPI + KPI + RAG
- `sql/` : schéma PostgreSQL
- `tests/` : smoke tests

## Next steps

1. Remplacer les placeholders `SALES_QUERY`, `PRODUCTS_QUERY`, ... dans `extractor/app/queries.py` par les vrais noms DataSnap Winpharma.
2. Ajuster la logique de transformation `staging -> mart` dans `api/app/kpi.py` selon les colonnes réelles.
3. Si besoin, brancher un LLM local via `rag/llm.py` (ex: Ollama).
