from bs4 import BeautifulSoup
import urllib
import urllib2
import json


def main():
    query = "sbml xml"
    
    results = bing_search(query, 'Web')
    with open('results.json','w') as f:
        json.dump(results,f)
def bing_search(query, search_type):
    #search_type: Web, Image, News, Video
    key= 'LXJAnlgTFNAJp49NVK2xnWZNMdGFVGLBCMKH4Spjg1w'
    query = urllib.quote(query)
    # create credential for authentication
    user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
    credentials = (':%s' % key).encode('base64')[:-1]
    auth = 'Basic %s' % credentials
    totalResults = []
    for iteration in range(0,100):
        print iteration
        url = 'https://api.datamarket.azure.com/Bing/SearchWeb/v1/Web' + '?Query=%27'+query+'%27&$skip={0}&$top=50&$format=json'.format(iteration*50)
        request = urllib2.Request(url)
        request.add_header('Authorization', auth)
        request.add_header('User-Agent', user_agent)
        request_opener = urllib2.build_opener()
        response = request_opener.open(request) 
        response_data = response.read()
        json_result = json.loads(response_data)
        result_list = json_result['d']['results']
        totalResults.extend(result_list)
    return totalResults
 
if __name__ == "__main__":
    main()