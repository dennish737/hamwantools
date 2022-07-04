
# Licensed under the MIT License.
import traceback
import re
import os
import sys

from commands.basecommand import BaseCommand
from nvd import CVEValidator



# Licensed under the MIT License.
class Identity(BaseCommand):
    def __init__(self):
        self.__name__ = 'Identity'

    def run_ssh(self, sshc):

        try:
            data = self._ssh_data_ascii(sshc, ':put [/system identity get name]')
            data = data.rstrip()

        except Exception:
            print(traceback.format_exc())

        return {'raw_data': data,
                'suspicious': [],
                'recommendation': []}
