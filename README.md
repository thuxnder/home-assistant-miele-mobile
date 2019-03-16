# home-assistant-miele-mobile
Home Assistant component providing support for Miele@mobile enabled appliances

## Introduction

This project exposes state information of Miele appliances supporting Miele@Mobile to [Home Assistant](https://home-assistant.io). Communication between Home Assistant happens via local network, no cloud services involved. 
Miele appliance that support Miele@Mobile either via XKM3100W or nativly are supported.
If you need cloud service based integration please have a look at the Related section

## Setup
Communications with a Miele appliance require the correct GroupID and GroupKey which is used to secure the communication. You can get them by either extract them from a mobile app setup which would allows using the app and this API at the same time or by setting a new GroupID / GroupKey pair on the appliance.
### Set new keys (easy)
To configurare new keys the appliance needs to be on the wifi network and in register mode. The Miele@mobile app can be used to setup wifi, but it will also set GroupID and GroupKey. In this case the appliance can be removed from the app which will put it back into register mode but leave it on the wifi.

Once the appliance is on wifi and in register mode you can set new keys:
```
python -c 'from MieleHomeApi import easySetup; easySetup()'
```

### Use existing keys (advanced)
If you want to use the Miele@mobile app and this API at the same time you have to get the GroupID and GroupKey from the app. This can be achieved by sniffing them off the network when the app is setting up the appliance, look for a http request like this:
```
HTTP: PUT /Security/Commissioning/ HTTP/1.1
```
GroupID and GroupKey can be found in the request body in plain text.


## Relateded
* Alternative approach based on Miele's cloud service [Source](https://github.com/docbobo/home-assistant-miele/)
