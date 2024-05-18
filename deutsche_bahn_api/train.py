from __future__ import annotations

from deutsche_bahn_api.train_changes import TrainChanges
from datetime import datetime
#from train_changes import TrainChanges
#from otsi_parameters import *
import numpy as np
import json
import copy

class Train:
    request_time: str
    request_timeDate: datetime | None
    stop_id: str
    trip_type: str
    train_type: str
    train_number: str
    train_line: str | None
    platform: str
    passed_stations: str | None
    stations: str
    arrival: str
    departure: str | None
    departureReal: str | None
    train_changes: TrainChanges | None
    ex: str | None
    nextStops: [] | None
    nextStop: str | None
    departureDate: datetime
    departureRealDate: datetime
    delayDate: timedelta
    delay_minutes: int
    reaches_terminal_station: bool 
    last_message: str | None
    last_message_time: str | None
    last_message_timeDate: datetime | None
        
    def postprocess(self):
               
        date_format = "%y%m%d%H%M"

        # Get request data as datetime
        self.request_timeDate = datetime.strptime(self.request_time, date_format)
        
        # Get planed and real departure
        try:
            self.departureReal = self.train_changes.departure
        except:
            self.departureReal = self.departure
        self.departureDate = datetime.strptime(self.departure, date_format)
        self.departureRealDate = datetime.strptime(self.departureReal, date_format)
        self.delayDate = self.departureRealDate - self.departureDate
        self.delay_minutes = int(self.delayDate.total_seconds() / 60) % 60

        # Get real next stops 
        self.nextStops = self.stations.split("|") # Get regular stops
        planned_last_stop = self.nextStops[-1]
        if hasattr(self.train_changes, 'stations'):
            self.nextStops = self.train_changes.stations.split("|") # Get changed stops
        if self.nextStops[-1] != planned_last_stop:
            self.reaches_terminal_station = False
        else:
            self.reaches_terminal_station = True

        # Get next stop
        self.nextStop = self.nextStops[0]

        # Get last message
        try:
            last_message_index = np.argmax([x.time for x in self.train_changes.messages] )
            self.last_message =      self.train_changes.messages[last_message_index].message
            self.last_message_time = self.train_changes.messages[last_message_index].time
            self.last_message_timeDate = datetime.strptime(self.last_message_time, date_format)  
        except:
            self.last_message = None
            self.last_message_time = None
            self.last_message_timeDate = None

    def to_dict(self):
        dct = copy.deepcopy(vars(self))
        train_changes = copy.deepcopy(vars(self.train_changes))
        messages = copy.deepcopy([vars(x) for x in self.train_changes.messages])
        dct["train_changes"] = train_changes
        dct["train_changes"]["messages"] = messages
        return dct

    def to_cleaned_dict(self, indent=4):
        """Returns dict but without datetime formats"""
        dct = self.to_dict()
        del dct["departureDate"]
        del dct["departureRealDate"]
        del dct["delayDate"]
        del dct["request_timeDate"]

        try:
            del dct["last_message_timeDate"]
        except:
            pass
        #dct = json.dumps(dct, indent=None, ensure_ascii=False)
        return dct
