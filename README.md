A weewx driver for WS2000 weather stations.  

This works by continuously updating a text file using ambient's API.

You must set up your WS2000 to upload data to ambient weather,  and obtain API keys.   


## Approximate Setup for a Raspberry pi
(these steps probably aren't perfect, but give the general setup.  If I missed something let me know in the issues page)

* Install weewx with the Belchertown skin (https://github.com/poblabs/weewx-belchertown)

* Install mqtt extension (https://github.com/matthewwall/weewx-mqtt) and follow https://github.com/poblabs/weewx-belchertown#mqtt-and-mqtt-websockets-optional

* Create conda environment using `yml` file in this repo

* Clone and install the `aioambient` python module into this environment (https://github.com/bachya/aioambient)

* Update all required fields in the `.conf` and `.py` file in this repo, including usernames, passwords, API keys, and others.

* Install `ws2000.service` into `/etc/systemd/system`.   Change the launch command for your own setup.

* Run `mkdir /home/pi/ws2000data`

* Enable and start the `ws2000.service` via
```
sudo systemctl enable ws2000.service
sudo systemctl start ws2000.service
```

This will update the files in `/home/pi/ws2000data` constantly so they can be read by the weewx `FileParse` driver.   

* Update the weewx.conf file `/etc/weewx/weewx.conf` using the contents in this repo.

* Start weewx
```
sudo /etc/init.d/weewx start
```


