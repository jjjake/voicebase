#!/home/jake/work/voicebase/venv/bin/python
from __future__ import unicode_literals, print_function
import sys
from glob import glob
import time
import json

from voicebase import VoiceBase
from slacker import Slacker
import audioread


T = time.time()
LIMIT_PER_MINUTE = 6000
LENGTH_UPLOADED = 0


def notify_slack(message):
    with open('/home/jake/.config/slack.yml') as f:
        j = json.load(f)
    slack = Slacker(j['token'])
    slack.chat.post_message('@jake', message, 'voicebase')


def get_duration(fname):
    with audioread.audio_open(fname) as f:
        return f.duration


def limit_per_minute_reached():
    global LENGTH_UPLOADED
    global LIMIT_PER_MINUTE
    global T
    if (time.time()-T > 60) and (LENGTH_UPLOADED < LIMIT_PER_MINUTE):
        return False
    return True


def reset_timer():
    global LENGTH_UPLOADED
    global T
    LENGTH_UPLOADED = 0
    T = time.time()


if __name__ == '__main__':
    for p in glob('*/**mp3'):
        if limit_per_minute_reached() is False:
            reset_timer()

        identifier, fname = p.split('/')

        # Throttle uploads.
        if LENGTH_UPLOADED >= LIMIT_PER_MINUTE:
            time_to_sleep = 60-(time.time()-T)
            print('warning: max uploaded, sleeping for {0}'.format(time_to_sleep),
                  file=sys.stderr)
            try:
                time.sleep(time_to_sleep)
            except:
                time.sleep(60)
            reset_timer()

        # Upload.
        try:
            vb = VoiceBase(identifier, p, '/home/jake/.config/vb.ini')
            r = vb.get_file_status()
            j = r.json()
            if not j.get('media'):
                r = vb.upload_media()
                j = r.json()
                j['identifier'] = identifier
                j['file'] = fname
                j['external_id'] = vb.external_id
                print(json.dump(j))
                LENGTH_UPLOADED += get_duration(p)
                continue
            print('info: skipping {0}/{1} - already uploaded?'.format(identifier, fname),
                  file=sys.stderr)
        except Exception as exc:
            print('error: skipping {0}/{1} - '
                  'exception: {2}'.format(identifier, fname,str(exc)), file=sys.stderr)
            continue

    notify_slack('finished voicebase submission.')
