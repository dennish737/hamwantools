
# Licensed under the MIT License.
import traceback
import re
import os
import sys

from commands.basecommand import BaseCommand
from nvd import CVEValidator




class BasicCommand(BaseCommand):
    def __init__(self):
        self.__name__ = 'BasicCommand'

    def run_ssh(self, sshc, command_text):
        command = ':put [{command__text}]'
        data = self._ssh_data(sshc,command)
        return {'raw_data': data,
                'suspicious': [],
                'recommendation': []}


    def run_ssh_ascii(self, sshc, command):
        command = ':put [{command__text}]'
        data = self._ssh_data_ascii(sshc,command)
        return {'raw_data': data,
                'suspicious': [],
                'recommendation': []}

