if __name__ == '__main__':
    from bin.module import OpenTickets
    from datetime import date
    import time
    year = date.fromtimestamp(time.time()).strftime("%Y")
    opti = OpenTickets.OpenTickets(project="SERVICE")
    items, success = opti.run()
    print(items)
    print(success)

