import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def graph(lib, list_classes_for_graph, dict_classes_sizes, class_counter_lt_gt, max_subclasses, min_subclasses, size_image=50):
    fig, ax = plt.subplots()
    fig.set_size_inches(size_image, size_image)
    fig.patch.set_visible(False)
    ax.set_facecolor('k')
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

    DG = nx.DiGraph()
    G = nx.Graph()

    for i in list_classes_for_graph:
        if i[0] not in class_counter_lt_gt and i[1] not in class_counter_lt_gt:
            DG.add_edge(i[0], i[1])
            G.add_edge(i[0], i[1])

    df = pd.DataFrame(list(G.degree), columns=['node','degree']).set_index('node')
    if df.empty:
        print("Graph is empty")
        sys.exit()
    df_size = pd.DataFrame({'node': list(dict_classes_sizes.keys()), 'size': list(dict_classes_sizes.values())})
    df = pd.merge(df, df_size, how='left', on='node')
    df['color'] = df['size'].rank()
    vmin = df['color'].min()
    vmax = df['color'].max()
    cmap = plt.cm.rainbow

    pos = nx.spring_layout(G, k=0.2, seed=38)
    nx.draw_networkx(DG, pos=pos, arrows=True, arrowsize=20, node_size=df.degree*100, node_color=df['color'],\
                     edge_color='grey', font_color='white', cmap=cmap, vmin=vmin, vmax=vmax)
    plt.savefig(f'{lib}_gt_{min_subclasses}_lt_{max_subclasses}.png')
