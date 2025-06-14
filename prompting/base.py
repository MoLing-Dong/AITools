from dataclasses import dataclass


@dataclass
class ChatPrompt:
    system: str

    def format(self, **kwargs):
        return [{
            "role": "system",
            "content": self.system.format(**kwargs),
        }]
