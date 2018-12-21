class KappaAgent:
    
    def __init__(self, name, sites):
        self.name = name
        self.sites = sites

    def _kappa_declaration(self):
        return "%%agent: %s(%s)" % (self.name, ", ".join(self.sites))
    def __str__(self):
        return self._kappa_declaration()

class KappaSiteState:
    
    def __init__(self, agent, site, state='.'):
        if isinstance(agent, KappaAgent) and (site not in agent.sites):
            raise ValueError("%s has not site %s" % (agent, site))
        self.agent = agent
        self.site = site
        self.state = state
    def _kappa(self):
        agent =  self.agent
        if isinstance(agent, KappaAgent):
            agent = agent.name
        return "%s(%s[%s])" % (agent, self.site, self.state)

class KappaRule:
    
    def __init__(self, name, reactants, sense, products, rate):
        self.name = name
        self.reactants = reactants
        self.products = products
        self.rate = rate
        self.sense = sense
    
    def _kappa(self):
        if isinstance(self.rate, (list, tuple)):
            rate = self.rate
        else:
            rate = str(self.rate)
        return "'%s' %s %s %s @ %s" % (
            self.name,
            ",".join(reactant._kappa() for reactant in self.reactants),
            self.sense,
            ",".join(product._kappa() for product in self.products),
            rate
        )