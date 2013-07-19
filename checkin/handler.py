#!/usr/bin/env python
#coding = utf-8
import json
import config
import time
import tornado
import checkin.network

from redis import Redis

_client = Redis(config.REDIS_HOST, config.REDIS_PORT)
_KEY = "FEED"

class FeedHandler(tornado.web.RequestHandler):
    def get(self):
        data = []
        for item in  _client.zrange(_KEY, 0, 10, withscores = True):
            j_obj = json.loads(item[0])
            data.append((j_obj['data'], int(item[1]), float(j_obj['lo']), float(j_obj['la'])))
        self.set_header('Content-Type',"application/json" )
        self.write(json.dumps(data))

    def post(self):
        data = self.get_argument('data', 'No data received')
        lo   = self.get_argument('lo', -1)
        la   = self.get_argument('la', -1)
        _client.zadd(_KEY, json.dumps({'lo':lo, 'la':la, 'data':data}), int(time.time()))
        self.write("{}")

class NearbyHandler(tornado.web.RequestHandler):
    def get(self):
        lat = self.get_argument('lat', 0)
        lng   = self.get_argument('lng', 0)
        query   = self.get_argument('query', None) 
        data = []
        url = config.NEARBY_API+ "?types=food&rankby=distance&language=zh-CN&sensor=true&location=%s,%s&key=%s"%(lat,lng,config.API_KEY)
        if query is not None:
            url = url + "&name=%s"%(query)
        print url
        result = checkin.network.https_get(url) 
        j_obj = json.loads(result) 
        for item in j_obj.get("results", []):
            data.append({"lat":item['geometry']['location']['lat'], "lng":item['geometry']['location']['lng'], 'name':item['name'], 'vicinity':item.get('vicinity', "")})
        self.set_header('Content-Type',"application/json" )
        self.write(json.dumps(data))
