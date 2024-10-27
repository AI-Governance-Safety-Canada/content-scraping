EVENT_METHOD = "scrape_event_information"

EVENT_PROMPT_OVERVIEW = """
Please parse the requested information for all events listed below.
If a detail is not explicitly mentioned, set it to the JSON value null
(not the string "null"). Do not fabricate any details.
Only include dates, times and locations if they are clearly provided in the text.
""".strip().replace(
    "\n", " "
)
