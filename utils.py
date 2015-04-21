import xbmc,xbmcplugin,xbmcgui,xbmcaddon
import urllib,datetime,json,sys,pytz
import time

import vars

#Get the current date and time in EST timezone
def nowEST():
    if hasattr(nowEST, "datetime"):
        return nowEST.datetime

    #Convert UTC to EST datetime
    timezone = pytz.timezone('America/New_York')
    utc_datetime = datetime.datetime.utcnow()
    est_datetime = utc_datetime + timezone.utcoffset(utc_datetime)
    log("UTC datetime: %s" % utc_datetime)
    log("EST datetime: %s" % est_datetime)

    #Save the result to a static variable
    nowEST.datetime = est_datetime

    return est_datetime

#Returns a datetime in the local timezone
#Thanks: http://stackoverflow.com/a/8328904/2265500
def toLocalTimezone(date):
    #Check settings
    if not vars.use_local_timezone:
        return date

    local_names = []
    if time.daylight:
        local_offset = time.altzone
        local_shortname = time.tzname[1]
    else:
        local_offset = time.timezone
        local_shortname = time.tzname[0]

    local_offset = datetime.timedelta(seconds = -local_offset)

    for name in pytz.all_timezones:
        timezone = pytz.timezone(name)
        if not hasattr(timezone, '_tzinfos'):
            #Skip, if some timezone doesn't have info
            continue

        #Go thru tzinfo and see if short name like EDT and offset matches
        for (utcoffset, daylight, tzname), _ in timezone._tzinfos.iteritems():
            if utcoffset == local_offset and tzname == local_shortname:
                local_names.append(name)

    #No locale found?
    if len(local_names) == 0:
        return date

    #Pick the first timezone name found
    local_timezone_name = local_names[0]

    #Get the actual timezone object
    local_timezone = pytz.timezone(local_timezone_name)

    #Get the NBA league pass timezone (EST)
    est_timezone = pytz.timezone('America/New_York')

    #Localize the date to include the offset, then convert to local timezone
    return est_timezone.localize(date).astimezone(local_timezone)

def isLiveUsable():
    # retrieve current installed version
    json_query = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_query = json.loads(json_query)
    version_installed = []
    if json_query.has_key('result') and json_query['result'].has_key('version'):
        version_installed  = json_query['result']['version']
        log("Version installed %s" %version_installed, xbmc.LOGDEBUG)

    return version_installed and version_installed['major'] >= 13

def log(txt, severity=xbmc.LOGINFO):
    if severity == xbmc.LOGDEBUG and not vars.debug:
        pass
    else:
        try:
            message = ('##### %s: %s' % (vars.__addon_name__,txt) )
            xbmc.log(msg=message, level=severity)
        except UnicodeEncodeError:
            message = ('##### %s: UnicodeEncodeError' %vars.__addon_name__)
            xbmc.log(msg=message, level=xbmc.LOGWARNING)

def getParams():
    param={}
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]
    return param

def addVideoListItem(name, url, iconimage):
    return addListItem(name,url,"",iconimage,False,True)

def addListItem(name, url, mode, iconimage, isfolder=False, usefullurl=False, customparams={}):
    if not hasattr(addListItem, "fanart_image"):
        settings = xbmcaddon.Addon( id="plugin.video.nba")
        addListItem.fanart_image = settings.getSetting("fanart_image")

    params = {
        'url': url,
        'mode': str(mode),
        'name': name
    }
    params.update(customparams) #merge params with customparams
    params = urllib.urlencode(params) #urlencode the params

    generated_url = "%s?%s" % (sys.argv[0], params)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )

    if addListItem.fanart_image:
        liz.setProperty('fanart_image', addListItem.fanart_image)

    if not isfolder:
        liz.setProperty("IsPlayable", "true")
    if usefullurl:
        generated_url = url

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=generated_url, listitem=liz, isFolder=isfolder)
    return liz
