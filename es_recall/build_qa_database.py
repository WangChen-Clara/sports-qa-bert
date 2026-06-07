# Import Elasticsearch package
import os
import time
import json
from elasticsearch import Elasticsearch
from elasticsearch import helpers


class ProcessIntoES(object):
    def __init__(self):
        self._index = "sport_qa_test_6"  # 定义索引名
        self.es = Elasticsearch("http://127.0.0.1:9200")  # 连接es
        cur = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.music_file = os.path.join(cur, 'data/qa_sports.json')  # 读取文件

    def creatw_mapping(self):  # 创建映射，采用ik分词器
        node_mappings = {
            "properties": {
                "question": {"type": "text",
                             "analyzer": "ik_max_word",
                             "search_analyzer": "ik_smart"},
                "category": {"type": "text",
                             "analyzer": "ik_max_word",
                             "search_analyzer": "ik_smart"},
                "answer": {"type": "text",
                           "analyzer": "ik_max_word",
                           "search_analyzer": "ik_smart"}
            }
        }
        # ik_smart 提取粒度较粗，而后者 ik_max_word 则较细，它给出更多的 token

        if not self.es.indices.exists(index=self._index):  # 判断索引是否已经存在
            self.es.indices.create(index=self._index, mappings=node_mappings)
            print("Create {} mapping successfully.".format(self._index))
        else:
            print("index({}) already exists.".format(self._index))

    def insert_data_bulk(self, action_list):  # 批量插入数据
        success, _ = helpers.bulk(self.es, action_list, index=self._index)
        print("Performed {0} actions. _: {1}".format(success, _))


def init_ES():
    pie = ProcessIntoES()
    pie.creatw_mapping()
    start_time = time.time()
    index = 0
    count = 0
    action_list = []
    BULK_COUNT = 1000  # 每BULK_COUNT个句子一起插入到ES中

    for line in open(pie.music_file, 'r', encoding='utf-8'):
        if not line:
            continue
        item = json.loads(line)
        index += 1
        action = {
            "_index": pie._index,
            "_source": {
                "question": item['question'],
                "category": item['category'],
                "answers": item['answers']
            }
        }
        action_list.append(action)
        if index > BULK_COUNT:
            pie.insert_data_bulk(action_list=action_list)
            index = 0
            count += 1
            print("bulk {} writted finished!".format(count))
            action_list = []
    end_time = time.time()

    print("Time cost:{0}".format(end_time - start_time))


if __name__ == "__main__":
    # 将知识库文件库插入到elasticsearch当中
    init_ES()
