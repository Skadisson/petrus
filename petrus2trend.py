if __name__ == '__main__':
    from bin.module import Trend
    from datetime import date
    import time
    year = date.fromtimestamp(time.time()).strftime("%Y")
    trend = Trend.Trend(months=1, year=year, week_numbers="", start=0)
    items, success = trend.run()
    print(success)

