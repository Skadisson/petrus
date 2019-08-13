from bin.service import Cache


class Backup:
    """Cache Backup"""

    @staticmethod
    def run():
        items = []
        success = True
        cache = Cache.Cache()
        cache.backup()
        return items, success
