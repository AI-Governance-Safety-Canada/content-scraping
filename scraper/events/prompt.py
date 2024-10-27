EVENT_METHOD = "scrape_event_information"

EVENT_PROMPT_OVERVIEW = """
Please parse the requested information for all events listed below.
""".strip().replace(
    "\n", " "
)

EVENT_DETAILS = {
    "events": [
        {
            "event_name": "<The name of the event>",
            "start_date": "<The date the event starts, excluding the time, in ISO-8601 format. If the date is not provided, this field is the empty string.>",
            "start_time": "<The time the event starts, if available. Must be ISO-8601 format and include UTC offset. If the time is not provided, this field is the empty string.>",
            "end_date": "<The date the event ends, excluding the time, in ISO-8601 format. If the date is not provided, this field is the empty string.>",
            "end_time": "<The time the event ends, if available. Must be in ISO-8601 format and include the UTC offset. If the time is not provided, this field is the empty string.>",
            "event_description": "<A short description of the event in one to three sentences if one is present. Otherwise, the empty string.>",
            "event_url": "<The full URL for the event. If no URL is provided, this field is the empty string.>",
            "event_attendence": "<How participants will join the event: either 'in-person', 'virtual' or 'hybrid'>",
            "event_country": "<The country the event is located in, if provided. For for in-person or hybrid events without a listed location, this field is the empty string. For virtual events, this is set to 'online'.>",
            "event_region": "<The region (state, province, etc.) the event is located in, if provided. For for in-person or hybrid events without a listed location, this field is the empty string. For virtual events, this is set to 'online'.>",
            "event_city": "<The city the event is located in, if provided. For for in-person or hybrid events without a listed location, this field is the empty string. For virtual events, this is set to 'online'.>",
        },
    ],
}
