from dash import html, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc

from . import ids
from src.backend.data.cfgdata import pathplannercfgstate

mowsettings = dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle('Mow settings')),
                dbc.ModalBody([
                    
                    dbc.ListGroup(
                    [
                        dbc.ListGroupItem(
                            # Line Settings
                            dbc.Row([
                                dbc.Col([  
                                    html.P(['Pattern'], className='mb-0'),
                                    dbc.Select(
                                        id=ids.INPUTPATTERNSTATE, 
                                        options=[
                                            {'label': 'lines', 'value': 'lines'},
                                            {'label': 'squares', 'value': 'squares'},
                                            {'label': 'rings', 'value': 'rings'},
                                        ],
                                        value=pathplannercfgstate.pattern, style={"padding-top" : "0.17rem", "padding-bottom" : "0.17rem"}
                                    ),
                                ]),
                                dbc.Col([  
                                    html.P(['Width'], className='mb-0'),
                                    dbc.Input(id=ids.INPUTMOWOFFSETSTATE, 
                                            value=pathplannercfgstate.width, 
                                            type='number', 
                                            min=0, 
                                            max=1, 
                                            step=0.01, 
                                            size='sm'
                                    ), 
                                ]),
                                dbc.Col([  
                                    html.P(['Angle'], className='mb-0'),
                                    dbc.Input(id=ids.INPUTMOWOANGLESTATE, 
                                            value=pathplannercfgstate.angle, 
                                            type='number', 
                                            min=0, 
                                            max=359, 
                                            step=1, 
                                            size='sm'
                                    ),
                                ]),
                            ], style={"padding-bottom" : "0.75rem"}),
                        style={"padding-left" : "0.75rem", "padding-right" : "0.75erem", "padding-bottom" : "0.5rem", "padding-top" : "1.0rem"}),
                        
                        dbc.ListGroupItem(
                            # Perimeter Settings
                            dbc.Row([
                                dbc.Col([  
                                    html.P(['Distance to border'], className='mb-0'),
                                    dbc.Input(id=ids.INPUTDISTANCETOBORDERSTATE, 
                                            value=pathplannercfgstate.distancetoborder, 
                                            type='number', 
                                            min=0, 
                                            max=5, 
                                            step=1, 
                                            size='sm'
                                    ),
                                ]),
                                dbc.Col([  
                                    html.P(['Border rounds'], className='mb-0'),
                                    dbc.Input(id=ids.INPUTMOWCUTEDGEBORDERSTATE, 
                                            value=pathplannercfgstate.mowborder, 
                                            type='number', 
                                            min=0, 
                                            max=6, 
                                            step=1, 
                                            size='sm'
                                    ),
                                ]),
                            ], style={"padding-bottom" : "0.75rem"}),
                        style={"padding-left" : "0.75rem", "padding-right" : "0.75erem", "padding-bottom" : "0.5rem", "padding-top" : "1.0rem"} ),
                        
                        dbc.ListGroupItem([
                            # 
                            dbc.Row([
                                dbc.Col([ 
                                    html.P(['Mow area'], className='mb-0'),
                                ], style={"flex-grow" : "2"}),
                                dbc.Col([ 
                                    dbc.Select(
                                        id=ids.INPUTMOWAREASTATE, 
                                        options=[
                                            {'label': 'yes', 'value': 'yes'},
                                            {'label': 'no', 'value': 'no'}
                                        ],
                                        value=pathplannercfgstate.mowarea 
                                    ),
                                ], style={"flex-shrink" : "2"}),
                            ], style={"padding-bottom" : "0.75rem"}),
                            
                            dbc.Row([
                                dbc.Col([ 
                                    html.P(['Mow exclusion border'], className='mb-0'),
                                ], style={"flex-grow" : "2"}),
                                dbc.Col([ 
                                    dbc.Select(
                                        id=ids.INPUTMOWCUTEDGEEXCLUSIONSTATE, 
                                        options=[
                                            {'label': 'yes', 'value': 'yes'},
                                            {'label': 'no', 'value': 'no'}
                                        ],
                                        value=pathplannercfgstate.mowexclusion 
                                    ),
                                ], style={"flex-shrink" : "2"}),
                            ], style={"padding-bottom" : "0.75rem"}),


                            dbc.Row([
                                dbc.Col([ 
                                    html.P(['Mow border CCW'], className='mb-0'),
                                ], style={"flex-grow" : "2"}),
                                dbc.Col([ 																		
                                    dbc.Select(
                                        id=ids.INPUTMOWCUTEDGEBORDERCCWSTATE, 
                                        options=[
                                            {'label': 'yes', 'value': 'yes'},
                                            {'label': 'no', 'value': 'no'}
                                        ],
                                        value=pathplannercfgstate.mowborderccw 
                                    ),   
                                ], style={"flex-shrink" : "2"}),
                            ], style={"padding-bottom" : "0.75rem"}),
                        
                        ],
                        style={"padding-left" : "0.75rem", "padding-right" : "0.75erem", "padding-bottom" : "0.5rem", "padding-top" : "1.0rem"} ),
                    ],
                    flush=True,
                ),
                    

                ], style={"padding-top" : 0, "padding-bottom" : 0}),
                dbc.ModalFooter(
                    dbc.Button('OK', id=ids.BUTTONOKINPUTMAPSETTINGS, className='ms-auto', n_clicks=0)
                ),
        ],id=ids.MODALMOWSETTINGS, is_open=False, centered=True,
        )

@callback(Output(ids.MODALMOWSETTINGS, 'is_open'),
          [Input(ids.BUTTONMOWSETTINGS, 'n_clicks'),
           Input(ids.BUTTONOKINPUTMAPSETTINGS, 'n_clicks'),
           State(ids.MODALMOWSETTINGS, 'is_open'),
           State(ids.INPUTPATTERNSTATE, 'value'),
           State(ids.INPUTMOWOFFSETSTATE, 'value'),
           State(ids.INPUTMOWOANGLESTATE, 'value'),
           State(ids.INPUTDISTANCETOBORDERSTATE, 'value'),
           State(ids.INPUTMOWAREASTATE, 'value'),
           State(ids.INPUTMOWCUTEDGEBORDERSTATE, 'value'),
           State(ids.INPUTMOWCUTEDGEEXCLUSIONSTATE, 'value'),
           State(ids.INPUTMOWCUTEDGEBORDERCCWSTATE, 'value')])
def toggle_modal(n_clicks_bms: int, n_clicks_bok: int,
                 modal_is_open: bool, pattern: str(),
                 mowoffset: float, mowangle: int,
                 distancetoborder: int, mowarea: str,
                 mowborder: str, mowexclusion: str,
                 mowborderccw: str) -> bool:
    context = ctx.triggered_id
    if context == ids.BUTTONOKINPUTMAPSETTINGS:
        if pattern != 'lines' and pattern != 'squares' and pattern != 'rings':
            pathplannercfgstate.pattern = 'lines'
        else:
            pathplannercfgstate.pattern = pattern
        if mowoffset != None:
            pathplannercfgstate.width = mowoffset
        if mowangle != None:
            pathplannercfgstate.angle = mowangle
        if distancetoborder != None:
            pathplannercfgstate.distancetoborder = distancetoborder
        pathplannercfgstate.mowarea = mowarea
        pathplannercfgstate.mowborder = mowborder
        pathplannercfgstate.mowexclusion = mowexclusion
        pathplannercfgstate.mowborderccw = mowborderccw
            
    if n_clicks_bms or n_clicks_bok:
        return not modal_is_open
    return modal_is_open

@callback(Output(ids.INPUTMOWOFFSETSTATE, 'value'),
          Output(ids.INPUTMOWOANGLESTATE, 'value'),
          Output(ids.INPUTMOWCUTEDGEBORDERSTATE, 'value'),
          Output(ids.INPUTDISTANCETOBORDERSTATE, 'value'),
          Output(ids.INPUTPATTERNSTATE, 'value'),
          Output(ids.INPUTMOWAREASTATE, 'value'),
          Output(ids.INPUTMOWCUTEDGEEXCLUSIONSTATE, 'value'),
          Output(ids.INPUTMOWCUTEDGEBORDERCCWSTATE, 'value'),
          [Input(ids.URLUPDATE, 'pathname')])
def update_pathplandersettings_on_reload(pathname: str) -> list:
    return pathplannercfgstate.width, pathplannercfgstate.angle, pathplannercfgstate.mowborder, pathplannercfgstate.distancetoborder, pathplannercfgstate.pattern, pathplannercfgstate.mowarea, pathplannercfgstate.mowexclusion, pathplannercfgstate.mowborderccw
    
