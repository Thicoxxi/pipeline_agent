from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def stream(
        self,
        prompt: str
    ):
        pass