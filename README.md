# Sports FAQ Question Answering with Elasticsearch Recall and BERT Semantic Re-ranking

This repository is a cleaned version of an undergraduate thesis project on retrieval-based sports knowledge question answering.

The system uses Elasticsearch for first-stage FAQ candidate recall, then applies a fine-tuned BERT sentence-pair classifier for semantic matching and candidate re-ranking.

## Highlights

- Built a sports FAQ QA system over a sports question-answer knowledge base.
- Used Elasticsearch with Chinese tokenization for candidate question recall.
- Fine-tuned BERT on a Chinese sentence-pair similarity task because the sports FAQ data did not contain enough labeled similar-question pairs.
- Applied the fine-tuned BERT model to score query-candidate question pairs and re-rank ES results.
- Compared BERT with ARC-I and Match-LSTM using NDCG@3, NDCG@5, mAP, and runtime.

## Architecture

```text
User question
    |
    v
Elasticsearch recall
    |
    v
Top-k candidate FAQ questions
    |
    v
Fine-tuned BERT semantic matching
    |
    v
Re-ranked answer
```

## Repository Structure

```text
es_recall/
  build_qa_database.py   # Build Elasticsearch FAQ index
  sport_qa.py            # Retrieve candidate questions from ES

bert_rerank/
  run_similarity.py      # BERT sentence-pair scoring and reranking
  bert_model/            # BERT modeling/tokenization/optimization code

model_comparison/
  arci.py                # ARC-I comparison experiment
  matchlstm.py           # Match-LSTM comparison experiment
  chinese_bert.py        # BERT comparison experiment

third_party/
  mzcn/                  # Chinese MatchZoo fork used by comparison scripts

sample_data/
  sports_qa_sample.jsonl
  sentence_pair_sample.csv

docs/
  project_summary.md
```

## Task Definition

The BERT component is not a generative QA model. It is a semantic matching model.

Input:

```text
sentence1, sentence2, label
```

Where:

- `sentence1`: user question
- `sentence2`: candidate standard FAQ question
- `label = 1`: semantically similar
- `label = 0`: not similar

The model outputs a probability for semantic equivalence. During QA inference, Elasticsearch first recalls candidates, then BERT re-ranks them by semantic similarity.

## Why Fine-tune BERT?

The sports FAQ dataset mainly contains question-answer pairs, not large-scale labeled similar-question pairs. Therefore, BERT was fine-tuned on a Chinese sentence-pair similarity dataset and transferred to the sports FAQ scenario for semantic matching.

The fine-tuning objective teaches BERT to distinguish whether two Chinese questions express the same intent, while the sports knowledge itself remains in the FAQ database.

## Experimental Results

In the thesis experiments, BERT outperformed ARC-I and Match-LSTM on ranking metrics, with higher NDCG and mAP. The trade-off was significantly higher runtime.

Representative results:

| Model | NDCG@3 | NDCG@5 | mAP | Runtime |
|---|---:|---:|---:|---:|
| ARC-I | ~0.4963 | ~0.4965 | ~0.4940 | 21.86s |
| Match-LSTM | ~0.4831 | ~0.4832 | ~0.4794 | 33.05s |
| BERT | ~0.5091 | ~0.5094 | ~0.5066 | 5489.17s |

## Notes

Large artifacts are intentionally excluded from this repository:

- BERT checkpoints
- pre-trained BERT weights
- full sports QA data
- full CCKS similarity data
- TensorBoard logs

See `sample_data/` for small format examples.

