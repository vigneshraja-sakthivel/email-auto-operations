"""
Email client interface defining standard email operations.
"""

from abc import ABC, abstractmethod


class CommandProcessorInterface(ABC):
    """
    Command Processor interface defining standard command operations.
    """

    @abstractmethod
    def execute(self, params: dict = None):
        """
        Process the commands

        Args:
            params(dict, optional): Dictionary containing parameters required for executing the command
        """
        raise NotImplementedError("Subclasses must implement this method")
