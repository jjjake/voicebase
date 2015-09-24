#!/usr/bin/env python
"""Usage: vb [IDENTIFIER] [FILE] [options] ...

IA Voice Base cli.

Arguments:
    IDENTIFIER   Archive.org IDENTIFIER in which the given file is from.
    FILE         FILE to transcribe. 

Options:
    -h --help
    -c --config CONFIG           Config file to use. [default: vb.ini]
    -m --media-id ID             MediaId for FILE.
    -u --upload                  Upload the FILE for transcription.
    -g --get-status              Get the status of FILE.
    -t --get-transcript FORMAT   Get Voice Base FILE transcript.
    -G --get-analytics           Get Voice Base FILE topics, keywords, etc..
"""
from __future__ import unicode_literals, print_function

from docopt import docopt

from voicebase.core import VoiceBase


def main():
    args = docopt(__doc__)

    media_id = args['--media-id'][0] if args['--media-id'] else None
    vb = VoiceBase(args['IDENTIFIER'],
                   args['FILE'],
                   args['--config'][0],
                   media_id)

    if args['--upload']:
        r = vb.upload_media()
    elif args['--get-status']:
        r = vb.get_file_status()
    elif args['--get-transcript']:
        r = vb.get_file_transcript(args['--get-transcript'][0])
    elif args['--get-analytics']:
        r = vb.get_file_analytics()
    elif args['--media-id']:
        r = vb.get_file_analytics()
    else:
        r = vb.list()
    print(r.content)
    #print(r.content.decode('utf-8'))


if __name__ == '__main__':
    main()
