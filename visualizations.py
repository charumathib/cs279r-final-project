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
from matplotlib.colors import LinearSegmentedColormap


# globals
N_PLOTS = 3
N_MINUTES = 30

fig, axs = plt.subplots(N_PLOTS, 1, figsize=(12, 7))
data = [
    np.random.lognormal(mean=np.log(12), sigma=0.2, size=1_000_000),
    np.random.normal(loc=14, scale=0.5, size=1_000_000),
    np.random.normal(loc=16, scale=1.5, size=1_000_000)
    ]
xs = np.linspace(0, N_MINUTES, 100)

# 0.5 quantile 
times = [round(np.quantile(d, 0.5), 1) for d in data]
risks = [50.0, 50.0, 50.0]

# TODO: randomize condition and have it change on a button click so that we don't manually have to rerun the script each time

condition = "quantile"

if condition == "quantile":
    # TODO: figure out resizing
    plt.rcParams.update({'font.size': 15})
    for i in range(N_PLOTS):
        axs[i] = ntile_dotplot(data[i], dots=20, linewidth=0, ax=axs[i])

elif condition == "PDF":
    # PDFs specified in the form stats.lognorm([variance], mean) for lognormal and stats.norm([mean], variance) for normal
    dists = [stats.lognorm([0.2], scale=12), stats.norm([14], scale=0.5), stats.norm([16], scale=1.5)]
    colors = ["blue", "pink", "green"]
    # lines corresponding to time
    for i in range(N_PLOTS):
        ax = axs[i]
        ax.plot(xs, dists[i].pdf(xs), color = colors[i])
elif condition == "green-red":
    for i in range(N_PLOTS):
        cMap = []
        ax = axs[i]
        colTuples = [(stats.percentileofscore(data[i], x)/100, 1 - stats.percentileofscore(data[i], x)/100, 0) for x in xs]
        for value, colour in zip(xs, colTuples):
            cMap.append((value/N_MINUTES, colour))
        customColorMap = LinearSegmentedColormap.from_list("custom", cMap)
        ax.imshow(
            np.tile(np.linspace(0, 1, N_MINUTES + 1), (3, 1)),
            cmap = customColorMap,
            interpolation = 'bicubic',
        )

timeTextElems = []
riskTextElems = []
lines = []
for i in range(N_PLOTS):
    ax = axs[i]
    ax.set_xticks(np.linspace(0, N_MINUTES, 16))
    ax.set_xlim(left=0, right=N_MINUTES)
    ax.get_yaxis().set_visible(False)
    lines.append(ax.axvline(x = times[i], color = "black"))
    timeTextElems.append(ax.text(0.5, 1.5, f"{times[i]} mins", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes))
    riskTextElems.append(ax.text(0.5, 1.2, f"{risks[i]}% risk", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes))

# adjust the main plot to make room for the sliders and text
fig.subplots_adjust(bottom=0.25)
fig.subplots_adjust(top=0.85)
fig.subplots_adjust(hspace=1)

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
    valmin=0,
    valmax=N_MINUTES,
    valinit=N_MINUTES//2,
)

# we want to update our dotplot to have a line
def updateFreq(val):
    times = [round(np.quantile(d, val/100), 1) for d in data]
    risks = [round(val, 1)] * 3
    for i in range(N_PLOTS):
        timeTextElems[i].set_text(f"{times[i]} mins")
        riskTextElems[i].set_text(f"{risks[i]}% risk")
        lines[i].set_xdata(times[i])
        
    fig.canvas.draw_idle()
    time_slider.reset()

def updateTime(val):
    times = [round(val, 1)] * 3
    risks = [round(stats.percentileofscore(d, val), 1) for d in data]
    for i in range(N_PLOTS):
        timeTextElems[i].set_text(f"{times[i]} mins")
        riskTextElems[i].set_text(f"{risks[i]}% risk")
        lines[i].set_xdata(val)

    fig.canvas.draw_idle()
    freq_slider.reset()

# register the update function with each slider
freq_slider.on_changed(updateFreq)
time_slider.on_changed(updateTime)

plt.show()