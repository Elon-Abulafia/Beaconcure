from abc import ABC, abstractmethod


class ValidatorStrategy(ABC):
    @abstractmethod
    def validate(self, document):
        pass


class DocumentValidator:
    def __init__(self, validation_strategy: ValidatorStrategy):
        self.validation_strategy: ValidatorStrategy = validation_strategy

    def validate(self, document):
        return self.validation_strategy.validate(document)

    @property
    def strategy(self):
        return self.validation_strategy

    @strategy.setter
    def strategy(self, strategy):
        self.validation_strategy = strategy
