# source/dataframe.py

"""
Provides extended functionality by converting collection metadata into a Pandas
dataframe, including sorting, filtering, and the generation and display of graphs.
"""

# Standard library
import logging
import math
import os

# Third-party packages
import matplotlib as plt
import networkx as nx
import pandas as pd
import plotly.graph_objects as go


class CollectionDataframe:
    def __init__(self, collection: dict = None):
        # Convert the nested videos to a DataFrame
        # Create an empty DataFrame
        self.df = pd.DataFrame()
        if collection is None:
            logging.warning(
                'Collection dataframe was created, but no metadata was passed to the constructor. No metadata'
                'loaded.')
        else:
            self.load(collection)

    def filter(self, col, val, comp=None):
        if comp not in ('<', '>', None):
            raise ValueError("Optional comparator must be either '<' (less than) or '>' (greater than).")

        # This method of extracting numeric values of strings is tolerant of
        # ranges and unicode characters which are often present in OMDB videos.
        # Another method would be to use
        #
        # self.df = self.df[self.df[col].apply(pd.to_numeric, errors='coerce') < val]
        #
        # However, that results in lost entries.
        if isinstance(val, (int, float)):
            if comp == '<':
                # .extract() uses a regex to get the first number out of every entry in the column,
                # returns a dataframe, and .squeeze() turns it back into a column.
                # .to_numeric() turns out extracted stings into floats, wile errors='coerce' ignores
                # problems that otherwise arise from things like unicode characters.
                extract_num = self.df[col].str.extract('(\d+)').squeeze()
                str_to_float = pd.to_numeric(extract_num, errors='coerce')
                self.df = self.df[str_to_float < val]
            elif comp == '>':
                extract_num = self.df[col].str.extract('(\d+)').squeeze()
                str_to_float = pd.to_numeric(extract_num, errors='coerce')
                self.df = self.df[str_to_float > val]
            else:
                raise ValueError("Comparator must be specified for numeric values.")

        elif isinstance(val, str):
            if comp == '<':
                self.df = self.df[self.df[col].str.lower() < str(val).lower()]
            elif comp == '>':
                self.df = self.df[self.df[col].str.lower() > str(val).lower()]
            else:
                self.df = self.df[self.df[col].str.contains(str(val), case=False, na=False)]
        else:
            raise TypeError("Unsupported filter value type. Must be STR, INT, or FLOAT.")

        if comp is None:
            if isinstance(val, (str, int, float)):
                self.df = self.df[self.df[col].str.contains(str(val), case=False, na=False)]
            else:
                raise TypeError("Unsupported filter value type. Must be STR, INT, or FLOAT.")

    def sort(self, col):
        if self.df is None:
            raise ValueError(f"No dataframe is currently loaded, or it is empty. ")
        elif col not in self.df.columns:
            raise ValueError(f"Column {col} not in the current dataframe")
        else:
            self.df = self.df.sort_values(by=col)

    def load(self, collection):
        # This procedure prevents each column from being prefixed with the lengthy sha256 hash
        # Extract hashes and nested videos into separate lists
        hashes = list(collection.keys())
        nested_data = list(collection.values())

        # Create a "Video Hash" column
        self.df["Video Hash"] = hashes

        # Flatten the nested videos into columns and put it to the right of the hash column
        self.df = pd.concat([self.df, pd.json_normalize(nested_data)], axis=1)

        pd.set_option('display.max_columns', None)

    def generate_m3u_playlist(self):
        path = './playlist_example.m3u'
        playlist = ''
        for _, row in self.df.iterrows():
            root = row['file_data.root']
            filename = row['file_data.filename']
            entry = os.path.join(root, filename)
            entry = os.path.normpath(entry)
            playlist += entry + '\n'

        with open(path, 'w', encoding='utf-8') as file:
            file.write(playlist)

    def generate_graph(self):
        # Generates a graph associating movies by actors and directors
        g = nx.Graph()
        nodes = []
        for index, row in self.df.iterrows():
            title = row['omdb_data.Title']
            if title not in nodes:
                nodes.append(title)  # add movie to node list
                g.add_node(title, type="Movie")  # create movie node
                if type(row['omdb_data.Actors']) is str:
                    actors = row['omdb_data.Actors'].split(',')
                    for actor in actors:  # for each actor in movie
                        if actor not in nodes:  # if actor not in list
                            nodes.append(actor)  # add actors to node list
                            g.add_node(actor, type="Actor")  # create actor node
                        g.add_edge(title, actor)  # add edge from movie to actor
                if type(row['omdb_data.Director']) is str:
                    directors = row['omdb_data.Director'].split(',')
                    for director in directors:  # for each director in movie
                        if director not in nodes:  # if director not in node list
                            nodes.append(director)  # add director to node list
                            g.add_node(director, type="Director")  # create director node
                        g.add_edge(title, director)  # add edge from movie to director
        return g

    def trim_unrelated(self, g: nx.Graph):
        trim = []
        for node, data in g.nodes.data():
            if (data.get('type') == 'Actor') and (g.degree(node) < 2):
                trim.append(node)
            if (data.get('type') == 'Director') and (g.degree(node) < 2):
                trim.append(node)
        for node in trim:
            g.remove_node(node)
        trim.clear()
        for node, data in g.nodes.data():
            if (data.get('type') == 'Movie') and (g.degree(node) == 0):
                trim.append(node)
        for node in trim:
            g.remove_node(node)

    def display_graph(self, g):
        node_colors = []
        for n in g.nodes:
            node_type = g.nodes[n]['type']
            if node_type == 'Actor':
                node_colors.append('lightblue')
            elif node_type == 'Director':
                node_colors.append('lightgreen')
            elif node_type == 'Movie':
                node_colors.append('lightcoral')
            else:
                node_colors.append('gray')  # Default color for unknown types

        plt.figure(figsize=(50, 50))
        pos = nx.spring_layout(g, k=None)  # Okayish
        # pos = nx.arf_layout(g) # Evenly space, generally okay
        # pos = nx.shell_layout(g) # Terrible, just circular
        # pos = nx.circular_layout(g, scale=1, dim=1)  # Position nodes
        # pos = nx.planar_layout(g) # took too long to render
        # pos = nx.spectral_layout(g, weight=1, scale=0.01, center=(0,0), dim=2) # Promising, but spacing needs to be worked out
        # pos = nx.kamada_kawai_layout(g)
        pos = nx.fruchterman_reingold_layout(g, k=25 / math.sqrt(g.number_of_nodes()), iterations=1000)
        nx.draw(g, pos, with_labels=True, node_color=node_colors, node_size=5000, font_size=10, width=1.5)
        plt.show()

    def display_graph_plotly(self, G):
        pos = nx.fruchterman_reingold_layout(G, k=0.750, iterations=500)
        fig = go.Figure()

        # Define dictionaries to store node information based on type
        node_types = {'actor': [], 'director': [], 'movie': []}

        # Populate the dictionaries based on node type
        for node, node_type in G.nodes(data='type'):
            x, y = pos[node]
            text = f'Node {node} ({node_type})'
            # Convert node_type to lowercase
            node_type = node_type.lower()
            node_types[node_type].append(dict(x=x, y=y, text=text))

        # Add traces for each node type
        for node_type, node_info in node_types.items():
            x_values = [info['x'] for info in node_info]
            y_values = [info['y'] for info in node_info]
            text_values = [info['text'] for info in node_info]

            fig.add_trace(go.Scatter(
                x=x_values, y=y_values, mode='markers',
                text=text_values, hoverinfo='text',
                marker=dict(size=10, color=self.get_node_color(node_type)),  # You can customize the color
            ))

        # Add edges
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            fig.add_trace(go.Scatter(x=[x0, x1, None], y=[y0, y1, None],
                                     mode='lines', line=dict(width=0.5, color='#888')))

        # Add annotations for node labels
        for node, (x, y) in pos.items():
            fig.add_annotation(
                x=x, y=y, text=f'{node}', showarrow=False,
                font=dict(size=10, color='black'), xshift=10, yshift=10  # Adjust the position of the labels
            )

        # Update layout for better presentation
        fig.update_layout(
            hovermode='closest',
        )

        # Show the plot
        fig.show()

    def get_node_color(self, node_type):
        # Define a color mapping for each node type
        color_mapping = {'actor': 'blue', 'director': 'green', 'movie': 'red'}
        return color_mapping.get(node_type, 'blue')  # Default to blue if the type is not recognized

    def __repr__(self):
        return self.df.__repr__()