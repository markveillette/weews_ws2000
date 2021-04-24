"""Run an example script to quickly test."""
import asyncio
import logging

from aiohttp import ClientSession

from aioambient import Client
from aioambient.errors import WebsocketError

_LOGGER = logging.getLogger()

# ENTER YOUR API & APP KEYS
API_KEY = # ENTER API KEY
APP_KEY = # ENTER APP KEY

import json

past_rain = None
past_time = None
def get_weewx_data_dict(data,outdir='/home/pi/ws2000data',rate_interval=60.0):
    """
    data is json containing data

    data={'dateutc': 1609286640000, 'tempinf': 66.7, 'battin': 1, 'humidityin': 41,
    'baromrelin': 30.077, 'baromabsin': 30.077, 'tempf': 25, 'battout': 1,
    'humidity': 36, 'winddir': 23, 'winddir_avg10m': 26, 'windspeedmph': 0,
    'windspdmph_avg10m': 0.7, 'windgustmph': 1.1, 'maxdailygust': 18.3,
    'hourlyrainin': 0, 'eventrainin': 0, 'dailyrainin': 0, 'weeklyrainin': 0,
    'monthlyrainin': 0, 'yearlyrainin': 0, 'solarradiation': 0, 'uv': 0,
    'feelsLike': 25, 'dewPoint': 1.86, 'feelsLikein': 66.7, 'dewPointin': 42.2,
    'tz': 'America/New_York', 'date': '2020-12-30T00:04:00.000Z', 'macAddress':
    'F0:08:D1:07:16:A7'}

    rate_interval is the interval used to compute rain rate.  E.g. if rate_interval=60,
    then rain is rain per minute.

    """
    global past_rain,past_time
    # map weewx keys to ambient keys
    key_map = {
        'barometer':'baromabsin',
        'dewpoint':'dewPoint',
        'inDewpoint':'dewPointin',
        'inHumidity':'humidityin',
        'inTemp':'tempinf',
        'inTempBatteryStatus':'battin',
        'outHumidity':'humidity',
        'outTemp':'tempf',
        'outTempBatteryStatus':'battout',
        'pressure':'baromrelin',
        'rain':'yearlyrainin', # Make sure you adjust!
        'rainBatteryStatus':'battout',
        'UV':'uv',
        'uvBatteryStatus':'battout',
        'windBatteryStatus':'battout',
        'windchill':'feelsLike',
        'windDir':'winddir_avg10m',
        'windGust':'windgustmph',
        'windGustDir':'winddir',
        'windSpeed':'windspdmph_avg10m'
    }

    out_data = {
        'dateTime':int(data['dateutc']//1000),
    }

    for wk,ak in key_map.items():
        out_data[wk]=data.get(ak,None)

    # Rain calculation: weewx expects rain per reporting interval, so
    # need to convert accumulated rain to this rate.
    if past_rain is not None:
        out_data['rain']-=past_rain
        dt=float(out_data['dateTime'])-past_time
        # Convert accumlulated rain to rain rate
        if dt>0:
            out_data['rain']/=(dt/rate_interval) 
        else:
            out_data['rain']=0.0 # same obs repeated?
    else:
        out_data['rain']=0.0
    if out_data['rain']<0:
        out_data['rain']=0.0 # just in case of roll over..
    past_rain=data[key_map['rain']]
    past_time=float(out_data['dateTime'])

    fname='ws2000_latest'
    
    with open(outdir+'/'+fname+'.txt','w') as f:
        for i,(k,v) in enumerate(out_data.items()):
            e ='' if i==len(out_data)-1 else '\n'
            f.write('%s=%s%s' % (k,str(v),e))
    tname = str(out_data['dateTime'])
    with open(outdir+'/'+fname+'.json','w') as f:
        json.dump(data, f)

    return out_data



def print_data(data):
    """Print data as it is received."""
    _LOGGER.info("WS-2000 Data received")
    out_data = get_weewx_data_dict(data)

def print_goodbye():
    """Print a simple "goodbye" message."""
    _LOGGER.info("Client has disconnected from the websocket")


def print_hello():
    """Print a simple "hello" message."""
    _LOGGER.info("Client has connected to the websocket")


def print_subscribed(data):
    """Print subscription data as it is received."""
    _LOGGER.info("Client has subscribed")


async def main() -> None:
    """Run the websocket example."""
    logging.basicConfig(level=logging.INFO)

    async with ClientSession() as session:
        client = Client(API_KEY, APP_KEY, session=session)

        client.websocket.on_connect(print_hello)
        client.websocket.on_data(print_data)
        client.websocket.on_disconnect(print_goodbye)
        client.websocket.on_subscribed(print_subscribed)

        try:
            await client.websocket.connect()
        except WebsocketError as err:
            _LOGGER.error("There was a websocket error: %s", err)
            return

        while True:
            #_LOGGER.info("Simulating some other task occurring...")
            await asyncio.sleep(5)


loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
