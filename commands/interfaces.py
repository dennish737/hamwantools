# Copyright (c) Dennis Harding
# Licensed under the MIT License.
import traceback
import re
import os
import sys

from commands.basecommand import BaseCommand
from nvd import CVEValidator

CVES_PATH = './assets/mikrotik_cpe_match.json'


# Licensed under the MIT License.
class Interfaces(BaseCommand):
    def __init__(self):
        self.__name__ = 'Interfaces'

    def run_ssh(self, sshc):

        try:
            data = self._ssh_data_ascii(sshc, ':put [/interface print]')
            chunks = data.split('\r\n')

        except Exception:
            print(traceback.format_exc())


        return {'raw_data': chunks,
                'suspicious': [],
                'recommendation': []}




