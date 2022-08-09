import json
import pprint
import logging

from libs.baseparser import BaseParser

# parses config file to configure interfaces
class ParseInterfaces(BaseParser):
    def __init__(self, mode, device_type, template_file):
        super().__init__(mode, device_type)
        self.__name__ = 'ParseInterfaces'

        self.section = 'interfaces'
        self.region_parameters = None
        self.router_parameters = None
        self.region_keys = []
        self.router_keys = []
        with open(template_file) as json_file:
            raw_data = json.load(json_file)[mode][device_type]
            if self.section in raw_data:
                self.data = raw_data[self.section]
            else:
                self.data = None
        logging.debug("starting {}".format(self.__name__))

    def getTypeList(self):
        type_list = list(self._get_dict_keys(self.data))
        return type_list

    def getActivities(self, device):
        activities = self.data[device]["activities"]
        activities_list = list(self._get_dict_keys(activities))
        return activities_list

    def parseSettings(self, device, activity, region_params=None, router_params=None):
        commands = []
        activities_list = self.data[device]["activities"][activity]
        for key, value in activities_list.items():
            if key == 'command':
                commands.extend(self._command(value))
            elif key == 'actions':
                commands.extend(self._actions(value))
        #print(commands)
        return commands


if __name__ == '__main__':

    # used for testing

    from libs.dbtools import DbSqlite

    db_file = "../data/region9_hamwan.sqlite3"
    template_file = '../templates/ptp_config.json'
    mode = 'config'
    device_type = 'PTP'

    operation = 'config'
    device_name = "SPODEM.PTP1"
    region = 9

    db = DbSqlite()
    db.connect(db_file)
    ip, device_type = db.getDeviceIP(device_name)
    print(device_name, ip, device_type)
    print("------------")

    region_params = db.getRegionInfo(region)
    print(region_params)
    print("------------")
    router_params = None
    if device_type == 'PTP':
        router_params = db.getPTPParams(device_name)
        print(router_params)
    print("------------")

    p = ParseInterfaces(mode,device_type, template_file)
    p.addParameters(region_params, router_params)
    print("region_keys:", p.region_keys)
    print("router_keys:", p.router_keys)

    interfaces = p.getTypeList()
    print(interfaces)
    commands = []
    print("--------------------")
    for interface in interfaces:
        activities = p.getActivities(interface)
        #print(activities)
        for activity in activities:
            commands.extend(p.parseSettings(interface, activity, region_params, router_params ))

    for command in commands:
        print(command)


