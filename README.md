# Sports-QA-BERT

**基于 Elasticsearch + BERT 的体育 FAQ 问答系统**  
Sports FAQ QA System with Elasticsearch Recall and BERT Semantic Re-ranking

本项目整理自本科实习与本科毕业设计代码，完整链路包括：**体育领域 QA 数据构建、Elasticsearch 候选召回、BERT 语义匹配重排序，以及 ARC-I / Match-LSTM / BERT 模型对比实验**。

## 项目定位

这是一个检索式 FAQ 问答系统，不是生成式问答，也不是 RAG。

系统先使用 Elasticsearch 从体育 FAQ 知识库中召回候选标准问题，再使用微调后的 BERT 句对匹配模型计算“用户问题”和“候选问题”的语义匹配概率，并根据该概率对候选答案进行重排序。

```text
体育 QA 数据构建
    -> Elasticsearch FAQ 索引
    -> ES Top-5 候选召回
    -> BERT 语义匹配打分
    -> 候选问题重排序
    -> 返回匹配 FAQ 对应答案
```

## 仓库结构

```text
data_construction/
  README.md                              # 实习阶段数据处理说明
  scripts/
    filter_baike_qa_sports.py            # 体育 QA 筛选脚本重构版
    convert_json_array_to_jsonl.py        # JSON 数组转 JSONL/ndJSON 工具
  samples/
    sports_qa_construction_sample.jsonl  # 数据构建样例

es_recall/
  build_qa_database.py                   # 构建 Elasticsearch 体育 FAQ 索引
  sport_qa.py                            # 根据用户问题召回 Top-5 候选 FAQ

bert_rerank/
  run_similarity.py                      # BERT 句对语义匹配与候选重排序
  bert_model/                            # BERT 建模、分词和优化相关代码

model_comparison/
  arci.py                                # ARC-I 对比实验
  matchlstm.py                           # Match-LSTM 对比实验
  chinese_bert.py                        # BERT 对比实验

third_party/
  mzcn/                                  # 中文 MatchZoo 风格排序框架

sample_data/
  sports_qa_sample.jsonl                 # 体育 FAQ 小样例
  sentence_pair_sample.csv               # 句对匹配小样例

docs/
  project_summary.md
```

## 数据构建

体育 FAQ 知识库是在本科实习阶段完成的，后来作为本科毕设问答系统的知识库。

本地历史文件主要位于：

```text
D:\pythonProject\sx_json
D:\pythonProject\ES_baesd_QA_sport\data
```

数据处理流程：

1. 逐行读取大规模中文 QA 语料。
2. 根据类别、topic 或体育关键词筛选体育相关记录。
3. 将不同来源的数据字段统一为 FAQ 格式。
4. 将 JSON 数据转换为 Elasticsearch bulk 导入更方便的 JSONL / ndJSON。
5. 构建最终体育 FAQ 知识库。

从本地文件反查确认的数据规模：

| 数据文件 | 作用 | 数量 |
|---|---|---:|
| `qa_sports_2.json` | 体育 QA 子集 | 10,109 |
| `qa_sports_3.json` | 体育 QA 子集 | 20,965 |
| `qa_sports.json` | 合并后的体育 FAQ 数据 | 31,074 |

最终 FAQ 数据结构大致为：

```json
{
  "qid": "question id",
  "category": "体育相关类别",
  "question": "标准问题",
  "desc": "问题描述",
  "answers": "标准答案"
}
```

这份体育数据主要作为 FAQ 知识库使用，提供标准问题与对应答案。

## Elasticsearch 候选召回

Elasticsearch 模块负责构建体育 FAQ 索引，并完成第一阶段候选召回。

主要代码：

```text
es_recall/build_qa_database.py
es_recall/sport_qa.py
```

索引字段包括：

- `question`
- `category`
- `answers`

检索模块会根据用户输入问题召回 Top-5 候选 FAQ，并将候选结果写入 `responses.json`，供后续 BERT 重排序模块读取。

## BERT 语义重排序

BERT 模块是句对语义匹配模型，不负责生成答案。

训练/预测输入形式：

```text
sentence1, sentence2, label
```

含义：

- `sentence1`：用户问题
- `sentence2`：候选 FAQ 问题
- `label = 1`：两个问题语义匹配
- `label = 0`：两个问题语义不匹配

推理时，BERT 输出二分类 softmax 概率，其中 class `1` 的概率被作为语义相似度：

```text
similarity = P(label = 1 | user_question, candidate_question)
```

系统选择相似度最高的候选问题，并返回该 FAQ 对应的答案。如果最高分低于阈值，则返回没有合适答案。

## BERT 微调与迁移

体育 FAQ 数据主要是 question-answer pair，缺少大规模“相似问题 / 不相似问题”的标注。因此，BERT 不是直接用体育 QA 数据监督微调的，而是使用外部中文语义匹配数据完成句对二分类微调，再迁移到体育 FAQ 场景中作为 reranker。

微调目标是让模型学习中文问题之间的语义匹配能力，而体育领域知识仍然来自 FAQ 知识库本身。

## 模型对比实验

项目中还包括文本匹配模型对比实验：

- ARC-I
- Match-LSTM
- BERT

评估指标：

- NDCG@3
- NDCG@5
- mAP
- runtime

论文表格中第 10 个 epoch 的结果：

| 模型 | NDCG@3 | NDCG@5 | mAP | 运行时间 |
|---|---:|---:|---:|---:|
| ARC-I | 0.4963 | 0.4965 | 0.4940 | 21.86s |
| Match-LSTM | 0.4831 | 0.4832 | 0.4794 | 33.05s |
| BERT | 0.5091 | 0.5094 | 0.5066 | 5489.17s |

模型对比实验用于分析不同文本匹配模型在语义匹配排序任务中的效果与运行效率差异。

## 仓库说明

为了便于公开展示，本仓库不包含以下大文件：

- 原始大规模 QA 语料
- 完整体育 FAQ 数据集
- BERT checkpoint
- 预训练 BERT 权重
- 训练日志和中间产物
- 本地 Elasticsearch 数据

仓库中仅保留代码、说明文档和小规模样例数据。

## License

MIT License.
