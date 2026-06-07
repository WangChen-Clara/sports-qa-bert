# Data Construction

This module documents the internship-stage data processing work that later became the knowledge base for the undergraduate Sports FAQ QA project.

## Purpose

The original sports FAQ data was not a manually labeled reranking benchmark. It was a domain QA knowledge base built from public Chinese QA corpora. Each record is a question-answer pair, later indexed by Elasticsearch and used as the retrieval target for the FAQ system.

## Original Local Evidence

The original files are intentionally not included in this public repository because they are large raw datasets.

Local source traces:

```text
D:\pythonProject\sx_json
D:\pythonProject\ES_baesd_QA_sport\data
```

Important local files:

```text
sx_json/baike_qa_train.json
sx_json/baike_qa_valid.json
sx_json/test.py
sx_json/test2.py
sx_json/train.json
sx_json/wd.json
sx_json/wd1.json
ES_baesd_QA_sport/data/qa_sports_2.json
ES_baesd_QA_sport/data/qa_sports_3.json
ES_baesd_QA_sport/data/qa_sports.json
```

## Reconstructed Flow

1. Read large Chinese QA corpora line by line.
2. Filter sports-related records.
3. Normalize fields into a unified sports FAQ schema.
4. Convert JSON arrays or raw records into JSONL/ndJSON for Elasticsearch bulk import.
5. Build the final sports FAQ knowledge base with 31,074 question-answer pairs.

The reconstructed counts from local files are:

| Intermediate File | Role | Count |
|---|---|---:|
| `qa_sports_2.json` | one sports QA subset | 10,109 |
| `qa_sports_3.json` | another sports QA subset | 20,965 |
| `qa_sports.json` | merged sports FAQ data | 31,074 |

These numbers match the internship report notes.

## Final Schema

The Elasticsearch-facing data uses this logical schema:

```json
{
  "qid": "question id",
  "category": "sports category",
  "question": "standard FAQ question",
  "desc": "optional question description",
  "answers": "standard answer"
}
```

## What This Data Is Not

This data is not a labeled semantic reranking dataset. It does not contain:

- query-candidate question pairs
- binary relevance labels
- graded relevance scores
- manually judged ES Top-K reranking annotations

That is why the BERT fine-tuning and model comparison experiments used external Chinese semantic matching data.

## Resume-Safe Description

Safe wording:

> Built a 31K-record sports FAQ knowledge base by filtering, cleaning, and normalizing sports-related question-answer records from Chinese QA corpora; converted the data into Elasticsearch-ready JSONL format for downstream FAQ retrieval.

Avoid saying:

> Built a 31K labeled sports reranking benchmark.

