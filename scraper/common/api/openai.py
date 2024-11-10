import logging
from typing import Type

import openai

from scraper.common.text_processors.html import clean_content

from .interface import Api, ApiResponse, RichResponse
from .http import get, HTTP_GET_HEADERS


class OpenAIApi(Api[RichResponse]):
    """Class for scraping webpages using OpenAI"""

    def __init__(
        self,
        model: str,
        prompt: str,
        response_format: Type[RichResponse],
    ) -> None:
        self.model = model
        self.prompt = prompt
        self.response_format = response_format
        self.client = openai.OpenAI()

    def scrape(self, url: str) -> ApiResponse[RichResponse]:
        logger = logging.getLogger(__name__)
        # We need to make two requests: first we fetch the page we want to scrape. Then
        # we submit its contents to the API for parsing.
        response = get(url, headers=HTTP_GET_HEADERS)
        if not response:
            return None
        # Remove irrelevant portions to reduce token count
        cleaned = clean_content(response.text)
        if not cleaned:
            logger.warning("No content found for %s", url)
            return None

        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.prompt,
                    },
                    {
                        "role": "user",
                        "content": cleaned,
                    },
                ],
                response_format=self.response_format,
            )
        except openai.OpenAIError as error:
            logger.error("Failed to scrape %s: %r", url, error)
            return None

        logger.debug("Usage information: %s", completion.usage)

        if len(completion.choices) == 0:
            logger.warning("Model returned no completions for %s", url)
            return None
        if len(completion.choices) > 1:
            logger.warning("Model returned multiple completions for %s", url)
            for choice in completion.choices:
                logger.debug(choice)

        reply = completion.choices[0].message
        if reply is None:
            return None
        if reply.refusal:
            logger.warning("Model refused to scrape %s: %r", url, reply.refusal)
            return None
        return reply.parsed
