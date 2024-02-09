#!/usr/bin/env python
""""
Copyright (C) 2022 twyleg
"""
import os
import time
import argparse
from pathlib import Path
from os.path import getmtime

global DEVICE


#
# Utils
#
def read_timestamp_file(filepath='.timestamp') -> float:
    try:
        return getmtime(filepath)
    except FileNotFoundError:
        return 0


def create_or_update_timestamp_file(filepath='.timestamp'):
    with open(filepath, 'w') as f:
        f.write('')


def delete_timestamp_file(filepath='.timestamp'):
    os.remove(filepath)


#
# Actions
#

def upload(src: str, dst=''):
    os.system(f'ampy --port {DEVICE} put {src} {dst}')


def update(src: str, dst_dir: str, basedir: str, reference_timestamp: float):
    p = Path(basedir)
    for src_file in p.glob(src):
        relative_filepath_to_basedir = src_file.relative_to(basedir)
        target_path = dst_dir / relative_filepath_to_basedir
        timestamp = getmtime(src_file)
        skip = timestamp < reference_timestamp
        print('{}: {} -> {}'.format('SKIP' if skip else 'UPDATE', src_file, target_path))
        if not skip:
            upload(src_file, target_path)


def run(filepath: str):
    print(f'Run script: {filepath}')
    os.system(f'ampy --port {DEVICE} run {filepath}')


def ls(path: str):
    print(f'ls: {path}')
    os.system(f'ampy --port {DEVICE} ls {path}')


def mkdir(path: str):
    print(f'mkdir: {path}')
    os.system(f'ampy --port {DEVICE} mkdir --exists-okay {path}')


def reset():
    print('reset')
    os.system(f'ampy --port {DEVICE} reset')


#
# Subcommands
#

def command_install_dependencies(args):
    print('command: install_dependencies')
    upload('config.json')
    run('scripts/install_dependencies.py')
    reset()


def command_upload(args):
    print('command: upload')
    reference_timestamp = read_timestamp_file()
    update('**/*.py', '.', 'webserver', reference_timestamp)
    update('**/*.json', '.', 'webserver', reference_timestamp)
    create_or_update_timestamp_file()
    reset()


def command_ls(args):
    print('command: ls')
    ls('/')


def command_serial(args):
    os.system(f'python -m serial.tools.miniterm {DEVICE} 115200')


if __name__ == "__main__":
    #
    # Scan for cli arguments
    #
    parser = argparse.ArgumentParser(description='Flash utility based on esptool and ampy.')
    subparsers = parser.add_subparsers(title='commands')

    parser.add_argument('-d', '--device', dest='device', default='/dev/ttyUSB0',
                        help='Serial device file.')

    upload_parser = subparsers.add_parser('upload')
    upload_parser.set_defaults(func=command_upload)

    upload_parser = subparsers.add_parser('ls')
    upload_parser.set_defaults(func=command_ls)

    upload_parser = subparsers.add_parser('serial')
    upload_parser.set_defaults(func=command_serial)

    args = parser.parse_args()
    DEVICE = args.device

    args.func(args)