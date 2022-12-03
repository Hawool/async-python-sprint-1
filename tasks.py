import json
import logging
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Optional

from pydantic import ValidationError

from api_client import YandexWeatherAPI
from pydantic_dataclass import RespModel, TownMathMetods

logger = logging.getLogger()


class DataFetchingTask:
    """Class for getting weather data for cities"""
    def __init__(self, cities: dict[str, str]):
        self.cities = cities

    def get_town_weather_data(self) -> list[RespModel]:
        with ThreadPoolExecutor(max_workers=1) as pool:
            weather_data = pool.map(DataFetchingTask.get_town_data, self.cities, chunksize=10)
        return [town for town in weather_data]

    @staticmethod
    def get_town_data(town: str) -> Optional[RespModel]:
        ywAPI = YandexWeatherAPI()
        resp = ywAPI.get_forecasting(town)
        return DataFetchingTask.validate_town_data(resp, town)

    @staticmethod
    def validate_town_data(resp: dict[str, Any], town: str) -> Optional[RespModel]:
        try:
            resp_model = RespModel(city_name=town, **resp)
            return resp_model
        except ValidationError as e:
            logger.error(f'Error: {e.json()}')


class DataCalculationTask:
    def __init__(self, weather_data: list[RespModel]):
        self.weather_data = weather_data

    def calculated_weather_data(self) -> list[TownMathMetods]:
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
            weather_data = pool.map(TownMathMetods, self.weather_data, chunksize=10)
        return [town for town in weather_data]


class DataAnalyzingTask:
    def __init__(self, weather_data: list[TownMathMetods]):
        self.weather_data = self.sort_towns(weather_data)

    def get_best_town(self) -> str:
        return self.weather_data[0].city_name if self.weather_data else "No data"

    def towns_with_rating(self) -> list[TownMathMetods]:
        return [self.town_get_rating(town, number + 1) for number, town in enumerate(self.weather_data)]

    @staticmethod
    def sort_towns(weather_data: list[TownMathMetods]) -> list[TownMathMetods]:
        return sorted(weather_data, key=lambda x: (x.total_average_temp, x.total_dry_hours), reverse=True)

    @staticmethod
    def town_get_rating(town: TownMathMetods, number: int) -> TownMathMetods:
        town.rating = number
        return town


class DataAggregationTask:
    def __init__(self, weather_data: list[TownMathMetods]):
        self.weather_data = weather_data

    def town_data_to_json_file(self) -> None:
        with open('result.json', 'w') as fp:
            json.dump([town.to_dict() for town in self.weather_data], fp, indent=4)
