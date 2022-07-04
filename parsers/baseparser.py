import json
import pprint

import traceback
import sys

# parses config file to configure interfaces
class BaseParser(object):
    def __init__(self, mode, device_type):
        self.mode = mode
        self.device_type = device_type
        self.data = None

    def _get_dict_keys(self,dict):
        return dict.keys()

    def _get_dict_keys(self,dict):
        return dict.keys()

    def _command(self, command):
        return [command]

    def _actions(self, actions):
        commands = []
        command = ""

        for action in actions:
            for key, value in action.items():
                if key == "action":
                    if command != '':
                        commands.append(command)
                        command = ""
                    command += str(value + " ")
                elif key == "params":
                    for param_key, param_value in value.items():
                        if isinstance(param_value, list):
                            # change param value to a string
                            # map the list items:
                            for i in range(len(param_value)):
                                if param_value[i] in self.region_keys and self.region_parameters is not None:
                                    param_value[i] = self.region_parameters[param_value[i]]
                                if param_value[i] in self.router_keys and self.router_parameters is not None:
                                    param_value[i] = self.router_parameters[param_value[i]]
                            param_value = ','.join(param_value)
                        else:
                            if param_value in self.region_keys and self.region_parameters is not None:
                                param_value = self.region_parameters[param_value]
                            if param_value in self.router_keys and self.router_parameters is not None:
                                param_value = self.router_parameters[param_value]
                        command += str(param_key + "=" + param_value + " ")
        if len(command) > 0:
            commands.append(command)

        return commands


    def _addParams(self, region_params, router_params):
        if region_parameters is not None:
            self.region_parameters = region_params
        if router_parameters is not None:
            self.router_parameters = router_params

    def addParameters(self, region_parameters=None, router_parameters=None):
        if region_parameters is not None:
            self.region_parameters = region_parameters
            self.region_keys = list(self._get_dict_keys(region_parameters))
        if router_parameters is not None:
            self.router_parameters = router_parameters
            self.router_keys = list(self._get_dict_keys(router_parameters))


    def getTypeList(self):
        raise NotImplementedError

    def getActivities(self, device):
        raise NotImplementedError

