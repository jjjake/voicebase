from __future__ import unicode_literals, print_function
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import sys
import hashlib

import requests
requests.packages.urllib3.disable_warnings()
from requests.auth import HTTPBasicAuth


class VoiceBase(object):

    def __init__(self, identifier=None, filename=None, config_file=None):
        # Note: The v2 API is currently in beta. It lacks support
        # it mostly only supports uploading at the moment.
        v1_endpoint = 'https://api.voicebase.com/services'
        endpoint = 'https://apis.voicebase.com/v2-beta/media'

        self.identifier = identifier
        self.filename = filename

        # Load config.
        cp = configparser.ConfigParser()
        cp.read(config_file)
        self.password = cp.get('DEFAULT', 'Password')
        self.api_key = cp.get('DEFAULT', 'ApiKey')
        # V2 API Auth.
        #self.auth = HTTPBasicAuth(self.api_key, self.password)
        #self.auth_token = self.get_auth_token()

        self.endpoint = endpoint
        self.v1_endpoint = v1_endpoint
        self.external_id = self.get_md5()
        self.title = '{0}/{1}'.format(self.identifier, self.filename)

    def get_md5(self):
        hash = hashlib.md5()
        if not self.filename:
            return
        with open(self.filename) as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash.update(chunk)
        return hash.hexdigest()

    def get_auth_token(self):
        u = 'https://apis.voicebase.com/v2-beta/access/users/admin/tokens'
        r = requests.get(u, auth=self.auth)
        j = r.json()
        return j.get('tokens', [{}])[0].get('token')

    def upload_media(self, transcript_type=None):
        # V2 API
        #h = dict(Authorization='Bearer {0}'.format(self.auth_token))
        #print(h)
        #data = dict(
        #    config=self.config,
        #    metadata=dict(externalId=self.external_id),
        #)
        #
        #with open(self.filename) as fh:
        #    #r = requests.post(self.endpoint, data=data, files=[('media', (self.filename, fh, 'audio/mpeg'))])
        #    r = requests.post(self.endpoint, files=[('media', (self.filename, fh, 'audio/mpeg'))], auth=self.auth)
        #    #r = requests.post(self.endpoint, data=data, files={'media': fh})
        #    print(r.content)
        #    r.raise_for_status()

        transcriptType = 'machine_best' if not transcript_type else transcript_type
        data = dict(
            version='1.1',
            apikey=self.api_key,
            password=self.password,
            externalID=self.external_id,
            action='uploadMedia',
            transcriptType=transcript_type,
            title=self.title,
            sourceUrl='https://archive.org/download/{0}.mp3'.format(self.identifier),
            lang='en',
        ) 
        with open(self.filename) as fh:
            r = requests.post(self.v1_endpoint, data=data, files={'file': fh})
            r.raise_for_status()
        print(r.content.decode('utf-8'))

    def _v1_get(self, action, params=None):
        p = dict(
            version='1.1',
            apikey=self.api_key,
            password=self.password,
            action=action,
            externalID=self.external_id,
        )
        if params:
            p.update(params)
        r = requests.get(self.v1_endpoint, params=p)
        r.raise_for_status()
        return r

    def get_file_status(self):
        r = self._v1_get('getFileStatus')
        print(r.content.decode('utf-8'))

    def get_file_metadata(self):
        r = self._v1_get('getFileMetadata')
        print(r.content.decode('utf-8'))

    def get_file_analytics(self):
        r = self._v1_get('getFileAnalytics')
        print(r.content.decode('utf-8'))

    def get_transcript(self, format=None):
        format = 'srt' if not format else format
        params = dict(format=format)
        r = self._v1_get('getTranscript', params=params)
        print(r.content.decode('utf-8'))

    def list(self, status=None, upload_collection=None):
        status = 'MACHINECOMPLETE' if not status else status
        params = dict(status=status)
        if upload_collection:
            params['uploadCollection'] = upload_collection
        r = self._v1_get('list', params=params)
        print(r.content.decode('utf-8'))
