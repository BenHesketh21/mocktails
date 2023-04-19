class FakeRedisClient():
    hashes = {}

    def clear_hashes(self):
        self.hashes = {}
    
    def hset(self, name, key, value):
        if name not in self.hashes:
            self.hashes[name] = {}
        self.hashes[name][key] = value
        return True

    def hscan(self, name, cursor=0):
        if name not in self.hashes:
            self.hashes[name] = {}
        if cursor == 0:
            cursor = 10
        else:
            cursor = 0
        return cursor, self.hashes[name]

    def hget(self, name, key):
        if name not in self.hashes:
            return None
        if key not in self.hashes[name]:
            return None
        return self.hashes[name][key]

    def hdel(self, name, key):
        self.hashes[name].pop(key)
        return True

    def hkeys(self, name):
        list_of_keys = []
        if name not in self.hashes:
            return []
        for _hash in self.hashes[name]:
            list_of_keys.append(_hash)
        return list_of_keys