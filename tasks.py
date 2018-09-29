# -*- coding: utf-8 -*-

import os
import shutil
import sys
try:
    import socketserver
except ImportError:
    import SocketServer as socketserver

from invoke import task
from invoke.util import cd
from pelican.server import ComplexHTTPRequestHandler

ssh_user = 'tiarno'
ssh_host = 'reachtim.com'
ssh_port = 22
ssh_target_dir = '/home/tiarno/webapps/reachtim'

CONFIG = {
    'deploy_path': 'reachtim',
    'production': f'{ssh_user}@{ssh_host}:{ssh_port}',
    'dest_path': ssh_target_dir,
    'port': 8000,
    }

@task
def clean(c):
    """Remove generated files"""
    if os.path.isdir(CONFIG['deploy_path']):
        shutil.rmtree(CONFIG['deploy_path'])
        os.makedirs(CONFIG['deploy_path'])

@task
def build(c):
    """Build local version of site"""
    c.run('pelican -s pelicanconf.py')

@task
def rebuild(c):
    """`build` with the delete switch"""
    c.run('pelican -d -s pelicanconf.py')

@task
def regenerate(c):
    """Automatically regenerate site upon file modification"""
    c.run('pelican -r -s pelicanconf.py')

@task
def serve(c):
    """Serve site at http://localhost:8000/"""
    os.chdir(CONFIG['deploy_path'])

    class AddressReuseTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(
        ('', CONFIG['port']),
        ComplexHTTPRequestHandler)

    sys.stderr.write('Serving on port {port} ...\n'.format(**CONFIG))
    server.serve_forever()

@task
def reserve(c):
    """`build`, then `serve`"""
    build(c)
    serve(c)

@task
def preview(c):
    """Build production version of site"""
    c.run('pelican -s publishconf.py')

@task
def publish(c):
    """Publish to production via rsync"""
    c.run('pelican -s publishconf.py')
    c.run(
        'rsync --delete --exclude ".DS_Store" -pthrvz -c '
        '{} {production}:{dest_path}'.format(
            CONFIG['deploy_path'].rstrip('/') + '/',
            **CONFIG))
