#coding=utf-8
import redis
import os

class RedisProcess:
    def __init__(self):
        cur = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.pool = redis.ConnectionPool(host='192.168.1.37', port=6379, decode_responses=True)
        self.conn = redis.Redis(connection_pool=self.pool)
        self.rel_filepath = os.path.join(cur, 'rel_data.txt')
        return

    def insert_data(self):
        name = 'person_names'
        i = 0
        for line in open(self.rel_filepath):
            i += 1
            if i < 833:
                continue
            line = line.strip()
            if not line or len(line.split('###')) != 4:
                continue
            self.conn.sadd(name, line)
            print(i)
        return

    def read_data(self):
        name = 'person_names'
        res = 1
        while(res):
            res = self.conn.spop(name)
            print(res)
        return


if __name__ == '__main__':
    handler = RedisProcess()
    handler.insert_data()
    # handler.read_data()

