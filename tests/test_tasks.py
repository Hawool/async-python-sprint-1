import json
from pathlib import Path

from tasks import (DataAggregationTask, DataAnalyzingTask, DataCalculationTask,
                   DataFetchingTask)
from test_data.data import TEST_CITIES


path_test = Path(__file__).resolve()
json.load(str(Path(path_test, 'test_data/resp_town_data.json')))



class MockDataFetchingTask(DataFetchingTask):
    @staticmethod
    def get_town_data(town: str):
        path_test = Path(__file__).resolve()
        json.load(str(Path(path_test, 'test_data/resp_town_data.json')))

        return DataFetchingTask.validate_town_data(resp, town)


class TestDataFetchingTask:
    data_fetching = DataFetchingTask(TEST_CITIES)




weather_data = DataFetchingTask(TEST_CITIES).get_town_weather_data()
calculated_weather_data = DataCalculationTask(weather_data).calculated_weather_data()
analyzing_towns = DataAnalyzingTask(calculated_weather_data)
print(analyzing_towns.get_best_town())

town_agregator = DataAggregationTask(analyzing_towns.towns_with_rating())
town_agregator.town_data_to_json_file()