import kappy
from .KappaClasses import KappaAgent, KappaSiteState
from .FormattedKappaError import FormattedKappaError

class KappaModel:
    """Class to represent Kappa models and create corresponding Kappa scripts.

    See the README example for a quick intro.

    Parameters
    ----------

    agents
      List of all KappaAgent in the model
    
    rules
      List of all KappaRule in the model
    
    initial_quantities
      Either a dict {agent_name: initial_quantity} or a single integer
      if all agents start with the same initial quantity. Note that the
      more initial agents, the less noisy the simulation results

    duration
      Virtual duration of the simulation, in seconds

    snapshot_times 
        A dict {snapshot_name: time}, e.g. {'end': 10}. The snapshot can then
        be accessed as simulation_results['snapshots']['end']
    
    plots
      List of Kappa expressions to plot. Each list element can be either
      a string (a Kappa expression like ``|A(.)|``) or a KappaSiteState like
      ``[KappaSiteState('B', 'b', '.'), KappaSiteState('C', 'c', '.')]``
    
    plot_time_step
      Time interval between two points when gathering data for plotting.

    stop_condition
      String representing a Kappa stopping condition. If none is provided,
      the simulation stops after the provided ``duration`` is reached.
      
    """
    
    def __init__(self, agents, rules, initial_quantities,
                 snapshot_times=None, plots=(), plot_time_step=0.1,
                 duration=None, stop_condition=None):
        
        self.agents = agents
        self.rules = rules
        self.initial_quantities = initial_quantities
        self.snapshot_times  = snapshot_times or {}
        self.plots  = list(plots)
        self.set_parameters(duration=duration, stop_condition=stop_condition,
                            plot_time_step=plot_time_step)
    
    def set_parameters(self, duration=None, stop_condition=None,
                       plot_time_step=0.1):
        """(Re-)set some parameters of the model.

        Do not attempt to set these parameters otherwise than with this
        function, e.g. directly by accessing self.parameters: it won't work.
        """
        if stop_condition is None:
            stop_condition = "[T] > %.04f" % duration
        self.parameters = kappy.SimulationParameter(
            plot_period=plot_time_step,
            pause_condition=stop_condition,
        )
        
        
    def _kappa_script_for_agents_declarations(self):
        """Generate the script for declaring agents."""
        return "\n".join([a._kappa_declaration() for a in self.agents])

    def _kappa_script_for_rules(self):
        """Generate the script for declaring all complexation rules."""
        return "\n".join([r._kappa() for r in self.rules])

    def _kappa_script_for_initial_quantities(self):
        """Generate the script for declaring all initial quantities."""
        return "\n".join([
            '%%init: %d %s()' % (
                n, agent.name if isinstance(agent, KappaAgent) else agent)
            for agent, n  in self.initial_quantities.items()
        ])

    def _kappa_script_for_snapshots(self):
        """Generate the script for declaring when snapshots are recorded."""
        return "\n".join([
            '%%mod: alarm %.03f do $SNAPSHOT "%s";' % (t, sid)
            for sid, t  in self.snapshot_times.items()
        ])

    def _auto_plot_item_string(self, item):
        """Generate the Kappa string for the number of agents or sites.
        
        This is mainly a helper for _kappa_script_for_plotted
        """
        if isinstance(item, KappaAgent):
            return '|%s()|' % item.name
        elif isinstance(item, KappaSiteState):
            return "|%s|" % item._kappa()
        else:
            return item

    def _kappa_script_for_plotted(self):
        """Generate the script for declaring what gets plotted."""
        return "\n".join([
            '%%plot: %s' % self._auto_plot_item_string(plot_item)
            for plot_item in self.plots
        ])

    def _full_kappa_script(self):
        """Generate the full script to be passed to the Kappa simulator."""
        return "\n\n".join([
            self._kappa_script_for_agents_declarations(),
            self._kappa_script_for_rules(),
            self._kappa_script_for_initial_quantities(),
            self._kappa_script_for_snapshots(),
            self._kappa_script_for_plotted(),
        ])

    def get_simulation_results(self):
        """Run a simulation of the model and return results as a dict.
        
        The result is of the form {plots: {}, snapshots {}}.

        The plots dict is of the form {'[T]': [...], 'A()': [...]} where the
        values are lists of numbers.

        The snapshots dict is of the form {snapshot_name: data} where the
        data is a complicated listing of the different complexes observed at
        that time point, and how often they occur. (See kappy documentation
        for more).

        Topkappy has a methods like ``plot_simulation_time_series`` or
        ``plot_snapshot_agents`` to help make sense of the simulation
        results.
        """
        model_string = self._full_kappa_script()
        kappa_client = kappy.KappaStd()
        kappa_client.add_model_string(model_string)
        try:
            kappa_client.project_parse()
        except kappy.KappaError as kappa_error:
            raise FormattedKappaError.from_kappa_error(kappa_error,
                                                       model_string)
        kappa_client.simulation_start(self.parameters)
        kappa_client.wait_for_simulation_stop()
        plot_data = kappa_client.simulation_plot()
        plot_data = dict(zip(plot_data['legend'], zip(*plot_data['series'])))
        snapshots = {}
        for sid in list(self.snapshot_times) + ['deadlock']:
            try:
                snapshots[sid] = kappa_client.simulation_snapshot(sid + '.ka')
            except:
                try:
                    snapshots[sid] = kappa_client.simulation_snapshot(sid)
                except:
                    pass
        return {
            'plots': plot_data,
            'snapshots': snapshots
        }