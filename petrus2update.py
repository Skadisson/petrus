if __name__ == '__main__':
    from bin.module import Update
    from bin.service import Cache
    cache = Cache.Cache()
    cache.backup()
    update = Update.Update()
    update.run()

