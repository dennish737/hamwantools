import json
import pprint
import logging

from parsers.baseparser import BaseParser

#parse config file for global ip settings
class ParseSystem(BaseParser):
    def __init__(self, mode, device_type, template_file):
        super().__init__(mode, device_type)
        self.__name__ = 'ParseSystem'

        self.section = 'system'

        self.region_parameters = None
        self.router_parameters = None
        self.region_keys = []
        self.router_keys = []
        with open(template_file) as json_file:
            self.data = json.load(json_file)[mode][device_type][self.section]
        logging.debug("starting {}".format(self.__name__))

    def getTypeList(self):
        type_list = []
        return type_list

    def getActivities(self):
        activities = self.data["activities"]
        activities_list = list(self._get_dict_keys(activities))
        return activities_list

    def parseSettings(self,  activity, region_params=None, router_params=None):
        commands = []
        activities_list = self.data["activities"][activity]
        for key, value in activities_list.items():
            if key == 'command':
                commands.extend(self._command(value))
            elif key == 'actions':
                commands.extend(self._actions(value))
        #print(commands)
        return commands

if __name__ == '__main__':

    # used for testing

    from parsers.dbtools import DbSqlite

    db_file = "../data/region9_hamwan.sqlite3"
    template_file = '../templates/ptp_config.json'
    mode = 'config'
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

    p = ParseSystem(mode, device_type, template_file)
    p.addParameters(region_params, router_params)

    commands = []
    activities = p.getActivities()
    for activity in activities:
        commands.extend(p.parseSettings( activity, region_params, router_params ))

    for command in commands:
        print(command)