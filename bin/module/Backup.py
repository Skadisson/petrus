from bin.service import Cache


class Backup:
    """Cache Backup"""

    def run(self):
        items = []
        success = True
        cache = Cache.Cache()
        cache.backup()
        return items, success
