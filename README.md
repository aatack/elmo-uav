# ELMO-UAV

A collection of code used for the ELMO (electric modular) UAV project.

**NOTE:** unless otherwise specified, all examples should be run from the root directory (the same folder as this README file).

## Data extraction

### Wind Tunnel

Tools are made available for parsing the wind tunnel files output by the large wind tunnel, placing the data into a list of readings with appropriate field names, which can be queried using lambdas.
Most of these tools are static methods of the ReadingSet class:

```python
from src.extraction.tunnel.read import ReadingSet
readings = ReadingSet.from_folder("data/first-wind-tunnel/")
```

By default, error messages will be printed if a file cannot be read.
Flags can be set to cause the function to raise an exception if it encounters such a file instead.

A few conventions are followed:
- the comment taken with each reading describes its pitch, in degrees, aerofoil (`"N"` for NACA or `"C"` for Clark-Y), wing angle, and flap angle as `"pitch_aerofoil_wing_flap"`, eg. `"0_N_4_35"`;
- stability trials for which the tail was detached have the text `"notail"` somewhere in the file name.
