
from urllib import request,parse
import gzip
import json
from lxml import etree
import pymongo
from collections import Counter


class PersonSpider:
    def __init__(self):
        self.conn = pymongo.MongoClient()
        return

    '''获取html'''
    def get_html(self, word):
        url = 'https://www.sogou.com/kmap?query='+ parse.quote(word)+'&from=relation&id='
        print(word, url)
        headers = {
            'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate,br',
            'Accept-Language': 'en-US,en;q=0.8',
            'Cookie':'GOTO=Af11458; SUV=00EF7C967C10886459C27A09D07E2879; LSTMV=186%2C155; LCLKINT=2115; SUID=6488107C7C20940A0000000059C27A09; ABTEST=7|1543156540|v17; IPLOC=CN1100',
            'Host':'www.sogou.com',
            'Referer':'https://www.sogou.com/tupu/person.html?q=' + parse.quote(word),
        }
        req = request.Request(url, headers=headers)
        page = request.urlopen(req).read()
        html = gzip.decompress(page)
        # 用urllib对网页进行请求,模式和界面版是一样的
        try:
            data = html.decode('UTF-16LE')[:-1]
            data = json.loads(data)
        except Exception as e:
            return {}
        return data

    '''采集主函数'''
    def spider_person(self, person):
        #系统默认返回关于该实体的三度人物关系
        data = self.get_html(person)
        if not data:
            return
        nodes = data['nodes']
        if not nodes:
            return
        else:
            item = {}
            item['nodes'] = nodes
            item['links'] = data['links']
            try:
                self.conn['person_rel']['data2'].insert(item)
            except Exception as e:
                print(e)

    '''收集人物名称'''
    def collect_names_star(self):
        f = open('korea_star_person_names.txt', 'w+')
        for page in range(1,11):
            # url = 'http://g.manmankan.com/dy2013/mingxing/fenlei/china/index_%s.shtml'%page
            url = 'http://g.manmankan.com/dy2013/mingxing/fenlei/hanguo/index_%s.shtml'%page
            req = request.Request(url)
            page = request.urlopen(req).read().decode('gbk')
            selector = etree.HTML(page)
            names = selector.xpath('//li/a/@title')
            f.write('\n'.join(list(names)) + '\n')
        f.close()

    '''收集历史人物'''
    def collect_names_history(self):
        f = open('history_person_names2.txt', 'w+')
        content = open('history_names2.html').read()
        selector = etree.HTML(content)
        names = [i.replace(' ','') for i in selector.xpath('//li/a/text()')]
        f.write('\n'.join(names) + '\n')
        f.close()

    '''采集函数'''
    def spider_main(self):
        history_names = [i.strip() for i in open('history_person_names.txt') if len(i.strip()) > 1]
        star_names = [i.strip() for i in open('star_person_names.txt') if len(i.strip()) > 1]
        name_dict = {
            'star': star_names,
            'history': history_names,
            }
        for label, names in name_dict.items():
            for name in names:
                data = self.spider_person(name)

    '''读取人物名称'''
    def update_data(self):
        names_all_has = []
        names_all_add = []
        for item in self.conn['person_rel']['data'].find():
            nodes =item['nodes']
            links = item['links']
            names = [node['name'] for node in nodes]
            names_all_has += names

        for item in self.conn['person_rel']['data2'].find():
            nodes =item['nodes']
            links = item['links']
            names = [node['name'] for node in nodes]
            names_all_add += names

        for name in set(names_all_add).difference(set(names_all_has)):
            self.spider_person(name)
        return

    '''统计有多少人物'''
    def read_persons(self):
        f = open('person.txt', 'w+')
        names_all = []
        links_all = []
        for item in self.conn['person_rel']['data2'].find():
            nodes = item['nodes']
            links = item['links']
            link_names = [link['name'] for link in links]
            links_all += link_names
            names = [node['name'] for node in nodes]
            names_all += names
        print(len(set(names_all)), len(names_all))
        print(len(set(links_all)), len(links_all))
        f.write('\n'.join(list(set(names_all))))
        f.close()

    '''整理人物数据'''
    def modify_data(self):
        f_rel = open('rel_data.txt', 'w+')
        f_reltype = open('rel_type.txt', 'w+')
        f_person = open('person2id.txt', 'w+')
        person_dict = {}
        rel_dict = {}
        rel_list = set()
        rel_types = []

        for item in self.conn['person_rel']['data2'].find():
            nodes = item['nodes']
            for node in nodes:
                id = node['id']
                name = node['name']
                person_dict[id] = name

        for item in self.conn['person_rel']['data2'].find():
            links = item['links']
            for link in links:
                from_person = person_dict.get(link['from'], '')
                to_person = person_dict.get(link['to'], '')
                if not from_person or not to_person:
                    continue
                rel_name = link['name']
                rel_type = link['type']

                rel_dict[rel_name] = rel_type
                data = [from_person, to_person, rel_name, str(rel_type)]
                rel_list.add('###'.join(data))

        rels_num = len(rel_list)
        persons_num = len(person_dict.keys())

        for rel in rel_list:
            if len(rel.split('###')) != 4:
                continue
            rel_name = rel.split('###')[2]
            rel_types.append(rel_name)


        for id, name in person_dict.items():
            f_person.write(str(id) + '\t' + name + '\n')

        reltype_dict = Counter(rel_types).most_common()

        sum = 0.0
        for i in reltype_dict:
            rel_name = i[0]
            rel_freq = i[1]
            rel_percent = rel_freq/rels_num
            sum += rel_percent

            f_reltype.write(rel_name + '\t' + str(rel_freq) + '\t' + str(rel_percent) + '\t' + str(sum) + '\n')

        f_rel.write('\n'.join(list(rel_list)))
        f_person.close()
        f_rel.close()
        f_reltype.close()

        print('rels_num', rels_num)
        print('persons_num', persons_num)
        return


if __name__ == '__main__':
    handler = PersonSpider()
    handler.spider_main()


