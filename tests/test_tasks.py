import json
from pathlib import Path

from tasks import DataAnalyzingTask, DataCalculationTask, DataFetchingTask
from tests.test_data.data import TEST_CITIES


class MockDataFetchingTask(DataFetchingTask):
    @staticmethod
    def get_town_data(town: str):
        path_test = Path(__file__).resolve().parent
        with open(str(Path(path_test, 'test_data/test_resp_town_data.json'))) as json_file:
            data = json.load(json_file)
        return DataFetchingTask.validate_town_data(data.get(town), town)


weather_data = MockDataFetchingTask(TEST_CITIES)


class TestDataFetchingTask:

    def test_get_town_weather_data(self):
        town_weather_data = weather_data.get_town_weather_data()
        assert town_weather_data[0].city_name == 'MOSCOW'
        assert town_weather_data[1].city_name == 'PARIS'
        assert town_weather_data[2].city_name == 'LONDON'


calculated_weather_data = DataCalculationTask(weather_data.get_town_weather_data())
analyzing_towns = DataAnalyzingTask(calculated_weather_data.calculated_weather_data())


class TestDataAnalyzingTask:
    def test_get_best_town(self):
        assert analyzing_towns.get_best_town() == 'PARIS'
