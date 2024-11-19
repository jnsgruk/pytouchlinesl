import pytest

test_attrs = [
    ("temperature", 22.1),
    ("target_temperature", 18.0),
    ("humidity", 61.0),
    ("mode", "globalSchedule"),
    ("enabled", True),
    ("relay_on", True),
    ("algorithm", "heating"),
    ("signal_strength", 53),
    ("alarm", None),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("attr,val", test_attrs)
async def test_zone_attributes(attr, val, test_zone):
    assert getattr(test_zone, attr) == val
