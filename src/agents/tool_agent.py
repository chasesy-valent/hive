from hive import BaseAgentType
from autogen_agentchat.agents import AssistantAgent
from typing_extensions import override
from typing import List
from autogen_core.memory import Memory

# tool functions, referenced above
weather_database = {
    "new york": {"temperature": 72, "condition": "Partly Cloudy", "humidity": 65, "wind": "10 mph"},
    "london": {"temperature": 60, "condition": "Rainy", "humidity": 80, "wind": "15 mph"},
    "tokyo": {"temperature": 75, "condition": "Sunny", "humidity": 50, "wind": "5 mph"},
    "sydney": {"temperature": 80, "condition": "Clear", "humidity": 45, "wind": "12 mph"},
    "paris": {"temperature": 68, "condition": "Cloudy", "humidity": 70, "wind": "8 mph"},
}

class WeatherAgent(BaseAgentType):
    @override
    def generate_with_autogen(self, name, model_client, memory: List[Memory]):
        return AssistantAgent(
            name=name,
            system_message=self.config.get('instructions', 'You are a helpful assistant.'),
            model_client=model_client,
            memory=memory,
            tools=[get_weather_data]
        )

def get_weather_data(location: str) -> str:
    """Simulates retrieving weather data for a given location."""
    if not location:
        return ""

    # useless code to show how to access tool configurations from your config.yml file
    # weather_configs = self.tool_configs.get('weather', {})
        
    location_key = location.lower()
    if location_key in weather_database:
        data = weather_database[location_key]
        return f"Weather for {location.title()}:\n" \
                f"Temperature: {data['temperature']}°F\n" \
                f"Condition: {data['condition']}\n" \
                f"Humidity: {data['humidity']}%\n" \
                f"Wind: {data['wind']}"
    else:
        return f"No weather data available for {location}."