#!/usr/bin/env python
#coding = utf-8
import json
import config
import time
import urllib
import tornado
import checkin.network

from redis import Redis

_client = Redis(config.REDIS_HOST, config.REDIS_PORT, db=15)
_KEY = "FEED"

class FeedHandler(tornado.web.RequestHandler):
    def get(self):
        data = []
        for item in  _client.zrevrange(_KEY, 0, 10, withscores = True):
            j_obj = json.loads(item[0])
            data.append({'data':j_obj['data'], 'created':int(item[1]), 'lat':float(j_obj['lat']), 'lng':float(j_obj['lng']), 'name':j_obj['name']})
        self.set_header('Content-Type',"application/json" )
        self.write(json.dumps(data))

    def post(self):
        data = self.get_argument('data', '')
        name = self.get_argument('name', '')
        lng   = self.get_argument('lng', -1)
        lat   = self.get_argument('lat', -1)
        _client.zadd(_KEY, json.dumps({'lng':lng, 'lat':lat, 'data':data, 'name':name}), int(time.time()))
        self.write("{}")

class NearbyHandler(tornado.web.RequestHandler):
    def get(self):
        lat = self.get_argument('lat', 0)
        lng   = self.get_argument('lng', 0)
        query   = self.get_argument('query', None) 
        offset  = int(self.get_argument('offset', 0))
        limit  = int(self.get_argument('limit', 12))
        data = []
        url = config.NEARBY_API+ "?types=(accounting|airport|amusement_park|aquarium|art_gallery|atm|bakery|bank|bar|beauty_salon|bicycle_store|book_store|bowling_alley|bus_station|cafe|campground|car_dealer|car_rental|car_repair|car_wash|casino|cemetery|church|city_hall|clothing_store|convenience_store|courthouse|dentist|department_store|doctor|electrician|electronics_store|embassy|establishment|finance|fire_station|florist|food|funeral_home|furniture_store|gas_station|general_contractor|grocery_or_supermarket|gym|hair_care|hardware_store|health|hindu_temple|home_goods_store|hospital|insurance_agency|jewelry_store|laundry|lawyer|library|liquor_store|local_government_office|locksmith|lodging|meal_delivery|meal_takeaway|mosque|movie_rental|movie_theater|moving_company|museum|night_club|painter|park|parking|pet_store|pharmacy|physiotherapist|place_of_worship|plumber|police|post_office|real_estate_agency|restaurant|roofing_contractor|rv_park|school|shoe_store|shopping_mall|spa|stadium|storage|store|subway_station|synagogue|taxi_stand|train_station|travel_agency|university|veterinary_care|zoo)&rankby=distance&language=zh-CN&sensor=true&location=%s,%s&key=%s"%(lat,lng,config.API_KEY)
        if query is not None:
            query = urllib.quote(query.encode('utf8'))
            url = url + "&name=%s"%(query)
        result = checkin.network.https_get(url) 
        j_obj = json.loads(result) 
        for idx, item in enumerate(j_obj.get("results", [])):
            if idx < offset:
                continue
            if idx >= offset + limit:
                break
            data.append({"lat":item['geometry']['location']['lat'], "lng":item['geometry']['location']['lng'], 'name':item['name'], 'vicinity':item.get('vicinity', "")})
        self.set_header('Content-Type',"application/json" )
        self.write(json.dumps(data))
