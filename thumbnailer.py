#/usr/bin/env python3

import os, sys, time
from paramiko import client
from scp import SCPClient

class RemoteControl:
    ssh = None
    scp = None
    addr = ''
    remote_dir = ''

    def __init__(self, addr):
        username = sys.argv[1]
        password = sys.argv[2]

        self.ssh = client.SSHClient()
        self.ssh.set_missing_host_key_policy(client.AutoAddPolicy())
        self.ssh.connect(addr, username=username, password=password)

        self.addr = addr

    def check_videos(self):
        self.remote_dir = sys.argv[3]
        command = 'cd {}; ls'.format(path)

        stdin, stdout, stderr = self.ssh.exec_command(command)
        video_names = [f.rstrip() for f in stdout]

        if len(video_names):
            for v in video_names:
                self.vname = v

                video_path = '{}/{}'.format(self.remote_dir, v)
                self.scp_remote_video(remote_video_path=video_path)

        else:
            print('No matching time data.')

    def scp_remote_video(self, remote_video_path):







