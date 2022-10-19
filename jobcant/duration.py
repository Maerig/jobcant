class Duration:
    @classmethod
    def parse(cls, duration: str):
        hours, minutes = duration.split(":")
        total_minutes = 60 * int(hours) + int(minutes)
        return cls(total_minutes)

    def __init__(self, minutes: int = 0):
        self.minutes: int = minutes

    def __repr__(self) -> str:
        return f"{'-' if self.minutes < 0 else ''}{abs(self.minutes) // 60:02}:{abs(self.minutes) % 60:02}"

    __str__ = __repr__

    def __add__(self, other):
        return Duration(self.minutes + other.minutes)

    def __sub__(self, other):
        return Duration(self.minutes - other.minutes)

    def __mul__(self, other):
        return Duration(other * self.minutes)
