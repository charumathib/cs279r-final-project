import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from dotplot import ntile_dotplot
from scipy import stats


# globals
N_PLOTS = 3
N_MINUTES = 20


data = [
    np.random.gamma(1.5, 2.0, size=1_000_000),
    np.random.gamma(7.0, 1.0, size=1_000_000),
    np.random.gamma(25.0, 0.5, size=1_000_000),
    ]
xs = np.linspace(0, N_MINUTES, 200)

# 0.5 quantile 
times = [round(np.quantile(d, 0.5), 1) for d in data]
risks = [50.0, 50.0, 50.0]
colors = ["blue", "pink", "green"]
fig, axs = None, None

def quantilePlot():
    plt.rcParams.update({'font.size': 12})
    for i in range(N_PLOTS):
        axs[i] = ntile_dotplot(data[i], dots=20, facecolor=colors[i], linewidth=0, ax=axs[i])

def pdfPlot():
    plt.rcParams.update({'font.size': 12})
    # PDFs specified in the form stats.lognorm([variance], mean) for lognormal and stats.norm([mean], variance) for normal
    dists = [stats.gamma(1.5, scale = 2.0), stats.gamma(7.0, scale = 1.0), stats.gamma(25.0,  scale = 0.5)]
    # lines corresponding to time
    for i in range(N_PLOTS):
        ax = axs[i]
        ax.plot(xs, dists[i].pdf(xs), color = colors[i])

def greenRedPlot():
    plt.rcParams.update({'font.size': 12})
    for i in range(N_PLOTS):
        ax = axs[i]
        for x in xs:
            ax.set_ylim(bottom=0, top=1)
            ax.scatter(x, 0.5, color=(stats.percentileofscore(data[i], x)/100, 1 - stats.percentileofscore(data[i], x)/100, 0), marker="s")

# shuffled list of all the plot types
def transformAxs(axs):
    timeTextElems, riskTextElems, lines = [], [], []
    for i in range(N_PLOTS):
        ax = axs[i]
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_xlim(left=0, right=N_MINUTES)
        ax.set_xticks(np.linspace(0, N_MINUTES, 11))
        ax.get_yaxis().set_visible(False)
        lines.append(ax.axvline(x = times[i], color = "black"))
        timeTextElems.append(ax.text(0.5, 1.5, f"{times[i]} mins", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, weight="bold"))
        riskTextElems.append(ax.text(0.5, 1.2, f"{risks[i]}% risk", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, weight="bold"))

        _, top = ax.get_ylim()
        if i == 0:
            ax.text(0, top, ' QYE ', color='blue', 
                bbox=dict(facecolor='none', edgecolor='blue', boxstyle='round,pad=0.5', linewidth=1))
        elif i == 1:
            ax.text(0, top, '  AL  ', color='pink', 
                bbox=dict(facecolor='none', edgecolor='pink', boxstyle='round,pad=0.5', linewidth=1))
        else:
            ax.text(0, top, '  CC  ', color='green', 
                bbox=dict(facecolor='none', edgecolor='green', boxstyle='round,pad=0.5', linewidth=1))
        
    return timeTextElems, riskTextElems, lines

plots = [quantilePlot, pdfPlot, greenRedPlot]
random.shuffle(plots)
for plot in plots:
    fig, axs = plt.subplots(N_PLOTS, 1, figsize=(3.5, 6))
    plot()
    timeTextElems, riskTextElems, lines = transformAxs(axs)

    # add the sliders
    fig.subplots_adjust(bottom=0.25)
    fig.subplots_adjust(top=0.85)
    fig.subplots_adjust(hspace=1)

    axrisk = fig.add_axes([0.35, 0.1, 0.5, 0.03])
    freq_slider = Slider(
        ax=axrisk,
        label='Risk slider (%)',
        valmin=0,
        valmax=100,
        valinit=50,
    )

    axtime = fig.add_axes([0.35, 0.05, 0.5, 0.03])
    time_slider = Slider(
        ax=axtime,
        label='Time slider (min)',
        valmin=0,
        valmax=N_MINUTES,
        valinit=N_MINUTES//2,
    )

    freq_slider.label.set_size(9)
    time_slider.label.set_size(9)

    def updateFreq(val):
        times = [round(np.quantile(d, val/100), 1) for d in data]
        risks = [round(val, 1)] * 3
        for i in range(N_PLOTS):
            timeTextElems[i].set_text(f"{times[i]} mins")
            riskTextElems[i].set_text(f"{risks[i]}% risk")
            lines[i].set_xdata(min(times[i], N_MINUTES))
        
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
    plt.show()


