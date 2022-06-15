from random import random, randint, choice
from igraph import Graph


class Node:
    """
    Class represents node of directed tree
    """
    def __init__(self, parent, p10, p11, is_leaf=False, id=0):
        self.id = id
        self.parent = parent
        self.p10 = p10
        self.p11 = p11
        self.value = None
        self.siblings = []
        self.is_leaf = is_leaf


def generateTransaction(root: Node, result: list):
    """
    Function generate transaction by a model with a given root
    """
    if root.parent is None:
        root.value = 1 if random() < root.p11 else 0
    else:
        if root.parent.value == 1:
            root.value = 1 if random() < root.p11 else 0
        else:
            root.value = 1 if random() < root.p10 else 0

    if root.is_leaf:
        result.append(root.value)

    for sibling in root.siblings:
        generateTransaction(sibling, result)

    return result


def numerate_graph(root: Node, last_id=[0]):
    """
    Function for proper numeration of nodes for a picture
    """
    root.id = last_id[0]
    for sib in root.siblings:
        last_id[0] += 1
        numerate_graph(sib, last_id)


def generate_igraph(root: Node, graph=Graph()):
    """
    Function fills vertices with a proper color
    """
    for sib in root.siblings:
        color = "green" if sib.is_leaf else "red"
        graph.add_vertex(sib.id, color=color)
        graph.add_edge(root.id, sib.id)
        generate_igraph(sib, graph)

    return graph


def generateNTree(n):
    """
    Function generates random tree with n verices
    """
    max_degree = 5
    vertices = 1
    root = Node(None, random(), random(), True)
    siblings_number = randint(1, min(n, max_degree))
    #siblings_number = n - 1
    layer1 = []
    for x in range(siblings_number):
        layer1.append(Node(root, random(), random(), True))
        vertices += 1
    root.siblings.extend(layer1)

    root_layer = [root]
    while vertices < n:
        root_candidates = []
        for i_root in root_layer:
            for sib in i_root.siblings:
                siblings_number = randint(1, min(n - vertices + 1, max_degree))
                layer1 = []
                for x in range(siblings_number):
                    layer1.append(Node(sib, random(), random(), True))
                    vertices += 1
                    if vertices == n:
                        sib.siblings.extend(layer1)
                        numerate_graph(root, [0])
                        return root
                sib.siblings.extend(layer1)
                root_candidates.append(sib)
        root_layer = root_candidates
    numerate_graph(root, [0])
    return root
