import json
import urllib

import httplib2

MAP_API_KEY = 'AIzaSyC_kU9l3eJ20DEPF2qq_XsQcz5ejxwbyns'
FOURSQUARE_CLIENT_ID = '1C1I0SPV4ZZ4YDKCGFAIJ3BLE0MLOM3RDW1SYKBKUSXLOXIE'
FOURSQUARE_CLIENT_SECRET = 'G0NPXGT4NMLOH0W2CWBZEA5HPAYKXUNAHD55YT21AGPMPXYM'


def getGeocodeLocation(s):
    p = urllib.parse.urlencode({'key': MAP_API_KEY, 'address': s})
    url = 'https://maps.googleapis.com/maps/api/geocode/json?' + p
    h = httplib2.Http()
    content = json.loads(h.request(url, 'GET')[1])
    lat, lng = content['results'][0]['geometry']['location'].values()
    return lat, lng


def findARestaurant(mealType, location):
    lat, lng = getGeocodeLocation(location)
    p = urllib.parse.urlencode({
        'client_id': FOURSQUARE_CLIENT_ID,
        'client_secret': FOURSQUARE_CLIENT_SECRET,
        'v': 20170101,
        'll': '{},{}'.format(lat, lng),
        # 'intent': 'browse',
        # 'radius': 100000,
        'limit': 1,
        'query': mealType,
    })
    url = 'https://api.foursquare.com/v2/venues/search?' + p
    h = httplib2.Http()
    content = json.loads(h.request(url, 'GET')[1])
    restaurant = content['response']['venues'][0]
    name = restaurant['name']
    address = ''
    for i in restaurant['location']['formattedAddress']:
        address += i + ', '

    # Get a photo
    venue_id = restaurant['id']
    p = urllib.parse.urlencode({
        'client_id': FOURSQUARE_CLIENT_ID,
        'client_secret': FOURSQUARE_CLIENT_SECRET,
        'v': 20170101,
        'limit': 1,
    })
    url = 'https://api.foursquare.com/v2/venues/' + venue_id + '/photos?' + p
    content = json.loads(h.request(url, 'GET')[1])
    photo = ('http://pixabay.com/get/8926af5eb597ca51ca4c/1433440765/' +
             'cheeseburger-34314_1280.png?direct')
    if content['response']['photos']['count']:
        photo = (
            content['response']['photos']['items'][0]['prefix'] +
            '300x300' +
            content['response']['photos']['items'][0]['suffix']
        )
    return (name, address, photo)


if __name__ == '__main__':
    findARestaurant('Pizza', 'Tokyo, Japan')
    findARestaurant('Tacos', 'Jakarta, Indonesia')
    findARestaurant('Tapas', 'Maputo, Mozambique')
    findARestaurant('Falafel', 'Cairo, Egypt')
    findARestaurant('Spaghetti', 'New Delhi, India')
    findARestaurant('Cappuccino', 'Geneva, Switzerland')
    findARestaurant('Sushi', 'Los Angeles, California')
    findARestaurant('Steak', 'La Paz, Bolivia')
    findARestaurant('Gyros', 'Sydney Australia')
