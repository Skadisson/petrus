from werkzeug.wrappers import Request, Response
from bin.service import Environment
from bin.module import Estimate
from bin.module import Search
from bin.module import Trend
from bin.module import CacheOP
from bin.module import Info
from bin.module import Rank
import json


@Request.application
def petrus(request):
    function = request.args.get('function', None)
    items = []
    success = False
    if function == 'Estimate':
        jira_key = request.args.get('jira_key', None)
        if jira_key is not None:
            estimator = Estimate.Estimate(jira_key)
            items, success = estimator.run(True)
    elif function == 'Search':
        keywords = request.args.get('keywords', None)
        if keywords is not None:
            search = Search.Search(keywords)
            items, success = search.run()
    elif function == 'Trend':
        months = request.args.get('months', None)
        year = request.args.get('year', None)
        week_numbers = request.args.get('week_numbers', None)
        trend = Trend.Trend(months, year, week_numbers)
        items, success = trend.run()
    elif function == 'Ping':
        success = True
    elif function == 'Cache':
        jira_key = request.args.get('jira_key', None)
        cache = CacheOP.CacheOP(jira_key)
        if jira_key is not None:
            items, success = cache.run()
    elif function == 'Info':
        info = Info.Info()
        items, success = info.run()
    elif function == 'Rank':
        jira_key = request.args.get('jira_key', None)
        rank = Rank.Rank(jira_key)
        items, success = rank.run()
    response = {'success': success, 'items': items}
    json_response = json.dumps(response)
    return Response(json_response, mimetype='application/json', headers={'Access-Control-Allow-Origin': '*'})


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    env = Environment.Environment()
    port = env.get_service_port()
    host = env.get_service_host()
    run_simple(hostname=host, port=port, application=petrus)
