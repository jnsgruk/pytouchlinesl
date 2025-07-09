"""An API client for the public Roth TouchlineSL API.

API Documentation: https://api-documentation.roth-touchlinesl.com/
"""

import json
import logging
from typing import Any

import aiohttp

from pytouchlinesl.client.models import GlobalScheduleModel

from .base import BaseClient
from .models import AccountModuleModel, ModuleModel

API_URL = "https://roth-touchlinesl.com/api/v1"

logger = logging.getLogger(__name__)


class RothAPIError(Exception):
    """An exception raised when an unsuccessful request is made to the Roth API."""

    def __init__(self, status: int, data: Any = None):
        """Construct an instance of the exception."""
        super().__init__()
        self._status = status
        self._data = data

    @property
    def status(self) -> int:
        """Return the HTTP status code of the failed request."""
        return self._status

    @property
    def data(self) -> Any:
        """Return any data included in the response of the failed request."""
        return self._data

    def __repr__(self) -> str:  # noqa: D105
        return f"{self.__class__.__name__}({self.__str__()})"

    def __str__(self) -> str:  # noqa: D105
        msg = f"{self.status}"

        if self.data is not None:
            msg += " " + json.dumps(self.data)

        return msg


class RothAPI(BaseClient):
    """An implementation of the BaseClient which interacts with Roth's public API."""

    def __init__(self, username, password):
        """Construct an instance of the client.

        Args:
            username: Roth TouchlineSL account email.
            password: Roth TouchlineSL account password.
        """
        self._username = username
        self._password = password
        self._user_id = None
        self._token = None

    async def _login(self):
        """Login to the Roth API, and store the received bearer token and user id."""
        data = {"username": self._username, "password": self._password}
        resp = await self._post("/authentication", json=data)

        self._user_id = resp.get("user_id")
        self._token = resp.get("token")

    async def user_id(self) -> int:
        """Return the unique user id for the authenticated account."""
        if self._token is None:
            await self._login()

        assert isinstance(self._user_id, int)
        return self._user_id

    async def authenticated(self) -> bool:
        """Report whether or not the client is authenticated with the API."""
        if self._token is None:
            return False

        resp = await self._authed_get("/authentication")
        return resp.get("authenticated", False)

    async def modules(self) -> list[AccountModuleModel]:
        """Return a list of TouchlineSL modules associated with the authenticated account."""
        if self._token is None:
            await self._login()

        resp = await self._authed_get(f"/users/{self._user_id}/modules")
        return [AccountModuleModel(**m) for m in resp]

    async def module(self, module_id: str) -> ModuleModel:
        """Return a specific module, by ID, that's associated with the authenticated account."""
        if self._token is None:
            await self._login()

        resp = await self._authed_get(f"/users/{self._user_id}/modules/{module_id}")
        return ModuleModel(**resp)

    async def set_zone_temperature(
        self, module_id: str, mode_id: int, zone_id: int, temperature: float
    ):
        """Set a constant target temperature for a specific zone, in a specific module."""
        data = {
            "mode": {
                "id": mode_id,
                "parentId": zone_id,
                "mode": "constantTemp",
                "constTempTime": 0,
                "setTemperature": int(temperature * 10),
                "scheduleIndex": 0,
            }
        }

        await self._authd_post(url=f"/users/{self._user_id}/modules/{module_id}/zones", data=data)

    async def set_zone_schedule(self, module_id: str, zone_id: int, schedule_id: int):
        """Assign a specific zone to a specific global schedule in the module's configuration."""
        module: ModuleModel = await self.module(module_id=module_id)
        schedules = module.zones.global_schedules.elements
        schedule = next((s for s in schedules if s.id == schedule_id), None)
        assert isinstance(schedule, GlobalScheduleModel)

        # Get a list of zones which are already assigned to the schedule.
        # The Roth API is relatively limited, and adding a zone to a schedule means
        # completely re-specifying the schedule, including intervals and assigned zones.
        zones_on_schedule = [
            z
            for z in module.zones.elements
            if (z.mode.mode == "globalSchedule" and z.mode.schedule_index == schedule.index)
            or z.zone.id == zone_id
        ]

        p0_intervals = [
            i.model_dump(by_alias=True) for i in schedule.p0_intervals if i.start != 6100
        ]
        p1_intervals = [
            i.model_dump(by_alias=True) for i in schedule.p1_intervals if i.start != 6100
        ]

        # TODO: This be simplified with Pydantic models
        data = {
            "scheduleName": schedule.name,
            "setInZones": [{"zoneId": z.zone.id, "modeId": z.mode.id} for z in zones_on_schedule],
            "schedule": {
                "id": schedule.id,
                "index": schedule.index,
                "p0Days": schedule.p0_days,
                "p0SetbackTemp": schedule.p0_setback_temp,
                # Empty intervals start/end with a value of 6100, which is invalid
                # if sent in this request.
                "p0Intervals": p0_intervals,
                "p1Days": schedule.p1_days,
                "p1SetbackTemp": schedule.p1_setback_temp,
                "p1Intervals": p1_intervals,
            },
        }

        await self._authd_post(
            url=f"/users/{self._user_id}/modules/{module_id}/zones/{zone_id}/global_schedule",
            data=data,
        )

    async def _authed_get(self, url: str, headers: dict[str, str] = {}) -> dict:
        """Perform an authenticated GET request to the Roth TouchlineSL API."""
        headers.update({"authorization": f"Bearer {self._token}"})
        return await self._get(url, headers)

    async def _get(self, url: str, headers: dict[str, str] = {}) -> dict:
        """Perform a GET request to the Roth TouchlineSL API."""
        logger.debug("GET %s%s", API_URL, url)

        async with aiohttp.ClientSession() as session:
            req = await session.get(f"{API_URL}{url}", headers=headers)
            resp = await req.json()

        if not req.ok:
            raise RothAPIError(status=req.status, data=resp)

        return resp

    async def _authd_post(self, url: str, headers: dict[str, str] = {}, data: dict = {}) -> dict:
        """Perform an authenticated POST request to the Roth TouchlineSL API."""
        headers.update({"authorization": f"Bearer {self._token}"})
        return await self._post(url, headers, data)

    async def _post(self, url: str, headers: dict[str, str] = {}, json: dict = {}) -> dict:
        """Perform a POST request to the Roth TouchlineSL API."""
        logger.debug("POST %s%s", API_URL, url)

        async with aiohttp.ClientSession() as session:
            req = await session.post(f"{API_URL}{url}", headers=headers, json=json)

        resp = await req.json()

        if not req.ok:
            raise RothAPIError(status=req.status, data=resp)

        return resp
