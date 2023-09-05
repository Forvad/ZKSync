import datetime
import random
import sqlite3


class DateBase:
    def __init__(self):
        try:
            self.conn = sqlite3.connect(f'./DateBase/expectation.db')  # создаём или конектим БД
        except sqlite3.OperationalError:
            self.conn = sqlite3.connect(f'../DateBase/expectation.db')

        self.cur = self.conn.cursor()  # обращение к БД
        self.add_table()

    def add_table(self):
        # создание таблицы

        self.cur.execute(f"""CREATE TABLE IF NOT EXISTS data(
                   address TEXT,
                   fee TEXT,
                   date_fee TEXT);
                """)
        self.conn.commit()

    def add_data_balance(self, *args):
        time_ = str(datetime.datetime.today().strftime("%Y-%m-%d"))
        self.cur.execute(f"INSERT INTO data VALUES(?, ?, ?);", args + (time_, ))
        self.conn.commit()

    def get_table(self, address=''):
        self.cur.execute(f"SELECT * FROM data;")
        result = {}
        all_results = self.cur.fetchall()
        for data in all_results:
            if result.get(data[0]):
                result[data[0]][0] += 1
                result[data[0]][1] += float(data[1])
            else:
                result[data[0]] = [1, float(data[1]), {}]
        if address:
            return result[address]
        return result
        # return [{'operation': result[0], 'balance': result[1]} for result in all_results]

    def delete_table(self, address):
        self.cur.execute(f"DELETE FROM data';")
        self.conn.commit()

if __name__ == '__main__':
    DB = DateBase()
    # for _ in range(1000):
    #     adr = random.choice(['0xDbde3A019589F121eBFd68cFCBa6f70becD76CC5', '0x8D26e499377556AEc66D993aD818C40949374e77'])
    #     DB.add_table()
    #     DB.add_data_balance(adr, random.choice([str(0.18), str(0.16), str(0.17)]), '2023-08-28')
    print(DB.get_table('0xDbde3A019589F121eBFd68cFCBa6f70becD76CC5'))
