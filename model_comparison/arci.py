import torch
import numpy as np
import pandas as pd
import mzcn as mz
import nltk

# nltk.download('punkt')
print('matchzoo version', mz.__version__)

ranking_task = mz.tasks.Ranking(losses=mz.losses.RankHingeLoss())
ranking_task.metrics = [
    mz.metrics.NormalizedDiscountedCumulativeGain(k=3),
    mz.metrics.NormalizedDiscountedCumulativeGain(k=5),
    mz.metrics.MeanAveragePrecision()
]
print("`ranking_task` initialized with metrics", ranking_task.metrics)


def load_data(tmp_data, tmp_task):
    df_data = mz.pack(tmp_data, task=tmp_task)
    return df_data


print('data loading ...')
train = pd.read_csv('data/train1.csv').sample(3000)
# print(train)
dev = pd.read_csv('data/dev1.csv').sample(1500)
test = pd.read_csv('data/test1.csv').sample(900)
# train = pd.read_csv('H:\python\project2\mzcn-main\\test\\ranking\data\\train_data(1).csv').sample(100)
# print(train.iloc[1]['text_left'])
# dev = pd.read_csv('H:\python\project2\mzcn-main\\test\\ranking\data\\dev_data(1).csv').sample(50)
# test = pd.read_csv('H:\python\project2\mzcn-main\\test\\ranking\data\\test_data(1).csv').sample(30)

train_pack_raw = load_data(train, ranking_task)
dev_pack_raw = load_data(dev, ranking_task)
test_pack_raw = load_data(test, ranking_task)
print('data loaded as `train_pack_raw` `dev_pack_raw` `test_pack_raw`')

import os

folder = mz.__path__[0] + '\\preprocessors\\units\\'
file = folder + 'stopwords.txt'
if not os.path.exists(file):
    print('请将stopwords.txt放置在' + folder + '下面' + '否则会报错')
else:
    print('停用表配置成功')

# 垃圾回收
import gc

gc.collect()

preprocessor = mz.models.ArcI.get_default_preprocessor(
    filter_mode='df',
    filter_low_freq=1,
)

train_pack_processed = preprocessor.fit_transform(train_pack_raw)
dev_pack_processed = preprocessor.transform(dev_pack_raw)
test_pack_processed = preprocessor.transform(test_pack_raw)

preprocessor.context

trainset = mz.dataloader.Dataset(
    data_pack=train_pack_processed,
    mode='pair',
    num_dup=2,
    num_neg=1
)
devset = mz.dataloader.Dataset(
    data_pack=dev_pack_processed
)

padding_callback = mz.models.ArcI.get_default_padding_callback(
    fixed_length_left=10,
    fixed_length_right=100,
    pad_word_value=0,
    pad_word_mode='pre'
)

trainloader = mz.dataloader.DataLoader(
    dataset=trainset,
    stage='train',
    callback=padding_callback,
)
devloader = mz.dataloader.DataLoader(
    dataset=devset,
    stage='dev',
    callback=padding_callback,
)

model = mz.models.ArcI()

model.params['task'] = ranking_task
# model.params['embedding'] = embedding_matrix #这里是当加载glove等模型时取消该行注释
# 设置embedding系数
model.params["embedding_output_dim"] = 100
model.params["embedding_input_dim"] = preprocessor.context["embedding_input_dim"]
model.params['left_length'] = 10
model.params['right_length'] = 100
model.params['left_filters'] = [128]
model.params['left_kernel_sizes'] = [3]
model.params['left_pool_sizes'] = [4]
model.params['right_filters'] = [128]
model.params['right_kernel_sizes'] = [3]
model.params['right_pool_sizes'] = [4]
model.params['conv_activation_func'] = 'relu'
model.params['mlp_num_layers'] = 1
model.params['mlp_num_units'] = 100
model.params['mlp_num_fan_out'] = 1
model.params['mlp_activation_func'] = 'relu'
model.params['dropout_rate'] = 0.9

model.build()

print(model)
print('Trainable params: ', sum(p.numel() for p in model.parameters() if p.requires_grad))

optimizer = torch.optim.Adadelta(model.parameters())

trainer = mz.trainers.Trainer(
    model=model,
    optimizer=optimizer,
    trainloader=trainloader,
    validloader=devloader,
    validate_interval=None,
    epochs=10
)
trainer.run()

import gc

gc.collect()
