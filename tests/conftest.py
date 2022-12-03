import json
from pathlib import Path

import pytest

from pydantic_dataclass import TownAverageTemp, DayAverageTemp, TownDryHours, DayDryHours


@pytest.fixture(scope='function')
def resp_data():
    path_test = Path(__file__).resolve().parent
    with open(str(Path(path_test, 'test_data/resp_town_data.json'))) as json_file:
        data = json.load(json_file)
    return data


@pytest.fixture(scope='function')
def average_temp_in_period_fixture():
    return TownAverageTemp(
        days=[
            DayAverageTemp(date='2022-05-26', average_temp=18.0),
            DayAverageTemp(date='2022-05-27', average_temp=13.1),
            DayAverageTemp(date='2022-05-28', average_temp=12.2),
            DayAverageTemp(date='2022-05-29', average_temp=1.2)
        ]
    )


@pytest.fixture(scope='function')
def dry_hours_in_period_fixture():
    return TownDryHours(
        days=[
            DayDryHours(date='2022-05-26', dry_hours=7),
            DayDryHours(date='2022-05-27', dry_hours=0),
            DayDryHours(date='2022-05-28', dry_hours=0),
            DayDryHours(date='2022-05-29', dry_hours=1)
        ]
    )
