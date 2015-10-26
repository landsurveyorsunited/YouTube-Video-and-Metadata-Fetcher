from RequestBase import RequestBase
import datetime
import urlparse
import urllib
import dateutil.parser
import pprint
import time
import json
import os
import sys
from urllib2 import urlopen, unquote;
from urlparse import parse_qs;
import xmltodict
import pprint
#from project import db
import logging
import xml.etree.ElementTree as ET
#from project.models import YoutubeQuery, YouTubeVideo, VideoRepresentation
logger = logging.getLogger('tasks')

# TODO:
# parameters:
#   this file requires: (not yet tested or fixed)
#       'id', the id of the query to fetch the videos of,
#       workQueueItem should be as follows:
#           0: video id
#           1: the height (resolution) preffered to be dl'ed (e.g. 1080, 720)
#           2: get sound? Boolean value

class YouTubeVideoFetcher(RequestBase):
    video_ids = []
    dl_path = ''
    get_sound = False

    def initAdditionalStructures(self):
        dir = os.path.dirname(__file__)
        self.dl_path = os.path.join(dir, '../downloads/')

    def buildRequestURL(self, workQueueItem):
        return self.url+'?video_id='+workQueueItem[0]

    def initWorkQueue(self):
        #queries = YoutubeQuery.query.filter_by(id=id)
        #for video in queries.videos:
        #    self.video_ids += video.video_id
        item = {}
        item[0] = self.parameter
        item[1] = 720
        item[2] = True
        self.putWorkQueueItem(item)

    def handleRequestSuccess(self,workQueueItem, response):
        got_video = False
        got_sound = False
        video_id = workQueueItem[0]
        CHUNK = 16 * 1024
        path = os.path.join(self.dl_path, video_id)
        if workQueueItem[2]:
            self.get_sound = True

        #download manifest
        video_info = parse_qs(unquote(response.read().decode('utf-8')))
        manifest_url = video_info["dashmpd"][0]
        manifest_file = urlopen(manifest_url).read()
        manifest = xmltodict.parse(manifest_file)['MPD']['Period']['AdaptationSet']
        #print json.dumps(manifest, indent=2, separators=(',', ': '))
        
        #db
        #video_dbitem = YouTubeVideo.query.filter_by(id=video_id)

        for adaptation in manifest:
            mimeType = adaptation['@mimeType'].split('/')

            # Downloading sound, for now first quality listed (should be mp4)
            if mimeType[0] == 'audio' and self.get_sound and not got_sound:
                filename = path+'/'+video_id+'.'+('m4a' if mimeType[1] == 'mp4' else mimeType[1]+'s')
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
                with open(filename, "w") as f:
                    representations = adaptation['Representation']
                    if not isinstance(representations, list):
                        representations = [representations]

                    for representation in representations:
                        url = representation['BaseURL']['#text']
                        filesize = int(representation['BaseURL']['@yt:contentLength'])
                        response = urllib.urlopen(url)
                        dl = 0
                        print 'Downloading sound! > ' + video_id + ' ' + mimeType[1]
                        while True:
                            done = int(50 * dl / filesize)
                            dl += CHUNK
                            sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                            sys.stdout.flush()
                            chunk = response.read(CHUNK)
                            if not chunk: break
                            f.write(chunk)
                    
                    #updating db
                    #vr = VideoRepresentation(
                    #        video_id,
                    #        adaptation['@mimeType'],
                    #        representation['@bandwidth'],
                    #        representation['@codecs']
                    #        )
                    #video_dbitem.representations.append(vr)                    
                    #db.session.add(vr)

                    print 'DONE!'
                got_sound = True

            #download video file, quality as specified or if no match, get best
            #format should be mp4
            elif mimeType[0] == 'video':
                filename = path+'/'+video_id
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
                last_representation = {}
                representations = adaptation['Representation']
                if not isinstance(representations, list):
                    representations = [representations]
                for representation in representations:
                    last_representation = representation
                    if not str(representation['@height']) == str(workQueueItem[1]):
                        continue
                    else:
                        break
                filename += '.'+last_representation['@height']+'.'+('m4v' if mimeType[1] == 'mp4' else mimeType[1])
                with open(filename, "w") as f:
                    url = last_representation['BaseURL']['#text']
                    response = urllib.urlopen(url)
                    dl = 0
                    filesize = int(last_representation['BaseURL']['@yt:contentLength'])
                    print 'Downloading video! > ' + video_id + ' ' + last_representation['@height'] + 'p'
                    while True:
                        done = int(50 * dl / filesize)
                        dl += CHUNK
                        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                        sys.stdout.flush()
                        chunk = response.read(CHUNK)
                        if not chunk: break
                        f.write(chunk)
                    
                    #updating db
                    #vr = VideoRepresentation(
                    #        video_id,
                    #        adaptation['@mimeType'],
                    #        representation['@bandwidth'],
                    #        representation['@codecs'],
                    #        representation['@frameRate'],
                    #        representation['@height'],
                    #        representation['@width']
                    #        )
                    #video_dbitem.representations.append(vr)                    
                    #db.session.add(vr)

                    print 'DONE!'
                got_video = True

            if got_video and (got_sound or (not self.get_sound and not got_sound)):
                break
        #db.session.add(video_dbitem)
        #db.commit()

    def saveResult(self):
        pass

test = YouTubeVideoFetcher("http://www.youtube.com/get_video_info",'hFKacalDPjc',1,1,)
test = YouTubeVideoFetcher("http://www.youtube.com/get_video_info",'a6iTg_FUS74',1,1,)
test.work()