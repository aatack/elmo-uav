from typing import Callable, List, Tuple
from collections import defaultdict
from datetime import datetime
from os import listdir


possible_date_formats = ["%d-%b-%y %H:%M:%S", "%d %b %Y %H:%M:%S"]


class ReadingSet:
    def __init__(self, readings: List["Reading"]):
        """Store a sit of wind tunnel readings."""
        self.readings = readings

    def __len__(self) -> int:
        """Return the number of readings in the set."""
        return len(self.readings)

    def where(self, predicate: Callable[["Reading"], bool]) -> "ReadingSet":
        """Filter the reading set into a new set."""
        return ReadingSet([reading for reading in self.readings if predicate(reading)])

    def partition(self, predicate: Callable[["Reading"], bool]) -> tuple:
        """Split the reading into two based on a partition."""
        trues, falses = [], []
        for reading in self.readings:
            (trues if predicate(reading) else falses).append(reading)
        return ReadingSet(trues), ReadingSet(falses)

    def group(self, key: Callable[["Reading"], any]) -> dict:
        """Group the readings according to a keying function."""
        groups = defaultdict(list)
        for reading in self.readings:
            groups[key(reading)].append(reading)
        return {k: ReadingSet(v) for k, v in groups.items()}

    @staticmethod
    def from_string(string: str, has_tail: bool = True) -> "ReadingSet":
        """Read the output file of a wind tunnel run."""
        return ReadingSet(
            [
                Reading.from_string(line)
                for line in string.split("\n")[1:]
                # Sequential checks to ensure no out of bounds error
                if len(line) > 0 and len(line) >= 2 and line[:2] != "//"
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

    def from_folder(
        path: str, has_tail: bool = None, terminate_on_error: bool = False
    ) -> "ReadingSet":
        """Read and merge a number of sets of readings from a folder."""
        if path[-1] != "/":
            raise ValueError("path must end in '/'")

        sets = []
        for file_name in listdir(path):
            if terminate_on_error:
                sets.append(ReadingSet.from_file(path + file_name, has_tail=has_tail))
            else:
                try:
                    sets.append(
                        ReadingSet.from_file(path + file_name, has_tail=has_tail)
                    )
                except:
                    print(
                        "[WARNING]: failed to parse file '{}'".format(path + file_name)
                    )
        return ReadingSet.merge(*sets)


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
        yaw: float,
        pitch: float,
        airspeed: float,
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
        self.yaw, self.pitch = yaw, pitch
        self.airspeed = airspeed
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
