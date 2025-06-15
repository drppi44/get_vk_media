from dataclasses import dataclass


@dataclass
class ConversationInfo:
    user_name: str
    photos: list[str]
    videos: list[str]