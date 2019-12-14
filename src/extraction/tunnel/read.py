from typing import Callable, List, Tuple, Union
from collections import defaultdict
from datetime import datetime
from os import listdir
import src.utils.plotting as pu


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
                Reading.from_string(line, has_tail=has_tail)
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
                f.read(), has_tail if (has_tail is not None) else not ("notail" in path)
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

    def offset_groups(self) -> dict:
        """Split the set into subsets based on which offset each should use."""
        return self.group(Reading.offset_key)

    def plot(self, x: pu.PlotHandle, y: pu.PlotHandle, z: pu.PlotHandle = None):
        """Plot a property of each reading in either two or three dimensions."""
        x, y, z = (pu.parse_plot_handle(d) for d in (x, y, z))
        pu.scatter(
            [x(r) for r in self.readings],
            [y(r) for r in self.readings],
            [z(r) for r in self.readings] if z is not None else None,
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

    def offset(self, other: "Reading") -> "Reading":
        """Copy this reading after adjusting the force/moment values for calibration."""
        return Reading(
            self.timestamp,
            self.lift - other.lift,
            self.drag - other.drag,
            self.side - other.side,
            self.pitch_moment - other.pitch_moment,
            self.roll_moment - other.roll_moment,
            self.yaw_moment - other.yaw_moment,
            self.yaw,
            self.pitch,
            self.airspeed,
            self.aerofoil,
            self.wing_angle,
            self.flap_angle,
            self.has_tail,
        )

    @staticmethod
    def offset_key(reading: "Reading") -> str:
        """Determine a unique identifier for this reading's offset type."""
        return "_".join(
            [
                str(s)
                for s in (
                    reading.aerofoil,
                    reading.has_tail,
                    reading.wing_angle,
                    reading.flap_angle,
                )
            ]
        )

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
