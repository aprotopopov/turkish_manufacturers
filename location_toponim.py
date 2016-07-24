import geocoder
# from googlemaps import Client

## Yandex geocoding

def get_location_yandex(address):
    # location = yandex.geocode(address)
    location = geocoder.yandex(address)
    if location.status != 'OK':
        raise Exception('Status code is not OK', location.status, address)
    return location

def get_lat_lng_yandex(location):
    # return location.latitude, location.longitude
    return str(tuple(float(n) for n in location.latlng))

def get_toponim_yandex(location):

    # address_list = location.address.split(", ")
    state = location.state
    sub_area = None
    if location.city:
        sub_area = location.city
    elif location.SubAdministrativeArea:
        sub_area = location.SubAdministrativeArea
    return '{}/{}'.format(sub_area, state)
    
## Google geocoding

def get_address_json(address, key):
    gmap = Client(key=key)
    adr_json = gmap.geocode(address)
    return adr_json


def get_lat_lng(adr_json):
    res = adr_json[0]
    lat = res['geometry']['location']['lat']
    lng = res['geometry']['location']['lng']
    return lat, lng
    

def get_toponim(adr_json):
    try:
        res = adr_json[0]
        d = {'city': None, 'province': None}
        for dict_adr in res['address_components']:
            # print(dict_adr)
            if 'administrative_area_level_1' in dict_adr['types']:
                d['province'] = dict_adr['short_name'].split(' ')[0]
            if 'locality' in res['types']:
                if 'locality' in dict_adr['types']:
                    d['city'] = dict_adr['short_name']
            elif 'administrative_area_level_2' in dict_adr['types']:
                d['city'] = dict_adr['short_name']

            toponim = '{}/{}'.format(d['city'], d['province'])

    except Exception as e:
        print(e)
        print(address)

    return toponim
    