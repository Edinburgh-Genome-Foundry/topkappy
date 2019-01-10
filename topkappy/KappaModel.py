import kappy
from .KappaClasses import KappaAgent, KappaSiteState
from .FormattedKappaError import FormattedKappaError

class KappaModel:
    
    def __init__(self, agents, rules, initial_quantities,
                 snapshot_times=None, plots=(), plot_period=0.1,
                 duration=None, stop_condition=None):
        
        self.agents = agents
        self.rules = rules
        self.initial_quantities = initial_quantities
        self.snapshot_times  = snapshot_times or {}
        self.plots  = list(plots)
        self.set_parameters(duration=duration, stop_condition=stop_condition,
                            plot_period=plot_period)
    
    def set_parameters(self, duration=None, stop_condition=None,
                       plot_period=0.1):
        if stop_condition is None:
            stop_condition = "[T] > %.04f" % duration
        self.parameters = kappy.SimulationParameter(
            plot_period=plot_period,
            pause_condition=stop_condition,
        )
        
        
    def _kappa_script_for_agents_declarations(self):
        return "\n".join([a._kappa_declaration() for a in self.agents])

    def _kappa_script_for_rules(self):
        return "\n".join([r._kappa() for r in self.rules])

    def _kappa_script_for_initial_quantities(self):
        return "\n".join([
            '%%init: %d %s()' % (
                n, agent.name if isinstance(agent, KappaAgent) else agent)
            for agent, n  in self.initial_quantities.items()
        ])

    def _kappa_script_for_snapshots(self):
        return "\n".join([
            '%%mod: alarm %.03f do $SNAPSHOT "%s";' % (t, sid)
            for sid, t  in self.snapshot_times.items()
        ])

    def _auto_plot_item_string(self, item):
        if isinstance(item, KappaAgent):
            return '|%s()|' % item.name
        elif isinstance(item, KappaSiteState):
            return "|%s|" % item._kappa()
        else:
            return item
    def _kappa_script_for_plotted(self):
        return "\n".join([
            '%%plot: %s' % self._auto_plot_item_string(plot_item)
            for plot_item  in self.plots
        ])

    def _full_kappa_script(self):
        return "\n\n".join([
            self._kappa_script_for_agents_declarations(),
            self._kappa_script_for_rules(),
            self._kappa_script_for_initial_quantities(),
            self._kappa_script_for_snapshots(),
            self._kappa_script_for_plotted(),
        ])

    def get_simulation_results(self):
        
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
        return {
            'plots': plot_data,
            'snapshots': {
                sid: kappa_client.simulation_snapshot(sid)
                for sid in self.snapshot_times
            }
        }