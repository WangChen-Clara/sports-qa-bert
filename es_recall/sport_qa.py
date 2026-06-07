# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
# import unicodedata2
import json

class Searcher(object):
    def __init__(self):
        self._index = "sport_qa_test_6"
        self.es = Elasticsearch("http://127.0.0.1:9200")  # 连接es

    '''根据question进行事件的匹配查询'''

    def search_specific(self, ques, key="question"):
        query_body = {
            "bool": {
                "must": [
                    {
                        "match": {
                            key: ques
                        }
                    }
                ],
                "must_not": [],
                "should": []
            }
        }
        '''bool【复合查询】
        ⭐must：必须达到 must 列举的所有条件
        ⭐must_not 必须不是指定的情况
        ⭐should：应该达到 should 列举的条件，如果达到会增加相关文档的评分，并不会改变查询的结果。'''
        '''
        Note：在这里返回的检索结果数量有两种设置方式：
        1.在es.search()中指定size参数值
        2.在query_body()中的size对应字段
        '''
        # searched = self.es.search(index=self._index, doc_type=self.doc_type, body=query_body, size=20)
        searched = self.es.search(index=self._index, query=query_body, size=5)
        # 输出查询到的结果
        return searched["hits"]["hits"]

    '''基于ES的问题查询'''

    def search_es(self, question):
        answers = []
        res = self.search_specific(question, 'question')
        # print(res)
        for hit in res:
            answer_dict = {'score': hit['_score'] / 100, 'sim_question': hit['_source']['question'],
                           'answers': hit['_source']['answers']}  # 删除.split('\n')
            answers.append(answer_dict)
        return answers


def main_qa():
    searcher = Searcher()
    # question = '什么是点球？'
    while True:
        question = input('query:')
        # 什么是点球？
        # 今天晚饭吃什么？
        # 将问题写入文件
        with open('sentence1.txt','w') as s:
            s.write(question)
        responses = searcher.search_es(question)
        print(responses)
        # responses_sorted = sorted(responses, key=lambda x: x['score'], reverse=True)
        # sort没有用处，结果已经按评分排序了

        # 将结果写入文件
        with open('responses.json','w') as f:
            json.dump(responses,f,ensure_ascii=False)
        answer = responses[0]['answers']
        print('answer: ', answer)  # 为数据集的回答设定相应的格式

if __name__ == "__main__":
    # 检索式问答
    main_qa()

