import sqlite3
import uuid
from datetime import datetime

class MemoryStorage(object):

    db = "/dev/shm/auth.db"

    def __init__(self):
        self.conn = sqlite3.connect(self.db)
        c = self.conn.cursor()
        c.execute("create table if not exists auth_cache (key NVARCHAR(100) PRIMARY KEY, status TEXT)")
        self.conn.commit()

    def get(self, key):
        c = self.conn.cursor()
        c.execute("SELECT status FROM auth_cache WHERE key = ?", (str(key),))
        res = c.fetchone()
        return res

    def put(self, key, status):
        c = self.conn.cursor()
        c.execute("DELETE FROM auth_cache WHERE key = ?", (str(key), ))
        self.conn.commit()
        c.execute("INSERT INTO auth_cache (key, status) VALUES (?, ?)", (str(key), status, ))
        self.conn.commit()

    def delete(self, key):
        c = self.conn.cursor()
        c.execute("DELETE FROM auth_cache WHERE key = ?", (str(key),))
        self.conn.commit()

    def clear(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM auth_cache")
        self.conn.commit()

    def size(self):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM auth_cache")
        return c.fetchone()[0]
