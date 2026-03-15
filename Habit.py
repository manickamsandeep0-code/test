from tracker_event import TrackerEvent

class Habit(TrackerEvent):
    def __init__(self, id: int, name: str):
        super().__init__(id, name)

    def get_details(self) -> str:
        return f"Habit: {self.get_name()}"

    def __str__(self) -> str:
        return self.get_name()