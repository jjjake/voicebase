#!/usr/bin/env python
"""Usage: vb [IDENTIFIER] [FILE] [options...]

IA Voice Base cli.

Arguments:
    IDENTIFIER   Archive.org IDENTIFIER in which the given file is from.
    FILE         FILE to transcribe. 

Options:
    -h --help
    -c --config CONFIG   Config file to use [default: vb.ini]
    -u --upload          Upload the FILE for transcription.
    -g --get-status      Get the status of FILE.
    -m --get-metadata    Get Voice Base FILE metadata.
    -t --get-transcript  Get Voice Base FILE metadata.
"""
from __future__ import unicode_literals, print_function

from docopt import docopt

from voicebase.core import VoiceBase


if __name__ == '__main__':
    args = docopt(__doc__)

    vb_item = VoiceBase(args['IDENTIFIER'], args['FILE'], args['--config'][0])
    if args['--upload']:
        vb_item.upload_media()
    elif args['--get-status']:
        vb_item.get_file_status()
    elif args['--get-metadata']:
        vb_item.get_file_metadata()
    elif args['--get-transcript']:
        vb_item.get_transcript()
    else:
        vb_item.list()
