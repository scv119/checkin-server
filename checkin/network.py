import httplib

def https_get(url):
    uri = '/'
    host = url
    sep_idx = url.find('/') 
    if sep_idx >= 0:
        host = url[:sep_idx]
        uri  = url[sep_idx:]
    c = httplib.HTTPSConnection(host)
    c.request("GET", uri)
    response = c.getresponse()
    data = response.read()
    return data
