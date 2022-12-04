from log_settings import logger
from tasks import (DataAggregationTask, DataAnalyzingTask, DataCalculationTask,
                   DataFetchingTask)
from utils import CITIES


def forecast_weather():
    """
    Анализ погодных условий по городам
    """
    logger.info('Project run')
    weather_data = DataFetchingTask(CITIES).get_town_weather_data()
    calculated_weather_data = DataCalculationTask(weather_data).calculated_weather_data()
    analyzing_towns = DataAnalyzingTask(calculated_weather_data)
    print(analyzing_towns.get_best_town())

    town_agregator = DataAggregationTask(analyzing_towns.towns_with_rating())
    town_agregator.town_data_to_csv_file()
    logger.info('Project stop')


if __name__ == "__main__":
    forecast_weather()
