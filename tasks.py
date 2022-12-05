import csv
import json
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Optional

from pydantic import ValidationError

from api_client import YandexWeatherAPI
from log_settings import logger
from pydantic_dataclass import RespModel, TownMathMethods
from utils import TOWN_DATA_FILENAME_CSV, TOWN_DATA_FILENAME_JSON


@dataclass
class DataFetchingTask:
    """Class for getting weather data for cities"""
    yandex_api = YandexWeatherAPI()
    cities: dict[str, str]

    def get_town_weather_data(self) -> list[Optional[RespModel]]:
        logger.info('Launch of weather assembly in towns')
        with ThreadPoolExecutor() as pool:
            weather_data = pool.map(self.get_town_data, self.cities)
        logger.info('Towns weather was collected')
        return [town for town in weather_data]

    def get_town_data(self, town: str) -> Optional[RespModel]:
        resp = self.yandex_api.get_forecasting(town)
        logger.info(f'{town} weather was get received')
        return DataFetchingTask.validate_town_data(resp, town)

    @staticmethod
    def validate_town_data(resp: dict[str, Any], town: str) -> Optional[RespModel]:
        try:
            resp_model = RespModel(city_name=town, **resp)
            return resp_model
        except ValidationError as e:
            logger.error(f'Error: {e.json()}')
            return None


@dataclass
class DataCalculationTask:
    weather_data: list[RespModel]

    def calculated_weather_data(self) -> list[TownMathMethods]:
        with ProcessPoolExecutor() as pool:
            weather_data = pool.map(TownMathMethods, self.weather_data, chunksize=10)
        return [town for town in weather_data]


class DataAnalyzingTask:
    def __init__(self, weather_data: list[TownMathMethods]):
        self.weather_data = self.sort_towns(weather_data)

    def get_best_town(self) -> str:
        return self.weather_data[0].city_name if self.weather_data else "No data"

    def towns_with_rating(self) -> list[TownMathMethods]:
        return [self.town_get_rating(town, number + 1) for number, town in enumerate(self.weather_data)]

    @staticmethod
    def sort_towns(weather_data: list[TownMathMethods]) -> list[TownMathMethods]:
        return sorted(weather_data, key=lambda x: (x.total_average_temp, x.total_dry_hours), reverse=True)

    @staticmethod
    def town_get_rating(town: TownMathMethods, number: int) -> TownMathMethods:
        town.rating = number
        return town


@dataclass
class DataAggregationTask:
    weather_data: list[TownMathMethods]

    def town_data_to_json_file(self) -> None:
        with open(TOWN_DATA_FILENAME_JSON, 'w') as fp:
            json.dump([town.to_dict() for town in self.weather_data], fp, indent=4)
        logger.info(f'File {TOWN_DATA_FILENAME_JSON} was created')

    def _write_headers_in_csv(self):
        with open(TOWN_DATA_FILENAME_CSV, 'w', newline='') as f:
            writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL)
            f.writelines('sep=,' + '\n')
            writer.writerow(['Город/день', '', *self.weather_data[0].get_day_headers(), 'Среднее', 'Рейтинг'])

    def town_data_to_csv_file(self) -> None:
        """
        Сделал два варианта решения, синхронный (закомментированный) и через потоки
        (как предлагалось в ревью ну и для себя поэкспериментировать :))

        В ходе всяких тестов (запись 100000 строк в csv) понял что синхронный метод в данном случае, при записи
        в один файл  во много раз быстрее многопоточного. (Пробовал также с бликировками и без)
        При многопоточном скорость значительно падает, т.к приходится создавать потоки, потом в каждом из них открывать
        файл, и только потом производить именно дозапись, чтобы предыдущие данные не стерлись, а потом закрывать потоки.
        В итоге, если бы я применял это на практике, то выбрал бы синхронный вариант.
        Или я что-то недопонимаю ‾\_(ツ)_/‾
        """
        # self._write_headers_in_csv()
        # with open(TOWN_DATA_FILENAME_CSV, 'a', newline='') as f:
        #     writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL)
        #     for town in self.weather_data:
        #         writer.writerow(town.get_first_row_town_data_for_csv())
        #         writer.writerow(town.get_second_row_town_data_for_csv())

        self._write_headers_in_csv()
        with ThreadPoolExecutor() as pool:
            pool.map(TownMathMethods.write_data_in_csv_file, self.weather_data)
