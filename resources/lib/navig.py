# -*- coding: utf-8 -*-

import sys,urllib, urllib2, xbmcgui, xbmcplugin, xbmcaddon,re,cache, simplejson, xbmc
from BeautifulSoup import BeautifulSoup

ADDON = xbmcaddon.Addon()
ADDON_IMAGES_BASEPATH = ADDON.getAddonInfo('path')+'/resources/media/images/'
ADDON_FANART = ADDON.getAddonInfo('path')+'/fanart.jpg'
THEPLATFORM_CONTENT_URL = "https://edge.api.brightcove.com/playback/v1/accounts/5481942443001/videos/"

__handle__ = int(sys.argv[1])

def ajouterItemAuMenu(items):
    for item in items:
        if item['isDir'] == True:
            ajouterRepertoire(item)
            #xbmc.executebuiltin('Container.SetViewMode(512)') # "Info-wall" view. 
            
        else:
            ajouterVideo(item)
            #xbmc.executebuiltin('Container.SetViewMode('+str(xbmcplugin.SORT_METHOD_DATE)+')')
            #xbmc.executebuiltin('Container.SetSortDirection(0)')

    if items:
        if items[0]['forceSort']  :
            xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
            xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_DATE)
            



def ajouterRepertoire(show):
    #print "--Show image--"
    #print show
    
    nom = show['nom']
    url = show['url']
    iconimage =show['image']
    genreId = show['genreId']
    resume = remove_any_html_tags(show['resume'])
    fanart = show['fanart']
    filtres = show['filtres']

    if resume=='':
        resume = urllib.unquote(ADDON.getAddonInfo('id')+' v.'+ADDON.getAddonInfo('version'))
    if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
        resume = '[B]'+nom+'[/B][CR]'+urllib.unquote(resume)
    if iconimage=='':
        iconimage = ADDON_IMAGES_BASEPATH+'default-folder.png'

    """ function docstring """
    entry_url = sys.argv[0]+"?url="+url+\
        "&mode=1"+\
        "&filters="+urllib.quote(simplejson.dumps(filtres))
  
    is_it_ok = True
    liz = xbmcgui.ListItem(nom,iconImage=iconimage,thumbnailImage=iconimage)

    liz.setInfo(\
        type="Video",\
        infoLabels={\
            "Title": nom,\
            "plot":resume
        }\
    )
    setFanart(liz,fanart)

    is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=True)

    return is_it_ok

def setFanart(liz,fanart):
    if ADDON.getSetting('FanartEnabled') == 'true':
        if ADDON.getSetting('FanartEmissionsEnabled') == 'true':
            liz.setProperty('fanart_image', fanart)
        else:
            liz.setProperty('fanart_image', ADDON_FANART)


def ajouterVideo(show):
    name = show['nom']
    the_url = show['url']
    iconimage = show['image']
    url_info = 'none'
    finDisponibilite = show['endDateTxt']

    resume = show['resume'] #remove_any_html_tags(show['resume'] +'[CR][CR]' + finDisponibilite)
    duree = show['duree']
    fanart = show['fanart']
    sourceUrl = show['sourceUrl']
    annee = "" #show['startDate'][:4]
    premiere = show['startDate']
    episode = show['episodeNo']
    saison = show['seasonNo']
    
    is_it_ok = True
    entry_url = sys.argv[0]+"?url="+urllib.quote_plus(the_url)+"&sourceUrl="+urllib.quote_plus(sourceUrl)

    #if resume != '':
    #    if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
    #        resume = '[B]'+name.lstrip()+'[/B]'+'[CR]'+resume.lstrip() 
    #else:
    #    resume = name.lstrip()

    liz = xbmcgui.ListItem(\
        remove_any_html_tags(name), iconImage=ADDON_IMAGES_BASEPATH+"default-video.png", thumbnailImage=iconimage)
    liz.setInfo(\
        type="Video",\
        infoLabels={\
            "Title":remove_any_html_tags(name),\
            "Plot":remove_any_html_tags(resume, False),\
            "Duration":duree,\
            "Year":annee,\
            "Premiered":premiere,\
            "Episode":episode,\
            "Season":saison}\
    )
    liz.addContextMenuItems([('Informations', 'Action(Info)')])
    setFanart(liz,fanart)
    liz.setProperty('IsPlayable', 'true')

    is_it_ok = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=False)
    return is_it_ok

RE_HTML_TAGS = re.compile(r'<[^>]+>')
RE_AFTER_CR = re.compile(r'\n.*')

# Caching ???
def get_pl(the_url):
    """ function docstring """
    log("--get_pl----START--")

    req = urllib2.Request(the_url)
    req.add_header(\
                   'User-Agent', \
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'\
                   )
    req.add_header('Accept', 'application/json;pk=BCpkADawqM1hywVFkIaMkLk5QCmn-q5oGrQrwYRMPcl_yfP9blx9yhGiZtlI_V45Km8iey5HKLSiAuqpoa1aRjGw-VnDcrCVf86gFp2an1FmFzmGx-O-ed-Sig71IJMdGs8Wt9IyGrbnWNI9zNxYG_noFW5dLBdPV3hXo4wgTzvC2KvyP4uHiQxwyZw')
    req.add_header('Accept-Language', 'fr-CA,fr-FR;q=0.8,en-US;q=0.6,fr;q=0.4,en;q=0.2')
    req.add_header('Accept-Encoding', 'gzip, deflate')
    req.add_header('Connection', 'keep-alive')
    req.add_header('Pragma', 'no-cache')
    req.add_header('Cache-Control', 'no-cache')
    response = urllib2.urlopen(req)

    data = ""
    log("--encoding--")
    log(response.info().get('Content-Encoding'))

    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( response.read() )
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    else:
        data = response.read()

    response.close()

    log("--data--")
    #log(data)
    return data

def jouer_video(source_url):
    """ function docstring """
    check_for_internet_connection()
    uri = None

    media_uid=source_url

    log("--media_uid--")
    log(source_url)

    #data = cache.get_cached_content(source_url)

    # Obtenir JSON avec liens RTMP du playlistService
    video_json = simplejson.loads(\
       get_pl(\
           'https://edge.api.brightcove.com/playback/v1/accounts/5481942443001/videos/%s' % media_uid\
       )\
    )

    #play_list_item =video_json['playlistItems'][0]
    #
    ## Obtient les streams dans un playlist m3u8
    #m3u8_pl=cache.get_cached_content('https://mnmedias.api.telequebec.tv/m3u8/%s.m3u8' % play_list_item['refId'])
    #
    ## Cherche le stream de meilleure qualité
    #uri = obtenirMeilleurStream(m3u8_pl)

    #soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    #video = soup.find("video", { "id" : "videoPlayer" })

    # log("video")
    # log(video)

    #uri = THEPLATFORM_CONTENT_URL + video['data-video-id']

    # Plusieurs sources disponibles. Il faudrait prendre le meilleur.
    uri = video_json['sources'][0]['src']

    # lance le stream
    if uri:
        item = xbmcgui.ListItem(\
            "Titre",\
            iconImage=None,\
            thumbnailImage=None, path=uri)
        play_item = xbmcgui.ListItem(path=uri)
        xbmcplugin.setResolvedUrl(__handle__,True, item)
    else:
        xbmc.executebuiltin('Notification(%s,Incapable d''obtenir lien du video,5000,%s')

def check_for_internet_connection():
    """ function docstring """
    if ADDON.getSetting('NetworkDetection') == 'false':
        return
    return

def remove_any_html_tags(text, crlf=True):
    """ function docstring """
    text = RE_HTML_TAGS.sub('', text)
    text = text.lstrip()
    if crlf == True:
        text = RE_AFTER_CR.sub('', text)
    return text

def obtenirMeilleurStream(pl):
    maxBW = 0
    bandWidth=None
    uri = None
    for line in pl.split('\n'):
        if re.search('#EXT-X',line):
            bandWidth=None
            try:
                match  = re.search('BANDWIDTH=(\d+)',line)
                bandWidth = int(match.group(1))
            except :
                bandWidth=None
        elif line.startswith('http'):
            if bandWidth!=None:
                if bandWidth>maxBW:
                    maxBW = bandWidth
                    uri = line
    return uri

def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))