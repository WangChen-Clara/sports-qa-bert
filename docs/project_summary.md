# Project Summary

## Accurate Resume Description

Built a sports FAQ question-answering system using Elasticsearch for candidate recall and fine-tuned BERT for semantic matching and answer re-ranking. Fine-tuned BERT on a Chinese sentence-pair similarity dataset due to limited labeled sports question-pair data, then transferred it to rank Elasticsearch-recalled sports FAQ candidates.

## What Was Implemented

- Sports FAQ knowledge base preparation.
- Elasticsearch index construction and top-k candidate recall.
- BERT sentence-pair classifier for semantic matching.
- Candidate answer re-ranking based on BERT similarity score.
- ARC-I, Match-LSTM, and BERT comparison experiments.

## Interview-safe Wording

Safe terms:

- BERT fine-tuning
- semantic matching
- sentence-pair classification
- candidate re-ranking
- retrieval-based QA
- Elasticsearch recall

Avoid overstating:

- Do not call it a generative QA system.
- Do not say BERT generated answers.
- Do not say the BERT model learned sports knowledge directly.

The sports knowledge comes from the FAQ database. BERT is used to judge semantic similarity between the user query and recalled standard questions.

