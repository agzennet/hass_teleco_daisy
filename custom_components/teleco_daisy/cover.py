from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .lib import (
    DaisyAwningCover,
    DaisyCover,
    DaisyRetractableSlatsCover,
    DaisyShadeCover,
    DaisySlatsCover,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    hub = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            TelecoDaisyCover(device)
            for device in hub.devices
            if isinstance(device, DaisyCover)
        ]
    )


class TelecoDaisyCover(CoverEntity):
    def __init__(self, cover: DaisyCover) -> None:
        self._cover = cover

        self._attr_unique_id = str(cover.idInstallationDevice)
        self._attr_name = cover.label

        if isinstance(cover, DaisySlatsCover):
            self._attr_device_class = CoverDeviceClass.BLIND
            self._attr_supported_features = (
                CoverEntityFeature.OPEN
                | CoverEntityFeature.CLOSE
                | CoverEntityFeature.STOP
                | CoverEntityFeature.OPEN_TILT
                | CoverEntityFeature.CLOSE_TILT
                | CoverEntityFeature.SET_TILT_POSITION
                | CoverEntityFeature.STOP_TILT
            )
        elif isinstance(cover, DaisyShadeCover):
            self._attr_device_class = CoverDeviceClass.SHADE
            self._attr_supported_features = (
                CoverEntityFeature.OPEN
                | CoverEntityFeature.CLOSE
                | CoverEntityFeature.STOP
            )
        elif isinstance(cover, DaisyAwningCover):
            self._attr_device_class = CoverDeviceClass.AWNING
            self._attr_supported_features = (
                CoverEntityFeature.OPEN
                | CoverEntityFeature.CLOSE
                | CoverEntityFeature.STOP
            )
        elif isinstance(cover, DaisyRetractableSlatsCover):
            self._attr_device_class = CoverDeviceClass.AWNING
            self._attr_supported_features = (
                CoverEntityFeature.OPEN
                | CoverEntityFeature.CLOSE
                | CoverEntityFeature.STOP
                | CoverEntityFeature.OPEN_TILT
                | CoverEntityFeature.CLOSE_TILT
                | CoverEntityFeature.SET_TILT_POSITION
                | CoverEntityFeature.STOP_TILT
            )

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            name=self._attr_name,
            manufacturer="Teleco Automation",
        )

    @property
    def is_closed(self) -> bool | None:
        return self._cover.is_closed

    async def async_update(self) -> None:
        stati = await self._cover.update_state()
        _LOGGER.debug(f"Cover update return value: {stati}")

    # @property
    # def is_closing(self) -> bool:
    #     """Return if the cover is closing or not."""
    #     return self._roller.moving < 0
    #
    # @property
    # def is_opening(self) -> bool:
    #     """Return if the cover is opening or not."""
    #     return self._roller.moving > 0
    #

    async def async_open_cover(self, **kwargs: Any) -> None:
        await self._cover.open_cover()
        await self.async_update()

    async def async_close_cover(self, **kwargs: Any) -> None:
        await self._cover.close_cover()
        await self.async_update()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        await self._cover.stop_cover()
        await self.async_update()

    async def async_open_cover_tilt(self, **kwargs: Any) -> None:
        await self._cover.open_cover()
        await self.async_update()

    async def async_close_cover_tilt(self, **kwargs: Any) -> None:
        await self._cover.close_cover()
        await self.async_update()

    async def async_stop_cover_tilt(self, **kwargs: Any) -> None:
        await self._cover.stop_cover()
        await self.async_update()

    @property
    def current_cover_position(self) -> int | None:
        return getattr(self._cover, "position", None)

    @property
    def current_cover_tilt_position(self) -> int | None:
        return getattr(self._cover, "position", None)

    async def _async_set_cover_position(self, position: int) -> None:
        if position <= 15:
            await self._cover.close_cover()
        elif 15 < position <= 48:
            await self._cover.open_cover("33")
        elif 48 < position <= 81:
            await self._cover.open_cover("66")
        else:
            await self._cover.open_cover("100")
        await self.async_update()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        await self._async_set_cover_position(kwargs[ATTR_POSITION])

    async def async_set_cover_tilt_position(self, **kwargs: Any) -> None:
        await self._async_set_cover_position(kwargs[ATTR_TILT_POSITION])
