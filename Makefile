binary:
	virtualenv --python=python2 venv
	./venv/bin/pip install pex
	./venv/bin/pex -r pex-requirements.txt  -e voicebase.__main__ -o vb
