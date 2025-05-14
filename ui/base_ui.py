from abc import ABC, abstractmethod

class BaseUI(ABC):

    @abstractmethod
    def run_agent(self, agent_name: str):
        pass

    @abstractmethod
    def send_message(self, message: str):
        pass

    @abstractmethod
    def list_scripts(self):
        pass

    @abstractmethod
    def run_script(self, script_name: str):
        pass