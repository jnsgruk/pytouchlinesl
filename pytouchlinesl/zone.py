"""A representation of a single Roth TouchlineSL zone.

In most cases, a Zone represents a specific room in a building.
Zones can report on both temperature and humidity.

Each zone can either be set with a constant target temperature,
set to a specific global schedule, or set onto a local schedule.

Typical Usage:

    import os
    from pytouchlinesl import TouchlineSL

    tsl = TouchlineSL(username"foo@bar.com", password="deadbeef")

    # Get the module from the account
    module = await tsl.modules()
    module = modules[0]

    # Get a specific zone from the module
    zone = await module.zone_by_name("Kitchen")
    temp = zone.temperature

    # Set the zone to a constant target temp of 22.5
    await zone.set_temperature(22.5)

    # Set the zone onto a specific global schedule
    schedule = module.schedule_by_name("Living Spaces")
    await zone.set_schedule(schedule.id)
"""

from typing import TYPE_CHECKING, Literal

from .client import BaseClient
from .client.models import GlobalScheduleModel, LocalScheduleModel, ZoneModel

if TYPE_CHECKING:
    from .module import Module


class Zone:
    """A representation of a single Roth TouchlineSL zone."""

    def __init__(
        self,
        module: "Module",
        client: BaseClient,
        zone_data: ZoneModel,
        schedule: GlobalScheduleModel | LocalScheduleModel | None,
    ):
        """Construct an instance of a zone.

        Args:
            module:    The Module this Zone belongs to.
            client:    The underlying API client to use for fetching data.
            zone_data: A raw representation of the Zone returned from a client instance.
            schedule:  None if Zone is set to constant temp, otherwise instance of the global
                       schedule assigned to the zone
        """
        self._module = module
        self._client = client
        self._raw_data = zone_data
        self._schedule = schedule

    @property
    def name(self) -> str:
        """Return the configured name of the zone."""
        return self._raw_data.description.name

    @property
    def id(self) -> int:
        """Return the ID of the zone."""
        return self._raw_data.zone.id

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the zone."""
        return self._raw_data.zone.battery_level

    @property
    def temperature(self) -> float | None:
        """Return the current temperature of the zone, if it's enabled, otherwise None."""
        if self._raw_data.zone.current_temperature:
            return float(int(self._raw_data.zone.current_temperature) / 10)
        return None

    @property
    def target_temperature(self) -> float:
        """Return the target temperature of the zone."""
        return float(int(self._raw_data.zone.set_temperature) / 10)

    @property
    def humidity(self) -> float:
        """Return the humidity of the zone."""
        return float(int(self._raw_data.zone.humidity))

    @property
    def mode(self) -> Literal["constantTemp", "globalSchedule", "localSchedule", "timeLimit"]:
        """Return the mode of the zone."""
        return self._raw_data.mode.mode

    @property
    def enabled(self) -> bool:
        """Return whether or not the zone is enabled."""
        return self._raw_data.zone.zone_state != "zoneOff"

    @property
    def schedule(self) -> GlobalScheduleModel | LocalScheduleModel | None:
        """Return the zone's current schedule. If a constant temp is set, returns None."""
        if self.mode == "constantTemp":
            return None

        return self._schedule

    @property
    def relay_on(self) -> bool:
        """Return whether or not the zone's relay is on."""
        return self._raw_data.zone.flags.relay_state == "on"

    @property
    def algorithm(self) -> Literal["heating", "cooling"]:
        """Return the zone's current algorithm, either `heating` or `cooling`."""
        return self._raw_data.zone.flags.algorithm

    async def set_temperature(self, temperature: float):
        """Set a constant target temperature for the zone."""
        await self._client.set_zone_temperature(
            module_id=self._module.id,
            zone_id=self.id,
            mode_id=self._raw_data.mode.id,
            temperature=temperature,
        )
        self._module.invalidate_cache()

    async def set_schedule(self, schedule_id: int):
        """Assign the zone to a specific global schedule."""
        await self._client.set_zone_schedule(self._module.id, self.id, schedule_id)
        self._module.invalidate_cache()
