import torch
import numpy as np
import pandas as pd
import mzcn as mz
import nltk
#nltk.download('punkt')
print('matchzoo version', mz.__version__)

ranking_task = mz.tasks.Ranking(losses=mz.losses.RankHingeLoss())
ranking_task.metrics = [
    mz.metrics.NormalizedDiscountedCumulativeGain(k=3),
    mz.metrics.NormalizedDiscountedCumulativeGain(k=5),
    mz.metrics.MeanAveragePrecision()
]
print("`ranking_task` initialized with metrics", ranking_task.metrics)

def load_data(tmp_data,tmp_task):
	df_data = mz.pack(tmp_data,task=tmp_task)
	return df_data

print('data loading ...')
train = pd.read_csv('data/train1.csv').sample(6000)
# print(train)
dev = pd.read_csv('data/dev1.csv').sample(3000)
test = pd.read_csv('data/test1.csv').sample(1500)

train_pack_raw = load_data(train,ranking_task)
dev_pack_raw = load_data(dev,ranking_task)
test_pack_raw=load_data(test,ranking_task)
print('data loaded as `train_pack_raw` `dev_pack_raw` `test_pack_raw`')

import os
folder=mz.__path__[0]+'\\preprocessors\\units\\'
file=folder+'stopwords.txt'
if not os.path.exists(file):
    print('请将stopwords.txt放置在'+folder+'下面'+'否则会报错')
else:
    print('停用表配置成功')

# 垃圾回收
import gc
gc.collect()

preprocessor = mz.models.Bert.get_default_preprocessor()

train_pack_processed = preprocessor.transform(train_pack_raw)
dev_pack_processed = preprocessor.transform(dev_pack_raw)
test_pack_processed = preprocessor.transform(test_pack_raw)

trainset = mz.dataloader.Dataset(
    data_pack=train_pack_processed,
    mode='pair',
    num_dup=2,
    num_neg=1,
    # resample=True,
    # sort=False,
    # batch_size=20
)
devset = mz.dataloader.Dataset(
    data_pack=dev_pack_processed,
    # batch_size=20
)


padding_callback = mz.models.Bert.get_default_padding_callback()
trainloader = mz.dataloader.DataLoader(
    dataset=trainset,
    stage='train',
    callback=padding_callback
)
devloader = mz.dataloader.DataLoader(
    dataset=devset,
    stage='dev',
    callback=padding_callback
)


model = mz.models.Bert()

model.params['task'] = ranking_task
model.params['mode'] = 'bert-base-uncased'
model.params['dropout_rate'] = 0.2

model.build()

print(model)
print('Trainable params: ', sum(p.numel() for p in model.parameters() if p.requires_grad))

no_decay = ['bias', 'LayerNorm.weight']
optimizer_grouped_parameters = [
    {'params': [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)], 'weight_decay': 5e-5},
    {'params': [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
]

from pytorch_transformers import AdamW, WarmupLinearSchedule

optimizer = AdamW(optimizer_grouped_parameters, lr=5e-5, betas=(0.9, 0.98), eps=1e-8)
scheduler = WarmupLinearSchedule(optimizer, warmup_steps=6, t_total=-1)

trainer = mz.trainers.Trainer(
    model=model,
    optimizer=optimizer,
    scheduler=scheduler,
    trainloader=trainloader,
    validloader=devloader,
    validate_interval=None,
    epochs=10
)

trainer.run()
