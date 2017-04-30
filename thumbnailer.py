#/usr/bin/env python3

import os, sys, time
import subprocess
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
    remote_dir = ''

    def __init__(self, addr):
        username = sys.argv[2]
        password = sys.argv[3]

        self.ssh = client.SSHClient()
        self.ssh.set_missing_host_key_policy(client.AutoAddPolicy())
        self.ssh.connect(addr, username=username, password=password)

        self.addr = addr

    def check_videos(self):
        self.remote_dir = sys.argv[4]
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

                else:
                    print('No matching time data.')

    def scp_remote_video(self, remote_video_path):
        local_video_path = '/tmp/CopiedVideo.mp4'
        local_thumbnail_path = '{}/{}'.format(sys.argv[5], self.thname)

        if self.ssh:
            self.scp = SCPClient(self.ssh.get_transport())
            self.scp.get(remote_path=remote_video_path, local_path=local_video_path)

            FFmpegParser(video_path=local_video_path, thumbnail_path=local_thumbnail_path)


class FFmpegParser:
    """
    Use simple ffmpeg command to screenshot the video(s) from ssh/scp processes
    """

    def __init__(self, video_path, thumbnail_path):
        command = 'ffmpeg -i {} -ss 00:00:15.000 -vframes 1 {}'.format(video_path, thumbnail_path)
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)



if __name__ == '__main__':
   rc = RemoteControl(addr=sys.argv[1])
   rc.check_videos()


