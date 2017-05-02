#!/usr/bin/env python3

import os
import sys, time
import getpass
import subprocess
import argparse
import socket
from paramiko import client
from scp import SCPClient

class RemoteControl:
    """
    To log in a remote device using ssh.
    And then copy remote videos from a remote directory that only has *.mp4 files
    """
    ssh = None
    scp = None
    addr = ''

    local_thumbnail_dir = ''
    remote_dir = ''

    def __init__(self, addr, dir):
        username, password = get_account(addr)

        self.ssh = client.SSHClient()
        self.ssh.set_missing_host_key_policy(client.AutoAddPolicy())

        try:
            print('>>> Connecting to {}...'.format(addr))
            self.ssh.connect(addr, username=username, password=password, timeout=10)
            self.ssh.exec_command('PATH=$PATH:/usr/local/bin')

        except socket.error:
            print('>>> Could not connect to remote device - {}\n'.format(addr))
            time.sleep(2)

        self.addr = addr
        self.local_thumbnail_dir = dir

    def check_videos(self):
        self.remote_dir = args.source
        command = 'cd {}; ls'.format(self.remote_dir)

        stdin, stdout, stderr = self.ssh.exec_command(command)
        video_names = [f.rstrip() for f in stdout]
        
        if len(video_names):
            for v in video_names:
                if '.mp4' in v:
                    self.vname = v
                    self.thname = v.replace('.mp4', '.png')

                    video_path = '{}/{}'.format(self.remote_dir, v)
                    self.scp_remote_video(remote_video_path=video_path)
                    self.write_message()

        else:
            print('No matching time data.')

    def scp_remote_video(self, remote_video_path):
        local_video_path = '/tmp/CopiedVideo.mp4'
        local_thumbnail_path = '{}/{}'.format(self.local_thumbnail_dir, self.thname)
        # print('local_thumbnail_path = {}'.format(local_thumbnail_path))
        if self.ssh:
            self.scp = SCPClient(self.ssh.get_transport())
            self.scp.get(remote_path=remote_video_path, local_path=local_video_path)

            FFmpegParser(video_path=local_video_path, thumbnail_path=local_thumbnail_path)

    def write_message(self):
        msg = '{} {} ==> {}/{}'.format(self.addr, self.vname, self.local_thumbnail_dir, self.thname)
        print(msg)


class FFmpegParser:
    """
    Use simple ffmpeg command to screenshot the video(s) from ssh/scp processes
    """

    def __init__(self, video_path, thumbnail_path):
        command = 'ffmpeg -i {} -ss 00:00:00.000 -vframes 1 {}'.format(video_path, thumbnail_path)
        print(command)
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


def make_local_dir(dir_name, ip='0.0.0.0'):
    path = '{}/{}'.format(dir_name, ip)
    os.makedirs(path, exist_ok=True)
    return path


def get_account(addr):
    print('>>> Remote Login as a Client - {}'.format(addr))
    username = input('\tUsername: ')
    password = getpass.unix_getpass(prompt='\tPassword: ')
    print()

    return username, password


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A script for generating thumbnails.')
    parser.add_argument('ip', action='store', help='ip address of device(s)')
    parser.add_argument('source', action='store', help='source directory')
    parser.add_argument('-d', action='store', help='output directory', default='/tmp')

    args = parser.parse_args()

    local_dir_name = make_local_dir(dir_name=args.d, ip=args.ip)

    try:
        rc = RemoteControl(addr=args.ip, dir=local_dir_name)
        rc.check_videos()

    except KeyboardInterrupt:
        print('\n\nKeyboardInterrupt: Exit')
        sys.exit(1)

    except EOFError:
        print('\n\nBye!')
        sys.exit(1)


