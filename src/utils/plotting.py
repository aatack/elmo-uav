from typing import Union, Callable, List
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


PlotHandle = Union[Callable[[any], float], str]


def parse_plot_handle(plot_handle: PlotHandle) -> Callable[[any], float]:
    """Parse a plot handle, returning a function for a float."""
    if plot_handle is None:
        return None

    if isinstance(plot_handle, str):
        return lambda x: getattr(x, plot_handle)

    return plot_handle


def scatter(x: List[float], y: List[float], z: List[float] = None):
    """Scatter a series of points in either two or three dimensions."""
    if z is None:
        plt.plot(x, y, ".")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.show()
    else:
        figure = plt.figure()
        axes = figure.add_subplot(111, projection="3d")
        axes.scatter(x, y, z)

        axes.set_xlabel("x")
        axes.set_ylabel("y")
        axes.set_zlabel("z")

        plt.show()
