# Sports-QA-BERT

Sports FAQ QA system with Elasticsearch recall and BERT semantic re-ranking.

本项目整理自本科实习与本科毕业设计代码。完整链路包括：体育领域 QA 数据构建、Elasticsearch 候选召回、BERT 语义匹配重排序，以及 ARC-I / Match-LSTM / BERT 模型对比实验。

## Project Scope

This is a retrieval-based FAQ question answering system, not a generative QA system.

The system first retrieves candidate FAQ questions from a sports knowledge base with Elasticsearch, then uses a fine-tuned BERT sentence-pair classifier to score semantic similarity between the user query and each candidate question.

```text
Sports QA data construction
    -> Elasticsearch FAQ index
    -> ES Top-5 candidate recall
    -> BERT semantic matching score
    -> candidate re-ranking
    -> answer from the matched FAQ record
```

## Repository Structure

```text
data_construction/
  README.md                              # internship-stage data processing notes
  scripts/
    filter_baike_qa_sports.py            # cleaned reconstruction of sports QA filtering
    convert_json_array_to_jsonl.py        # JSON array to JSONL conversion helper
  samples/
    sports_qa_construction_sample.jsonl  # tiny public sample

es_recall/
  build_qa_database.py                   # build Elasticsearch sports FAQ index
  sport_qa.py                            # retrieve Top-5 candidate FAQ questions

bert_rerank/
  run_similarity.py                      # BERT sentence-pair similarity and reranking
  bert_model/                            # BERT modeling/tokenization/optimization code

model_comparison/
  arci.py                                # ARC-I comparison experiment
  matchlstm.py                           # Match-LSTM comparison experiment
  chinese_bert.py                        # BERT comparison experiment

third_party/
  mzcn/                                  # Chinese MatchZoo-style ranking framework

sample_data/
  sports_qa_sample.jsonl                 # small sports FAQ sample
  sentence_pair_sample.csv               # small semantic matching sample

docs/
  project_summary.md
```

## Data Construction

The sports FAQ knowledge base was built during the internship stage and later used in the undergraduate thesis project.

Reconstructed local evidence:

```text
D:\pythonProject\sx_json
D:\pythonProject\ES_baesd_QA_sport\data
```

The processing flow was:

1. Read large Chinese QA corpora line by line.
2. Filter sports-related records by category, topic, or sports keywords.
3. Normalize heterogeneous fields into a unified FAQ schema.
4. Convert JSON data into JSONL/ndJSON for Elasticsearch bulk import.
5. Build the final sports FAQ knowledge base.

Confirmed local counts:

| Data File | Role | Count |
|---|---|---:|
| `qa_sports_2.json` | sports QA subset | 10,109 |
| `qa_sports_3.json` | sports QA subset | 20,965 |
| `qa_sports.json` | merged sports FAQ data | 31,074 |

The final FAQ schema is:

```json
{
  "qid": "question id",
  "category": "sports category",
  "question": "standard FAQ question",
  "desc": "optional question description",
  "answers": "standard answer"
}
```

Important boundary: this sports data is a QA knowledge base, not a labeled reranking benchmark. It does not contain manually judged `query, candidate_question, relevance_label` records.

## Elasticsearch Recall

The Elasticsearch module builds a sports FAQ index and performs first-stage candidate recall.

Main implementation:

```text
es_recall/build_qa_database.py
es_recall/sport_qa.py
```

The ES index uses sports FAQ fields such as:

- `question`
- `category`
- `answers`

The search module retrieves Top-5 candidate FAQ questions for a user query and writes the candidate results to `responses.json` for downstream BERT reranking.

## BERT Re-ranking

The BERT module is a sentence-pair semantic matching model.

Input format:

```text
sentence1, sentence2, label
```

Meaning:

- `sentence1`: user question
- `sentence2`: candidate FAQ question
- `label = 1`: semantically matched
- `label = 0`: not semantically matched

At inference time, BERT outputs a softmax probability. The probability of class `1` is used as the semantic similarity score:

```text
similarity = P(label = 1 | user_question, candidate_question)
```

The candidate with the highest similarity score is selected. If the best score is below the threshold, the system returns a no-suitable-answer result.

## Fine-tuning Boundary

The sports FAQ data mainly contains question-answer pairs and does not provide large-scale labeled similar/dissimilar question pairs. Therefore, BERT was fine-tuned on external Chinese semantic matching data and then applied to the sports FAQ reranking scenario.

Safe interpretation:

> BERT was fine-tuned for Chinese sentence-pair semantic matching and used as a reranker for Elasticsearch-recalled sports FAQ candidates.

Do not overstate it as:

> BERT was strictly evaluated as better than ARC-I on a labeled sports Top-5 reranking benchmark.

That full labeled sports reranking benchmark was not built in the recovered code.

## Model Comparison

The project also includes comparison experiments for:

- ARC-I
- Match-LSTM
- BERT

Metrics:

- NDCG@3
- NDCG@5
- mAP
- runtime

From the thesis result table, the 10th epoch results were:

| Model | NDCG@3 | NDCG@5 | mAP | Runtime |
|---|---:|---:|---:|---:|
| ARC-I | 0.4963 | 0.4965 | 0.4940 | 21.86s |
| Match-LSTM | 0.4831 | 0.4832 | 0.4794 | 33.05s |
| BERT | 0.5091 | 0.5094 | 0.5066 | 5489.17s |

Code inspection shows that the comparison scripts use labeled Chinese semantic matching data for ranking metrics. The sports FAQ `test1.csv` sample does not contain relevance labels, so the model comparison should be described as semantic matching/ranking evaluation, not as a strict labeled sports reranking evaluation.

## Resume-Safe Summary

Recommended wording:

> Built a sports FAQ QA prototype based on Elasticsearch and BERT. Constructed a 31K-record sports FAQ knowledge base from Chinese QA corpora, indexed it with Elasticsearch for Top-K candidate recall, and used a fine-tuned BERT sentence-pair matching model to rerank recalled candidate questions by semantic similarity. Compared ARC-I, Match-LSTM, and BERT on semantic matching/ranking metrics including NDCG and mAP.

Use with caution:

- Do not claim that the sports FAQ data was a manually labeled reranking benchmark.
- Do not claim quantified BERT-over-ARC-I improvement specifically on sports Top-5 reranking.
- Do not describe the system as generative QA or RAG.

## Large Files Excluded

This public repository excludes:

- full raw QA corpora
- full sports FAQ dataset
- BERT checkpoints
- pretrained BERT weights
- training logs and intermediate outputs
- local Elasticsearch data

Only code, documentation, and tiny samples are included.

## License

MIT License.

