from abc import ABC, abstractmethod


class BaseScraper(ABC):
    def __init__(self, query):
        self.query = query
        self.results = []

    @abstractmethod
    async def scrape(self, browser):
        pass
