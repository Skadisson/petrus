if __name__ == '__main__':
    from bin.module import Sync
    from bin.service import Cache
    cache = Cache.Cache()
    cache.backup()
    sync = Sync.Sync()
    sync.run()

