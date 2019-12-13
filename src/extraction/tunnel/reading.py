from datetime import datetime


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
    def read(string: str, has_tail: bool = True) -> "Reading":
        """Read a reading from its string representation."""
        segments = string.split(",")
        comments = segments[2].split("_")
        return Reading(
            datetime.strptime(segments[0] + " " + segments[1], "%d-%b-%y %H:%M:%S"),
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
