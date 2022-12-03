from pydantic_dataclass import TownMathMetods
from tasks import DataFetchingTask


class TestTownMathMetods:
    def test_methods(self, resp_data, average_temp_in_period_fixture, dry_hours_in_period_fixture):
        town_resp_model = DataFetchingTask.validate_town_data(resp_data['MOSCOW'], 'MOSCOW')
        town_math_class = TownMathMetods(town_resp_model)
        assert town_math_class.city_name == 'MOSCOW'
        assert town_math_class.now == 1653557277
        assert town_math_class.now_dt == '2022-05-26T09:27:57.820370Z'
        assert town_math_class.total_dry_hours == 2.0
        assert town_math_class.total_average_temp == 11.125
        assert town_math_class.forecasts == town_resp_model.forecasts
        assert town_math_class.fact == town_resp_model.fact
        assert town_math_class.yesterday == town_resp_model.yesterday

        assert town_math_class.average_temp_in_period == average_temp_in_period_fixture
        assert town_math_class.dry_hours_in_period == dry_hours_in_period_fixture
