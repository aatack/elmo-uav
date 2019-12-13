from datetime import datetime
from typing import List


possible_date_formats = ["%d-%b-%y %H:%M:%S", "%d %b %Y %H:%M:%S"]


class ReadingSet:
    def __init__(self, readings: List["Reading"]):
        """Store a sit of wind tunnel readings."""
        self.readings = readings

    @staticmethod
    def from_string(string: str, has_tail: bool = True) -> "ReadingSet":
        """Read the output file of a wind tunnel run."""
        return ReadingSet(
            [
                Reading.from_string(line)
                for line in string.split("\n")[1:]
                if len(line) > 0
            ]
        )

    @staticmethod
    def merge(*sets: List["ReadingSet"]) -> "ReadingSet":
        """Merge two or more sets of readings."""
        readings = []
        for reading_set in sets:
            readings += reading_set.readings
        return ReadingSet(readings)

    @staticmethod
    def from_file(path: str, has_tail: bool = None) -> "ReadingSet":
        """
        Read a reading set directly from a file.
        
        If it is not specified whether or not the tail was present, that is determined
        from whether or not the text "notail" appears in the path.
        """
        with open(path, "r") as f:
            return ReadingSet.from_string(
                f.read(), has_tail if has_tail is not None else not ("notail" in path)
            )


class Reading:
    def __init__(
        self,
        timestamp: datetime,
        lift: float,
        drag: float,
        side: float,
        pitch_moment: float,
        roll_moment: float,
        yaw_moment: float,
        pitch: float,
        yaw: float,
        windspeed: float,
        aerofoil: str,
        wing_angle: float,
        flap_angle: float,
        has_tail: bool,
    ):
        """Stores the data pertaining to one reading in the wind tunnel."""
        self.timestamp = timestamp
        self.lift, self.drag, self.side = lift, drag, side
        self.pitch_moment = pitch_moment
        self.yaw_moment = yaw_moment
        self.roll_moment = roll_moment
        self.pitch, self.yaw = pitch, yaw
        self.windspeed = windspeed
        self.aerofoil = aerofoil
        self.wing_angle = wing_angle
        self.flap_angle = flap_angle
        self.has_tail = has_tail

    @staticmethod
    def from_string(string: str, has_tail: bool = True) -> "Reading":
        """Read a reading from its string representation."""
        segments = string.split(",")
        comments = segments[2].split("_")
        return Reading(
            read_date(segments[0] + " " + segments[1]),
            float(segments[3]),
            float(segments[4]),
            float(segments[5]),
            float(segments[6]),
            float(segments[7]),
            float(segments[8]),
            float(segments[9]),
            float(segments[10]),
            float(segments[12]),
            comments[1],
            float(comments[2]),
            float(comments[3]),
            has_tail,
        )


def read_date(date_string: str) -> datetime:
    """Read a date from one of a number of formats."""
    for format_string in possible_date_formats:
        try:
            return datetime.strptime(date_string, format_string)
        except:
            pass
    raise Exception("could not parse datetime '{}'".format(date_string))
