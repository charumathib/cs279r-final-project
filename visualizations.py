"""
======
Slider
======

In this example, sliders are used to control the frequency and amplitude of
a sine wave.

See :doc:`/gallery/widgets/slider_snap_demo` for an example of having
the ``Slider`` snap to discrete values.

See :doc:`/gallery/widgets/range_slider` for an example of using
a ``RangeSlider`` to define a range of values.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from quantile_dotplot import ntile_dotplot
from scipy import stats
from scipy.stats import lognorm
from coloraide import Color
from matplotlib.colors import LinearSegmentedColormap


plt.rcParams.update({'font.size': 15})

# Define initial parameters

# Create the figure and the line that we will manipulate
fig, ax = plt.subplots(figsize=(18, 11))
data = np.random.lognormal(mean=np.log(12), sigma=0.2, size=1_000_000)
time = f"{round(np.quantile(data, 0.5), 3)} mins"
risk = "50.000%"

condition = "quantile"

if condition == "quantile":
    # quantile dotplot
    ax = ntile_dotplot(data, dots=20, edgecolor="k", linewidth=2, ax=ax)
elif condition == "PDF":
    # PDF
    frozen_lognorm = stats.lognorm([0.2], scale=12)
    x=np.linspace(8,18,200)
    print(x)
    ax.plot(x, frozen_lognorm.pdf(x))
elif condition == "red-green":
    # red-green color slider
    cMap = []
    xRange = list(np.linspace(0, 20, 100))
    colTuples = [(stats.percentileofscore(data, x)/100, 1 - stats.percentileofscore(data, x)/100, 0) for x in xRange]
    for value, colour in zip(xRange, colTuples):
        cMap.append((value/20, colour))

    customColourMap = LinearSegmentedColormap.from_list("custom", cMap)
    print(customColourMap)
    ax.imshow(np.vstack((np.linspace(0, 1, 18), np.linspace(0, 1, 18), np.linspace(0, 1, 18))),
    cmap = customColourMap,
    interpolation = 'bicubic',
    )
    ax.set_xlim(left=8, right=17.5)
    ax.get_yaxis().set_visible(False)

line = ax.axvline(x = 10, color = 'b', label = 'axvline - full height')

# adjust the main plot to make room for the sliders
fig.subplots_adjust(bottom=0.25)

# Make a horizontal slider to control the frequency.
axrisk = fig.add_axes([0.25, 0.1, 0.65, 0.03])
freq_slider = Slider(
    ax=axrisk,
    label='Risk slider (%)',
    valmin=0,
    valmax=100,
    valinit=50,
)

axtime = fig.add_axes([0.25, 0.05, 0.65, 0.03])
time_slider = Slider(
    ax=axtime,
    label='Time slider (min)',
    valmin=7,
    valmax=18,
    valinit=np.quantile(data, 0.5),
)

textTime = ax.text(0.5, 1.1, time, horizontalalignment='center',
     verticalalignment='center', transform=ax.transAxes)
textRisk = ax.text(0.5, 1.03, risk, horizontalalignment='center',
     verticalalignment='center', transform=ax.transAxes)

# we want to update our dotplot to have a line
def updateFreq(val):
    quantile = np.quantile(data, val/100)
    textTime.set_text(f"{round(quantile, 3)} mins")
    textRisk.set_text(f"{round(val, 3)}%")
    time_slider.reset()
    line.set_xdata(quantile)
    fig.canvas.draw_idle()

def updateTime(val):
    freq_slider.reset()
    textTime.set_text(f"{round(val, 3)} mins")
    textRisk.set_text(f"{round(stats.percentileofscore(data, val), 3)}%")
    line.set_xdata(val)
    fig.canvas.draw_idle()

# register the update function with each slider
freq_slider.on_changed(updateFreq)
time_slider.on_changed(updateTime)

# Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
plt.show()

#############################################################################
#
# .. admonition:: References
#
#    The use of the following functions, methods, classes and modules is shown
#    in this example:
#
#    - `matplotlib.widgets.Button`
#    - `matplotlib.widgets.Slider`
