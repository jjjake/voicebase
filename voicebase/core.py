from __future__ import unicode_literals, print_function
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import hashlib
import json

import requests
requests.packages.urllib3.disable_warnings()
from requests.auth import HTTPBasicAuth
import magic


class VoiceBase(object):

    def __init__(self, identifier=None, filename=None, config_file=None, checksum=None, media_id=None):
        endpoint = 'https://apis.voicebase.com/v2-beta/media'

        self.identifier = identifier
        self.filename = filename
        self.media_id = media_id

        # Load config.
        cp = configparser.ConfigParser()
        cp.read(config_file)
        self.password = cp.get('DEFAULT', 'Password')
        self.api_key = cp.get('DEFAULT', 'ApiKey')
        # V2 API Auth.
        self.auth = HTTPBasicAuth(self.api_key, self.password)
        self.auth_token = self.get_auth_token()
        self.session = requests.Session()
        self.session.headers.update(
            dict(Authorization='Bearer {0}'.format(self.auth_token)))

        self.endpoint = endpoint
        self.external_id = checksum if checksum else self.get_md5()
        print(self.get_md5(), self.external_id)
        if self.external_id:
            #self.title = '{0}/{1}'.format(self.identifier, self.filename).strip('./')
            self.title = self.filename.strip('./')

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

    def upload_media(self):
        # V2 API
        metadata = {
            'metadata': {
                'external': {
                    'id': self.external_id
                }
            }
        }
        configuration = {
            'configuration': {
                'transcripts': {
                    'engine': 'premium'
                }
            }
        }
        data = dict(
            metadata=json.dumps(metadata),
            configuration=json.dumps(configuration),
        )

        m = magic.Magic(mime=True)
        mime_type = m.from_file(self.filename)

        with open(self.filename) as fh:
            _r = requests.Request(b'POST',
                                 self.endpoint,
                                 data=data,
                                 headers=self.session.headers,
                                 files=[('media', (self.filename, fh, mime_type))])
            p = _r.prepare()
            r = self.session.send(p)
            #r = requests.post(self.endpoint,
            #                  data=data,
            #                  files=[('media', (self.filename, fh, mime_type))])
            #print(self.endpoint, self.session.headers, data, self.filename)
            r.raise_for_status()
        return r

    def get_file_status(self):
        p = dict(externalId=self.external_id)
        r = self.session.get(self.endpoint, params=p)
        return r

    def _get(self, target=None, headers=None, params=None):
        if not self.media_id:
            j = self.get_file_status().json()
            self.media_id = j['media'][0]['mediaId']
        url = '{0}/{1}'.format(self.endpoint, self.media_id)
        if target:
            url += '/{0}/latest'.format(target)
        r = self.session.get(url, headers=headers, params=params)
        return r

    def get_file_transcript(self, format=None):
        format = 'srt' if not format else format
        h = dict(Accept='text/{0}'.format(format))
        return self._get('transcripts', headers=h)

    def get_file_analytics(self):
        return self._get()

    def list(self, status=None, upload_collection=None):
        return self.session.get(self.endpoint)
