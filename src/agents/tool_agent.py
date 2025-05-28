from hive import BaseAgentType
from autogen_agentchat.agents import AssistantAgent
from typing_extensions import override

class WeatherAgent(BaseAgentType):
    @override
    def generate_with_autogen(self, name, model_client):
        return AssistantAgent(
            name=name,
            system_message=self.config.get('instructions', 'You are a helpful assistant.'),
            model_client=model_client,
            tools=[get_weather_data]
        )

# tool functions, referenced above
weather_database = {
    "new york": {"temperature": 72, "condition": "Partly Cloudy", "humidity": 65, "wind": "10 mph"},
    "london": {"temperature": 60, "condition": "Rainy", "humidity": 80, "wind": "15 mph"},
    "tokyo": {"temperature": 75, "condition": "Sunny", "humidity": 50, "wind": "5 mph"},
    "sydney": {"temperature": 80, "condition": "Clear", "humidity": 45, "wind": "12 mph"},
    "paris": {"temperature": 68, "condition": "Cloudy", "humidity": 70, "wind": "8 mph"},
}

async def get_weather_data(location: str) -> str:
    """Simulates retrieving weather data for a given location."""
    if not location:
        return ""
        
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