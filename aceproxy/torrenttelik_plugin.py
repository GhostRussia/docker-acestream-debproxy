# -*- coding: utf-8 -*-
__author__ = 'miltador'
'''
Torrent-telik.com Playlist Downloader Plugin
(based on ytv plugin by ValdikSS)
http://ip:port/torrent-telik || http://ip:port/torrent-telik/?type=ttv = torrent-tv playlist
http://ip:port/torrent-telik/?type=mob_ttv = torrent-tv mobile playlist
http://ip:port/torrent-telik/?type=allfon = allfon playlist
'''
import json
import logging
import urllib2
import urlparse
from modules.PluginInterface import AceProxyPlugin
from modules.PlaylistGenerator import PlaylistGenerator
import config.torrenttelik as config


class Torrenttelik(AceProxyPlugin):

    handlers = ('torrent-telik', 'torrent-telik-18', 'torrent-telik-sex',)

    logger = logging.getLogger('plugin_torrenttelik')
    playlist = None

    def downloadPlaylist(self, url):
        try:
            req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
            Torrenttelik.playlist = urllib2.urlopen(req, timeout=10).read()
            Torrenttelik.playlist = Torrenttelik.playlist.split('\xef\xbb\xbf')[1]     # garbage at the beginning
            Torrenttelik.playlist = Torrenttelik.playlist.replace(',\r\n]}', '\r\n]}') # excess comma at the end
        except:
            Torrenttelik.logger.error("Can't download playlist!")
            return False

        return True

    def handle(self, connection, headers_only=False):

        hostport = connection.headers['Host']

        connection.send_response(200)
        connection.send_header('Content-Type', 'application/x-mpegurl')
        connection.end_headers()
        
        if headers_only:
            return

        query = urlparse.urlparse(connection.path).query
        pathUrl = urlparse.urlparse(connection.path).path.replace('/', '')
        self.params = urlparse.parse_qs(query)

        url = None
        list_type = self.getparam('type')
        if not list_type or list_type.startswith('ttv'):
            url = config.url_ttv
        elif list_type.startswith('mob_ttv'):
            url = config.url_mob_ttv
        elif list_type.startswith('allfon'):
            url = config.url_allfon

        if not self.downloadPlaylist(url):
            connection.dieWithError()
            return

        # Un-JSON channel list
        try:
            jsonplaylist = json.loads(Torrenttelik.playlist)
        except Exception as e:
            Torrenttelik.logger.error("Can't load JSON! " + repr(e))
            return

        try:
            channels = jsonplaylist['channels']
        except Exception as e:
            Torrenttelik.logger.error("Can't parse JSON! " + repr(e))
            return

        add_ts = False
        try:
            if connection.splittedpath[2].lower() == 'ts':
                add_ts = True
        except:
            pass

        playlistgen = PlaylistGenerator()

        for channel in channels:
            isSexChanel = channel.get('cat', '').lower().startswith(u"эрот")
            if pathUrl == 'torrent-telik' and isSexChanel:
                continue
            elif pathUrl == 'torrent-telik-sex' and not isSexChanel:
                continue
            
            channel['group'] = channel.get('cat', '')
            playlistgen.addItem(channel)

        Torrenttelik.logger.debug('Exporting')
        header = '#EXTM3U url-tvg="%s" tvg-shift=%d\n' %(config.tvgurl, config.tvgshift)
        exported = playlistgen.exportm3u(hostport, header=header, add_ts=add_ts, fmt=self.getparam('fmt'))
        exported = exported.encode('utf-8') 
        connection.wfile.write(exported)
 
    def getparam(self, key):
        if key in self.params:
            return self.params[key][0]
        else:
            return None
