import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def snapshot_agent_nodes_to_graph(nodes, with_ports=True):
    """Turn a simulation result into a networkx graph of a bio-complex.
    
    The "nodes" are from the representation of a snapshot agent.

    If with_port is true, the ports (= agents binding sites) will be
    represented as nodes in the graph.

    Examples:
    --------

    >>> sim_results = model.get_simulation_results()
    >>> n, nodes = sim_results['snapshots']['NAME']['snapshot_agents']
    >>> graph = snapshot_agent_nodes_to_graph(nodes, with_ports=True)
    """
    graph = nx.Graph()
    for i, node in enumerate(nodes):
        graph.add_node(i, node_type='agent', node_name=node['node_type'])
        for j, site in enumerate(node['node_sites']):
            site_type, site_data = site['site_type']
            graph.add_node((i, j), node_type=site_type,
                           node_name=site['site_name'])
            graph.add_edge(i, (i, j), edge_type='port', weight=4)
            if site_type == 'port':
                for link in site_data['port_links']:
                    graph.add_edge((i, j), tuple(link), edge_type='link',
                                   weight=1)
    if not with_ports:
        for node_id, node in list(graph.nodes.items()):
            if node['node_type'] == 'agent':
                node_name = node['node_name']
                for neighbor in list(graph.neighbors(node_id)):
                    graph.remove_edge(node_id, neighbor)
                    graph = nx.contracted_nodes(graph, node_id, neighbor)
                graph.nodes[node_id]['node_name'] = node_name 
    return graph


def plot_snapshot_agent_nodes_graph(graph, ax=None, positions=None,
                                    pos_seed=123, figsize=(4, 4),
                                    layout_method='FR'):
    """Plot a graph of a complex agent from a snapshot.

    Parameters
    ----------
    graph
      The graph to be plotted.

    ax
      A matplotlib ax on which to draw the figure. If none is provided, a
      new figure and ax will be created and returned at the end

    positions
      A dict {node: position}. A ``layout_method`` can be provided instead
      for automatic positioning.

    pos_seed
      A seed to freeze the positions when using semi-random positioning
      methods.

    figsize
      Dimensions of the figure in inches (if ax is not provided)
    
    layout_method
      Networkx layout method for the graph drawing.
      Either 'FR' (fruchterman_reingold), 'spectral' or 'spring'.
    
    """
    if layout_method == 'FR':
        positions = nx.layout.fruchterman_reingold_layout(graph, seed=pos_seed)
    elif layout_method == 'spectral':
        positions = nx.layout.spectral_layout(graph)
    elif layout_method == 'spring':
        positions = nx.layout.spring_layout(graph, seed=pos_seed)
    else:
        raise ValueError('Unsupported layout_method %s' % layout_method)
    if ax is None:
        _, ax = plt.subplots(1, figsize=figsize)
    ax.axis('off')
    for edge in graph.edges():
        edge_type = graph.get_edge_data(*edge)['edge_type']
        is_port = edge_type == "port"
        (x1, y1), (x2, y2) = positions[edge[0]], positions[edge[1]]
        ax.plot([x1, x2], [y1, y2],
                color='#5d51da' if is_port else 'black',
                lw=4 if is_port else 1)
    for node, pos in positions.items():
        graph_node = graph.node[node]
        is_agent = graph_node['node_type'] == 'agent'
        ax.text(pos[0], pos[1], graph_node['node_name'],
                ha='center', va='center',
                bbox=dict(boxstyle='round',
                          facecolor='#e7e5f9' if is_agent else 'white',
                          edgecolor='grey'),
                fontdict=dict(weight='bold' if is_agent else 'normal'))


def plot_snapshot_agents(agents, with_ports=True, columns='auto', ax_inches=3,
                         layout_method='FR', freq_cutoff=0):
    """Plot graph representations of all complexes in a multi-ax figure.
    
    Parameters
    ----------
    agents
      Snapshot agents as provided in the result of ``get_simulation_results()``
      by ``simulation_results['snapshots']['SNAP_NAME']['snapshot_agents']``
    
    with_ports
      If true, ports (= agents binding sites) will be represented on the
      figure.
    
    columns
      How many columns (= plots by lines) in the figure ? Keep to "auto"
      for a more-or-less squared figure.
    
    ax_inches
      Size of one figure in inches
    
    layout_method
      Networkx layout method for the graph drawing.
      Either 'FR' (fruchterman_reingold), 'spectral' or 'spring'.
    
    freq_cutoff
      All complexes with a number of occurences lower than frew_cutoff in
      the snapshot will be ignored.

    Returns
    -------

    fig, axes
      Matplotlib "figure" and "axes" list of the multi-ax figure generated.
    """
    total_agents = sum(n for n, data in agents)
    # Normalize frequencies, filter, and sort agents.
    agents = sorted([
        (100.0 * frequency / total_agents, nodes)
        for frequency, nodes in agents
        if (1.0 * frequency / total_agents) > freq_cutoff
    ], key=lambda a: -a[0])
    if columns == 'auto':
        columns = int(np.sqrt(len(agents)) + 1)
    rows = int(np.ceil(len(agents) / columns))
    figsize = (ax_inches * columns, ax_inches * rows)
    fig, axes = plt.subplots(rows, columns, figsize=figsize)
    for ax in axes.flatten():
        ax.axis('off')
    for ax, (frequency, nodes) in zip(axes.flatten(), agents):
        graph = snapshot_agent_nodes_to_graph(nodes, with_ports=with_ports)
        plot_snapshot_agent_nodes_graph(graph, ax=ax,
                                        layout_method=layout_method)
        ax.set_title("%.01f%%\n" % frequency)
    fig.tight_layout()
    fig.subplots_adjust(hspace=0.8, top=0.8)
    return fig, axes
