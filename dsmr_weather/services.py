import xml.etree.ElementTree as ET
import urllib.request

from django.utils import timezone

from dsmr_weather.models.settings import WeatherSettings
from dsmr_weather.models.statistics import TemperatureReading
from dsmr_weather.buienradar import BUIENRADAR_API_URL, BUIENRADAR_XPATH


def read_weather():
    """ Reads the current weather state, if enabled, and stores it. """
    # Only when explicitly enabled in settings.
    weather_settings = WeatherSettings.get_solo()

    if not weather_settings.track:
        return

    # Fetch XML from API.
    request = urllib.request.urlopen(BUIENRADAR_API_URL)
    response_bytes = request.read()
    request.close()
    response_string = response_bytes.decode("utf8")

    # Use simplified xPath engine to extract current temperature.
    root = ET.fromstring(response_string)
    xpath = BUIENRADAR_XPATH.format(
        weather_station_id=weather_settings.buienradar_station
    )
    temperature_element = root.find(xpath)
    temperature = temperature_element.text

    # Gas readings trigger these readings, so the 'read at' timestamp should be somewhat in sync.
    # Therefor we align temperature readings with them, having them grouped by hour that is..
    read_at = timezone.now().replace(minute=0, second=0, microsecond=0)

    TemperatureReading.objects.create(
        read_at=read_at,
        degrees_celcius=temperature
    )
