import logging
logger = logging.getLogger(__name__)

from dataclasses import dataclass, field
import json

from .. data.mapdata import current_map, current_task, mapping_maps, tasks
from .. data.scheduledata import schedule_tasks
from .. data.cfgdata import schedulecfg, pathplannercfgapi
from .. map import path
from .. comm import cmdlist
from .. data.roverdata import robot

from icecream import ic

@dataclass
class API:
    apistate: str = 'boot'
    robotstate: dict = field(default_factory=dict)
    tasksstate: dict = field(default_factory=dict)
    mapsstate: dict = field(default_factory=dict)
    mowparametersstate: dict = field(default_factory=dict)
    robotstate_json: str = '{}'
    tasksstate_json: str = '{}'
    mapsstate_json: str = '{}'
    mowparametersstate_json = '{}'
    loaded_tasks: list = field(default_factory=list)
    commanded_object: str = ''
    command: str = ''
    value: str = ''

    def create_api_payload(self) -> None:
        self.apistate = 'ready'

    def create_robot_payload(self) -> None:
        robotstate = dict()
        robotstate['status'] = robot.status
        robotstate['battery'] = robot.soc
        self.robotstate = robotstate
        self.robotstate_json = json.dumps(robotstate)

    def create_maps_payload(self) -> None:
        mapsstate = dict()
        mapsstate['loaded'] = current_map.name
        if not mapping_maps.saved.empty:
            mapsstate['available'] = list(mapping_maps.saved['name'].unique())
        else:
            mapsstate['available'] = []
        self.mapsstate = mapsstate
        self.mapsstate_json = json.dumps(mapsstate)
    
    def create_tasks_payload(self) -> None:
        tasksstate = dict()
        if not current_task.subtasks.empty:
            tasksstate['selected'] = list(current_task.subtasks['name'].unique())
            tasksstate['loaded'] = self.loaded_tasks
        else:
            tasksstate['selected'] = []
            tasksstate['loaded'] = self.loaded_tasks
        if not tasks.saved.empty:
            tasksstate['available'] = list(tasks.saved[tasks.saved['map name'] == current_map.name]['name'].unique())
        else:
            tasksstate['available'] = []
        self.tasksstate = tasksstate
        self.tasksstate_json = json.dumps(tasksstate)
    
    def create_mow_parameters_payload(self) -> None:
        mowparametersstate = dict()
        mowparametersstate['pattern'] = pathplannercfgapi.pattern
        mowparametersstate['width'] = pathplannercfgapi.width
        mowparametersstate['angle'] = pathplannercfgapi.angle
        mowparametersstate['distancetoborder'] = pathplannercfgapi.distancetoborder
        mowparametersstate['mowarea'] = pathplannercfgapi.mowarea
        mowparametersstate['mowborder'] = pathplannercfgapi.mowborder
        mowparametersstate['mowexclusion'] = pathplannercfgapi.mowexclusion
        mowparametersstate['mowborderccw'] = pathplannercfgapi.mowborderccw
        self.mowparametersstate = mowparametersstate
        self.mowparametersstate_json = json.dumps(mowparametersstate)

    def update_payload(self) -> None:
        self.create_api_payload()
        self.create_robot_payload()
        self.create_maps_payload()
        self.create_tasks_payload()
        self.create_mow_parameters_payload()

    def check_cmd(self, buffer: dict) -> None:
        if 'tasks' in buffer:
            self.commanded_object = 'tasks'
            buffer = buffer['tasks']
            self.check_tasks_cmd(buffer)
        elif 'maps' in buffer:
            self.commanded_object = 'maps'
            buffer = buffer['maps']
            self.check_maps_cmd(buffer)
        elif 'robot' in buffer:
            self.commanded_object = 'robot'
            buffer = buffer['robot']
            self.check_robot_cmd(buffer)
        elif 'mow parameters' in buffer:
            self.commanded_object = 'mow parameters'
            buffer = buffer['mow parameters']
            self.check_mow_parameters_cmd(buffer)
        else:
            logger.info('No valid object in api message found. Aborting')
            return

    def check_tasks_cmd(self, buffer: dict) -> None:
        allowed_cmds = ['select', 'load']
        if 'command' in buffer:
            command = [buffer['command']]
            command = list(set(command).intersection(allowed_cmds))
            if command == []:
                logger.info(f'No valid command in api message found. Allowed commands: {allowed_cmds}. Aborting')
            else:
                self.command = command[0]
                self.perform_tasks_cmd(buffer)
        else:
           logger.info('No command in api message found. Aborting')
        return 
    
    def check_maps_cmd(self, buffer: dict) -> None:
        allowed_cmds = ['select', 'load']
        if 'command' in buffer:
            command = [buffer['command']]
            command = list(set(command).intersection(allowed_cmds))
            if command == []:
                logger.info(f'No valid command in api message found. Allowed commands: {allowed_cmds}. Aborting')
            else:
                self.command = command[0]
                self.perform_maps_cmd(buffer)
        else:
           logger.info('No command in api message found. Aborting')
        return 

    def check_robot_cmd(self, buffer: dict) ->  None:
        allowed_cmds = ['mow', 'stop', 'dock']
        if 'command' in buffer:
            command = [buffer['command']]
            command = list(set(command).intersection(allowed_cmds))
            if command == []:
                logger.info(f'No valid command in api message found. Allowed commands: {allowed_cmds}. Aborting')
            else:
                self.command = command[0]
                self.perform_robot_cmd(buffer)
        else:
           logger.info('No command in api message found. Aborting')
        return 
    
    def check_mow_parameters_cmd(self, buffer: dict) -> None:
        if 'pattern' in buffer:
            allowed_values = ['lines', 'squares', 'rings']
            pattern = buffer['pattern']
            value = list(set([pattern]).intersection(allowed_values))
            if value != []:
                pathplannercfgapi.pattern = value[0]
                logger.info(f'Mow parameter pattern changed to: {value[0]}')
            else:
                logger.info(f'No valid value for pattern found. Allowed values: {allowed_values}')
        if 'width' in buffer:
            try:
                value = float(buffer['width'])
                if 0.01 < value <= 1:
                    pathplannercfgapi.width = value
                    logger.info(f'Mow parameter width changed to: {value}')
                else:
                    logger.info(f'Wrong range of width value')
            except Exception as e:
                logger.info(f'Width value is invalid')
                logger.debug(str(e))
        if 'angle' in buffer:
            try:
                value = int(buffer['angle'])
                if 0 < value <= 359:
                    pathplannercfgapi.angle = value
                    logger.info(f'Mow parameter angle changed to: {value}')
                else:
                    logger.info(f'Wrong range of angle value')
            except Exception as e:
                logger.info(f'Angle value is invalid')
                logger.debug(str(e))
        if 'distancetoborder' in buffer:
            try:
                value = int(buffer['distancetoborder'])
                if 0 < value <= 5:
                    pathplannercfgapi.distancetoborder = value
                    logger.info(f'Mow parameter distance to border changed to: {value}')
                else:
                    logger.info(f'Wrong range of distance to border value')
            except Exception as e:
                logger.info(f'Distance to border value is invalid')
                logger.debug(str(e))
        if 'mowarea' in buffer:
            try:
                value = bool(buffer['mowarea'])
                pathplannercfgapi.mowarea = value
                logger.info(f'Mow parameter mow area changed to: {value}')
            except Exception as e:
                logger.info(f'Mow area value is invalid')
                logger.debug(str(e))
        if 'mowborder' in buffer:
            try:
                value = int(buffer['mowborder'])
                if 0 < value <= 5:
                    pathplannercfgapi.mowborder = value
                    logger.info(f'Mow parameter mow border changed to: {value}')
                else:
                    logger.info(f'Wrong range of mow border value')
            except Exception as e:
                logger.info(f'Mow border value is invalid')
                logger.debug(str(e))
        if 'mowexclusion' in buffer:
            try:
                value = bool(buffer['mowexclusion'])
                pathplannercfgapi.mowexclusion = value
                logger.info(f'Mow parameter mow exclusion changed to: {value}')
            except Exception as e:
                logger.info(f'Mow exclusion value is invalid')
                logger.debug(str(e))
        if 'mowborderccw' in buffer:
            try:
                value = bool(buffer['mowborderccw'])
                pathplannercfgapi.mowborderccw = value
                logger.info(f'Mow parameter mow border in ccw changed to: {value}')
            except Exception as e:
                logger.info(f'Mow border in ccw value is invalid')
                logger.debug(str(e))

    def perform_tasks_cmd(self, buffer: dict) -> None:
        if 'value' in buffer:
            value = []
            value.append(buffer['value'])
            self.value = list(set(value).intersection(list(tasks.saved[tasks.saved['map name'] == current_map.name]['name'].unique())))
            if self.value == []:
                allowed_values = list(tasks.saved[tasks.saved['map name'] == current_map.name]['name'].unique())
                logger.info(f'No valid value in api message found. Allowed values: {allowed_values}. Aborting')
            else:
                if self.command == 'select':
                    current_task.load_task_order(self.value)
                elif self.command == 'load':
                    self.loaded_tasks = self.value
                    current_task.load_task_order(self.value)
                    current_map.task_progress = 0
                    current_map.calculating = True
                    path.calc_task(current_task.subtasks, current_task.subtasks_parameters)
                    current_map.calculating = False
                    current_map.mowpath = current_map.preview
                    current_map.mowpath['type'] = 'way'
                    cmdlist.cmd_take_map = True

    def perform_maps_cmd(self, buffer: dict) -> None:
        if 'value' in buffer:
            value = buffer['value']
            self.value = list(set([value]).intersection(list(mapping_maps.saved['name'].unique())))
            if self.value == []:
                allowed_values = list(mapping_maps.saved['name'].unique())
                logger.info(f'No valid value in api message found. Allowed values: {allowed_values}. Aborting')
            else:
                if self.command == 'load':
                    selected = mapping_maps.saved[mapping_maps.saved['name'] == self.value[0]] 
                    current_map.perimeter = selected
                    current_map.create(self.value[0])
                    current_task.create()
                    schedule_tasks.create()
                    schedulecfg.reset_schedulecfg()
                    cmdlist.cmd_take_map = True

    def perform_robot_cmd(self, buffer) -> None:
        allowed_values = ['mow', 'stop', 'dock']
        if 'value' in buffer:
            self.value = buffer['value']
            if self.command == 'mow':
                self.perform_mow_cmd()
            elif self.command == 'stop':
                cmdlist.cmd_stop = True
            elif self.command == 'dock':
                cmdlist.cmd_dock = True
            else:
                logger.info(f'No valid command in api message found. Allowed values: {allowed_values}. Aborting')

    def perform_mow_cmd(self) -> None:
        allowed_values = ['resume', 'task', 'all', 'selection']
        if self.value == 'resume':
            cmdlist.cmd_resume = True
        elif self.value == 'task':
            if self.tasksstate['selected'] != []:
                current_map.task_progress = 0
                current_map.calculating = True
                path.calc_task(current_task.subtasks, current_task.subtasks_parameters)
                current_map.calculating = False
                current_map.mowpath = current_map.preview
                current_map.mowpath['type'] = 'way'
                cmdlist.cmd_mow = True
            else:
                logger.info(f'No selected tasks found')
        elif self.value == 'all':
            current_map.selected_perimeter = current_map.perimeter_polygon
            current_map.calculating = True
            current_map.task_progress = 0
            current_map.total_tasks = 1
            route = path.calc(current_map.selected_perimeter, pathplannercfgapi, [robot.position_x, robot.position_y])
            current_map.areatomow = round(current_map.selected_perimeter.area)
            current_map.calc_route_preview(route) 
            current_map.calculating = False
            current_map.mowpath = current_map.preview
            current_map.mowpath['type'] = 'way'
            cmdlist.cmd_mow = True
        elif self.value == 'selection':
            pass
        else:
            logger.info(f'No valid value in api message found. Allowed values: {allowed_values}. Aborting')
    
cassandra_api = API()