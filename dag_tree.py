from random import random, randint, choice
from igraph import Graph


class Node:
    def __init__(self, parent, p10, p11, is_leaf=False, id=0):
        self.id = id
        self.parent = parent
        self.p10 = p10
        self.p11 = p11
        self.value = None
        self.siblings = []
        self.is_leaf = is_leaf


def printTree(root: Node, c: int = 0, small=False):
    last_sibling = root
    if not small:
        if root.parent is None:
            print(f'{root.id} is root and is_leaf = {root.is_leaf} p10 = {root.p10} p11 = {root.p11}')
        else:
            print(f'{root.id} is a sibling of {root.parent.id} and is_leaf = {root.is_leaf} p10 = {root.p10} p11 = {root.p11}')
    if len(root.siblings) == 0:
        return c
    for sibling in root.siblings:
        c = printTree(sibling, c + 1 if sibling.is_leaf else c, small=small)
        last_sibling = sibling
    return c


def generateTransaction(root: Node, result: list):
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


def generateStar(n, randomize_weights=False, p10=0.5, p11=0.5):
    if randomize_weights:
        root = Node(None, random(), random(), False)
        root.siblings.extend([Node(root, random(), random(), True) for x in range(n)])
    else:
        root = Node(None, p10, p11, False)
        root.siblings.extend([Node(root, p10, p11, True) for x in range(n)])
    return root


def generatePath(n, randomize_weights=False, p10=0.5, p11=0.5):
    all_root = None
    if randomize_weights:
        root = Node(None, random(), random(), True)
        all_root = root
        for x in range(n - 1):
            root.siblings.append(Node(root, random(), random(), True))
            root = root.siblings[-1]
    else:
        root = Node(None, p10, p11, True)
        all_root = root
        for x in range(n - 1):
            root.siblings.append(Node(root, p10, p11, True))
            root = root.siblings[-1]
    return all_root


def generateRandomTree(n, k, p10=0.5, p11=0.5, leaf_chance=0.5):
    all_possible_leaves = set()
    root = Node(None, p10, p11, id=-1)
    leaf_count = 0
    i = 1
    id_offset = 0
    last_layer = [Node(None, p10, p11, id=_ + id_offset) for _ in range(n)]
    id_offset += 2 * n
    all_possible_leaves.update(last_layer)
    while i < k and leaf_count != n:
        parentless_last_count = 0
        for l in last_layer:
            if l.parent is None:
                parentless_last_count += 1
        for x in last_layer:
            if not x.is_leaf and random() < leaf_chance and leaf_count < n:
                x.is_leaf = True
                leaf_count += 1
        inner_nodes = [Node(None, p10, p11, id=_ + id_offset) for _ in range(parentless_last_count)]
        id_offset += 2 * n
        for node in inner_nodes:
            potential_child_count = randint(1, parentless_last_count)
            for _ in range(potential_child_count):
                possible_child = choice(last_layer)
                if possible_child.parent is None:
                    possible_child.parent = node
                    node.siblings.append(possible_child)
        to_delete = []
        for node in last_layer:
            if node.parent is None:
                to_delete.append(node)
        last_layer = to_delete
        for node in inner_nodes:
            if len(node.siblings) > 0:
                last_layer.append(node)
        all_possible_leaves.update(last_layer)
        i += 1

    candidates = list(filter(lambda x: not x.is_leaf, all_possible_leaves))
    while leaf_count < n:
        c = choice(candidates)
        c.siblings.append(Node(c, p10, p11, is_leaf=True, id=id_offset + 1))
        id_offset += 2
        leaf_count += 1

    for l in last_layer:
        if l.parent is None:
            l.parent = root
            root.siblings.append(l)

    return root


def generateRandomTreeWeighted(n, k, leaf_chance=0.5):
    all_possible_leaves = set()
    root = Node(None, random(), random(), id=-1)
    leaf_count = 0
    i = 1
    id_offset = 0
    last_layer = [Node(None, random(), random(), id=_ + id_offset) for _ in range(n)]
    id_offset += 2 * n
    all_possible_leaves.update(last_layer)
    while i < k and leaf_count != n:
        parentless_last_count = 0
        for l in last_layer:
            if l.parent is None:
                parentless_last_count += 1
        for x in last_layer:
            if not x.is_leaf and random() < leaf_chance and leaf_count < n:
                x.is_leaf = True
                leaf_count += 1
        inner_nodes = [Node(None, random(), random(), id=_ + id_offset) for _ in range(parentless_last_count)]
        id_offset += 2 * n
        for node in inner_nodes:
            potential_child_count = randint(1, parentless_last_count)
            for _ in range(potential_child_count):
                possible_child = choice(last_layer)
                if possible_child.parent is None:
                    possible_child.parent = node
                    node.siblings.append(possible_child)
        to_delete = []
        for node in last_layer:
            if node.parent is None:
                to_delete.append(node)
        last_layer = to_delete
        for node in inner_nodes:
            if len(node.siblings) > 0:
                last_layer.append(node)
        all_possible_leaves.update(last_layer)
        i += 1

    candidates = list(filter(lambda x: not x.is_leaf, all_possible_leaves))
    while leaf_count < n:
        c = choice(candidates)
        c.siblings.append(Node(c, random(), random(), is_leaf=True, id=id_offset + 1))
        id_offset += 2
        leaf_count += 1

    for l in last_layer:
        if l.parent is None:
            l.parent = root
            root.siblings.append(l)

    return root


def numerate_graph(root: Node, last_id=[0]):
    root.id = last_id[0]
    for sib in root.siblings:
        last_id[0] += 1
        numerate_graph(sib, last_id)


def generate_igraph(root: Node, graph=Graph()):
    for sib in root.siblings:
        color = "green" if sib.is_leaf else "red"
        graph.add_vertex(sib.id, color=color)
        graph.add_edge(root.id, sib.id)
        generate_igraph(sib, graph)

    return graph


def generateNTree(n):
    max_degree = 1
    vertices = 1
    root = Node(None, random(), random(), True)
    siblings_number = randint(1, min(n, max_degree))
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
                        return root
                sib.siblings.extend(layer1)
                root_candidates.append(sib)
        root_layer = root_candidates
    return root
