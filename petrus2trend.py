if __name__ == '__main__':
    from bin.module import Trend
    trend = Trend.Trend(months=1)
    items, success = trend.run()
    print(success)

