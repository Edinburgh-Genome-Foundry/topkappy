import matplotlib.pyplot as plt

def plot_simulation_time_series(plots_data, ax=None):
    plots_data = dict(plots_data.items())
    times = plots_data.pop('[T]')
    if ax is None:
        _, ax = plt.subplots(1)
    for label, series in plots_data.items():
        ax.plot(times, series, label=label)
    ax.legend()
    return ax