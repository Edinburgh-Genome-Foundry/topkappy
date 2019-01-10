import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def snapshot_agent_nodes_to_graph(nodes, with_ports=True):
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
    if layout_method == 'FR':
        positions = nx.layout.fruchterman_reingold_layout(graph, seed=pos_seed)
    elif layout_method == 'spectral':
        positions = nx.layout.spectral_layout(graph)
    elif layout_method == 'spring':
        positions = nx.layout.spring_layout(graph, seed=seed)
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
