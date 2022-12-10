import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from quantile_dotplot import ntile_dotplot
from scipy import stats
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as patches


# globals
N_PLOTS = 3
N_MINUTES = 30

data = [
    np.random.lognormal(mean=np.log(12), sigma=0.2, size=1_000_000),
    np.random.normal(loc=14, scale=0.5, size=1_000_000),
    np.random.normal(loc=16, scale=1.5, size=1_000_000)
    ]
xs = np.linspace(0, N_MINUTES, 200)

# 0.5 quantile 
times = [round(np.quantile(d, 0.5), 1) for d in data]
risks = [50.0, 50.0, 50.0]
colors = ["blue", "pink", "green"]
fig, axs = None, None

def quantilePlot():
    plt.rcParams.update({'font.size': 25})
    for i in range(N_PLOTS):
        axs[i] = ntile_dotplot(data[i], dots=20, facecolor=colors[i], linewidth=0, ax=axs[i])

def pdfPlot():
    plt.rcParams.update({'font.size': 10})
    # PDFs specified in the form stats.lognorm([variance], mean) for lognormal and stats.norm([mean], variance) for normal
    dists = [stats.lognorm([0.2], scale=12), stats.norm([14], scale=0.5), stats.norm([16], scale=1.5)]
    # lines corresponding to time
    for i in range(N_PLOTS):
        ax = axs[i]
        ax.plot(xs, dists[i].pdf(xs), color = colors[i])

def greenRedPlot():
    plt.rcParams.update({'font.size': 10})
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

# shuffled list of all the plot types
timeTextElems = []
riskTextElems = []
lines = []

def transformAxs(axs):
    for i in range(N_PLOTS):
        ax = axs[i]
        ax.set_xticks(np.linspace(0, N_MINUTES, 16))
        ax.set_xlim(left=0, right=N_MINUTES)
        ax.get_yaxis().set_visible(False)
        lines.append(ax.axvline(x = times[i], color = "black"))
        timeTextElems.append(ax.text(0.5, 1.5, f"{times[i]} mins", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes))
        riskTextElems.append(ax.text(0.5, 1.2, f"{risks[i]}% risk", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes))

        bottom, top = ax.get_ylim()
        mid = (bottom + top)/2
        if i == 0:
            ax.text(-3, mid, ' QYE ', color='blue', 
                bbox=dict(facecolor='none', edgecolor='blue', boxstyle='round,pad=1', linewidth=2))
        elif i == 1:
            ax.text(-3, mid, '  AL  ', color='pink', 
                bbox=dict(facecolor='none', edgecolor='pink', boxstyle='round,pad=1', linewidth=2))
        else:
            ax.text(-3, mid, '  CC  ', color='green', 
                bbox=dict(facecolor='none', edgecolor='green', boxstyle='round,pad=1', linewidth=2))

plots = [pdfPlot, quantilePlot, greenRedPlot]
random.shuffle(plots)
for plot in plots:
    fig, axs = plt.subplots(N_PLOTS, 1, figsize=(12, 7))
    plot()
    transformAxs(axs)

    # add the sliders
    fig.subplots_adjust(bottom=0.25)
    fig.subplots_adjust(top=0.85)
    fig.subplots_adjust(hspace=1)

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

    def updateFreq(val):
        times = [round(np.quantile(d, val/100), 1) for d in data]
        risks = [round(val, 1)] * 3
        for i in range(N_PLOTS):
            timeTextElems[i].set_text(f"{times[i]} mins")
            riskTextElems[i].set_text(f"{risks[i]}% risk")
            lines[i].set_xdata(times[i])
        
        freq_slider.poly.set_fc('#2074b4')
        time_slider.poly.set_fc('grey')

        fig.canvas.draw_idle()
        time_slider.reset()  

    def updateTime(val):
        times = [round(val, 1)] * 3
        risks = [round(stats.percentileofscore(d, val), 1) for d in data]
        for i in range(N_PLOTS):
            timeTextElems[i].set_text(f"{times[i]} mins")
            riskTextElems[i].set_text(f"{risks[i]}% risk")
            lines[i].set_xdata(val)

        time_slider.poly.set_fc('#2074b4')
        freq_slider.poly.set_fc('grey')

        fig.canvas.draw_idle()
        freq_slider.reset()

    # register the update function with each slider
    freq_slider.on_changed(updateFreq)
    time_slider.on_changed(updateTime)

    manager = plt.get_current_fig_manager()
    manager.full_screen_toggle()
    plt.show()


