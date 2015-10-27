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
from project import db
import logging
import xml.etree.ElementTree as ET
from project.models import QueryVideoMM
logger = logging.getLogger('tasks')


class YouTubeMPDFetcher(RequestBase):

    def initAdditionalStructures(self):
        pass

    def buildRequestURL(self, workQueueItem):
        return self.url+'?video_id='+workQueueItem

    def initWorkQueue(self):
        videoIDs = db.session.query(QueryVideoMM).filter_by(QueryVideoMM.youtube_query_id==self.parameter)
        for video in queries.videoIDs:
            self.putWorkQueueItem(video.video_id)

    def handleRequestSuccess(self,workQueueItem, response):
        video_id = workQueueItem

        #download manifest
        video_info = parse_qs(unquote(response.read().decode('utf-8')))
        manifest_url = video_info["dashmpd"][0]
        manifest_file = urlopen(manifest_url).read()
        manifest = xmltodict.parse(manifest_file)['MPD']['Period']['AdaptationSet']

        for adaptation in manifest:
            mimeType = adaptation['@mimeType'].split('/')
            representations = adaptation['Representation']
            if not isinstance(representations, list):
                representations = [representations]
            if mimeType[0] == 'audio' and self.get_sound and not got_sound:
                for representation in representations:
                     
                    self.resultList[str(video_id)]= {}
                    self.resultList[str(video_id)]['video_id'] = video_id
                    self.resultList[str(video_id)]['mimeType'] = adaptation['@mimeType']
                    self.resultList[str(video_id)]['bandwidth'] = representation['@bandwidth']
                    self.resultList[str(video_id)]['codecs'] = representation['@codecs']
                    self.resultList[str(video_id)]['frameRate'] = ''
                    self.resultList[str(video_id)]['width'] = ''
                    self.resultList[str(video_id)]['height'] = ''
                    

            elif mimeType[0] == 'video':
                for representation in representations:
                    
                    self.resultList[str(video_id)]= {}
                    self.resultList[str(video_id)]['video_id'] = video_id
                    self.resultList[str(video_id)]['mimeType'] = adaptation['@mimeType']
                    self.resultList[str(video_id)]['bandwidth'] = representation['@bandwidth']
                    self.resultList[str(video_id)]['codecs'] = representation['@codecs']
                    self.resultList[str(video_id)]['frameRate'] = representation['@frameRate']
                    self.resultList[str(video_id)]['width'] = representation['@height']
                    self.resultList[str(video_id)]['height'] = representation['@width']
                    
    def saveResult(self): 
        
        if len(self.resultList) > 0:
            self.updateProgress('SAVING')
            from project.models import YoutubeVideoMeta
            from sqlalchemy.ext.compiler import compiles 
            from sqlalchemy.sql.expression import Insert
            @compiles(Insert)
            def replace_string(insert, compiler, **kw):
                s = compiler.visit_insert(insert, **kw)
                if 'replace_string' in insert.kwargs:
                    return str(s).replace("INSERT",insert.kwargs['replace_string'])
                return s
            
            t0 = time.time()
            logger.info("save video MPD")
            #http://docs.sqlalchemy.org/en/rel_0_9/core/connections.html?highlight=engine#sqlalchemy.engine.Connection.execute
            db.session.execute(YoutubeVideoMeta.__table__.insert(replace_string = 'INSERT OR REPLACE'),
                   [value for key,value in self.resultList.iteritems()]
                   )
            logger.info("Total time for " + str(len(self.resultList)) +" records " + str(time.time() - t0) + " secs")
            

        
