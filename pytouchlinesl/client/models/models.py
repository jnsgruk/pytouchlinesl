"""Provides models that represent the data structures returned by the Roth API.

These are mostly auto-generated using responses received from the API, with some
tweaks to types and names.
"""

from typing import Any, Dict, List, Literal, Optional

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:
    from pydantic import BaseModel, Field


class ZoneFlagsModel(BaseModel):
    relay_state: str = Field(..., alias="relayState")
    min_one_window_open: bool = Field(..., alias="minOneWindowOpen")
    algorithm: Literal["heating", "cooling"]
    floor_sensor: int = Field(..., alias="floorSensor")
    humidity_algorytm: int = Field(..., alias="humidityAlgorytm")
    zone_excluded: int = Field(..., alias="zoneExcluded")


class ZoneAttributesModel(BaseModel):
    id: int
    parent_id: int = Field(..., alias="parentId")
    time: str
    during_change: bool = Field(..., alias="duringChange")
    index: int
    current_temperature: Optional[int] = Field(..., alias="currentTemperature")
    set_temperature: int = Field(..., alias="setTemperature")
    flags: ZoneFlagsModel
    zone_state: Literal[
        "zoneOff", "noAlarm", "zoneUnregistered", "sensorDamaged", "noCommunication"
    ] = Field(..., alias="zoneState")
    signal_strength: Optional[int] = Field(..., alias="signalStrength")
    battery_level: Optional[int] = Field(..., alias="batteryLevel")
    actuators_open: int = Field(..., alias="actuatorsOpen")
    humidity: int
    visibility: bool


class ZoneDescriptionModel(BaseModel):
    id: int
    parent_id: int = Field(..., alias="parentId")
    name: str
    style_id: int = Field(..., alias="styleId")
    style_icon: str = Field(..., alias="styleIcon")
    during_change: bool = Field(..., alias="duringChange")


class ZoneModeModel(BaseModel):
    id: int
    parent_id: int = Field(..., alias="parentId")
    mode: Literal["constantTemp", "globalSchedule", "localSchedule", "timeLimit"]
    const_temp_time: int = Field(..., alias="constTempTime")
    set_temperature: int = Field(..., alias="setTemperature")
    schedule_index: int = Field(..., alias="scheduleIndex")


class ScheduleIntervalModel(BaseModel):
    start: int
    stop: int
    temp: int


class LocalScheduleModel(BaseModel):
    id: int
    parent_id: int = Field(..., alias="parentId")
    index: int
    p0_days: List[str] = Field(..., alias="p0Days")
    p0_intervals: List[ScheduleIntervalModel] = Field(..., alias="p0Intervals")
    p0_setback_temp: int = Field(..., alias="p0SetbackTemp")
    p1_days: List[str] = Field(..., alias="p1Days")
    p1_intervals: List[ScheduleIntervalModel] = Field(..., alias="p1Intervals")
    p1_setback_temp: int = Field(..., alias="p1SetbackTemp")


class ZoneModel(BaseModel):
    zone: ZoneAttributesModel
    description: ZoneDescriptionModel
    mode: ZoneModeModel
    schedule: LocalScheduleModel
    actuators: List
    underfloor: Dict[str, Any]
    windows_sensors: List = Field(..., alias="windowsSensors")
    additional_contacts: List = Field(..., alias="additionalContacts")


class GlobalScheduleModel(BaseModel):
    id: int
    parent_id: int = Field(..., alias="parentId")
    index: int
    name: str
    p0_days: List[str] = Field(..., alias="p0Days")
    p0_setback_temp: int = Field(..., alias="p0SetbackTemp")
    p0_intervals: List[ScheduleIntervalModel] = Field(..., alias="p0Intervals")
    p1_days: List[str] = Field(..., alias="p1Days")
    p1_setback_temp: int = Field(..., alias="p1SetbackTemp")
    p1_intervals: List[ScheduleIntervalModel] = Field(..., alias="p1Intervals")


class GlobalSchedulesModel(BaseModel):
    time: str
    during_change: bool = Field(..., alias="duringChange")
    elements: List[GlobalScheduleModel]


class ControllerModeModel(BaseModel):
    id: int
    parent_id: int = Field(..., alias="parentId")
    type: int
    txt_id: int = Field(..., alias="txtId")
    icon_id: int = Field(..., alias="iconId")
    value: int
    menu_id: int = Field(..., alias="menuId")


class ControllerParametersModel(BaseModel):
    controller_mode: ControllerModeModel = Field(..., alias="controllerMode")
    global_schedules_number: Dict[str, Any] = Field(..., alias="globalSchedulesNumber")


class ZonesModel(BaseModel):
    transaction_time: str
    elements: List[ZoneModel]
    global_schedules: GlobalSchedulesModel = Field(..., alias="globalSchedules")
    controller_parameters: ControllerParametersModel = Field(..., alias="controllerParameters")


class ParamsModel(BaseModel):
    description: Optional[str]
    working_status: Optional[bool] = Field(None, alias="workingStatus")
    txt_id: Optional[int] = Field(None, alias="txtId")
    icon_id: Optional[int] = Field(None, alias="iconId")
    version: Optional[str] = None
    company_id: Optional[int] = Field(None, alias="companyId")
    controller_name: Optional[str] = Field(None, alias="controllerName")
    main_controller_id: Optional[int] = Field(None, alias="mainControllerId")


class TileModel(BaseModel):
    id: int
    parent_id: int = Field(..., alias="parentId")
    type: int
    menu_id: int = Field(..., alias="menuId")
    order_id: Any = Field(..., alias="orderId")
    visibility: bool
    params: ParamsModel


class ModuleModel(BaseModel):
    zones: ZonesModel
    tiles: Optional[List[TileModel]] = []
    tiles_order: Optional[Any] = Field(None, alias="tilesOrder")
    tiles_last_update: Optional[str] = Field(None, alias="tilesLastUpdate")


class AccountModuleModel(BaseModel):
    id: int
    default: bool
    name: str
    email: str
    type: str
    controller_status: Optional[str] = Field(None, alias="controllerStatus")
    module_status: Optional[str] = Field(None, alias="moduleStatus")
    additional_information: Optional[str] = Field(None, alias="additionalInformation")
    phone_number: Optional[Any] = Field(None, alias="phoneNumber")
    zip_code: Optional[str] = Field(None, alias="zipCode")
    tag: Optional[str] = None
    country: Optional[str] = None
    gmt_id: Optional[int] = Field(None, alias="gmtId")
    gmt_time: Optional[str] = Field(None, alias="gmtTime")
    postcode_policy_accepted: bool = Field(None, alias="postcodePolicyAccepted")
    style: Optional[str] = None
    version: Optional[str] = None
    company: Optional[str] = None
    udid: str
