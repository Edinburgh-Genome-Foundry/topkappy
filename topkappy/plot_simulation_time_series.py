import matplotlib.pyplot as plt

def plot_simulation_time_series(plots_data, ax=None):
    """Plot the time series data from a KappaModel simulation
    
    Examples
    --------

    >>> model = KappaModel(...)
    >>> simulation_results = model.get_simulation_results()
    >>> ax = plot_simulation_time_series(simulation_results['plots'])
    >>> ax.figure.savefig('basic_example_time_series.png')
    """
    
    plots_data = dict(plots_data.items())
    times = plots_data.pop('[T]')
    if ax is None:
        _, ax = plt.subplots(1)
    for label, series in plots_data.items():
        ax.plot(times, series, label=label)
    ax.legend()
    return ax