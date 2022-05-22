import numpy as np

from dag_tree import *
from apyori import apriori
from igraph import Graph, plot
import pickle
import matplotlib.pyplot as plt

TRANSACTION_LENGTH = 10
TRANSACTION_NUMBER = 500000
MAX_TEST_COUNT = 500
MIN_SUPPORT = 0.3
MIN_CONFIDENCE = 0.5
AVERAGE_LOSS_ITER = 100
TEST_STEP = MAX_TEST_COUNT // 50


def generateRules(dataset):
    apriori_result = apriori(dataset, min_support=MIN_SUPPORT, min_confidence=MIN_CONFIDENCE)
    association_rules_inner = []
    sets = set()
    for itemset in apriori_result:
        support = itemset[1]
        for association_rule in itemset[2]:
            if len(association_rule[0]) > 0 and len(association_rule[1]) > 0:
                items_base = tuple(association_rule[0])
                items_add = tuple(association_rule[1])
                confidence = association_rule[2]
                association_rules_inner.append((items_base, items_add, support, confidence))
                sets.add((items_base, items_add))
    return association_rules_inner, sets


def generate_transactions(model, count):
    transaction_dataset_inner = []
    for i in range(count):
        transaction = generateTransaction(model, [])
        item_transaction = []
        for i in range(len(transaction)):
            if transaction[i] == 1:
                item_transaction.append(i + 1)
        transaction_dataset_inner.append(item_transaction)
    return transaction_dataset_inner


if __name__ == '__main__':
    root = pickle.load(open('path_graph', 'rb'))
    #root = generateNTree(TRANSACTION_LENGTH)
    numerate_graph(root, [0])
    g = Graph()
    g.add_vertex(0, color='green')
    generate_igraph(root, g)
    pickle.dump(root, open("lastgraph", 'wb'))
    layout = g.layout_reingold_tilford(mode="in", root=0)
    p = plot(g, target="graph.png", layout=layout, vertex_label=g.vs['name'], vertex_color=g.vs['color'])
    print("Graph generated")
    print("root p10", root.p10)

    transaction_dataset = generate_transactions(root, TRANSACTION_NUMBER)

    true_association_rules, true_set = generateRules(transaction_dataset)

    for rule in true_association_rules:
        print(f'{rule[0]} => {rule[1]} with sup={rule[2]} conf={rule[3]}')

    print("True association rules count:", len(true_association_rules))

    x = [i for i in range(0, MAX_TEST_COUNT + 1, TEST_STEP)]
    y = []
    precision_l = []
    recall_l = []
    for tran_num in x:
        AVG_LOSS = []
        AVG_PRECISION = []
        AVG_RECALL = []
        for _ in range(AVERAGE_LOSS_ITER):
            test_dataset = generate_transactions(root, tran_num)
            association_rules, specific_set = generateRules(test_dataset)
            recall = len(specific_set.intersection(true_set)) / (len(true_set) + 0.00001)
            AVG_RECALL.append(recall)

            precision = len(specific_set.intersection(true_set)) / (len(specific_set) + 0.00001)

            AVG_PRECISION.append(precision)

            loss = len(specific_set.symmetric_difference(true_set))

            AVG_LOSS.append(loss)
        print(f'#{tran_num} completed...')
        AVG_LOSS = np.median(AVG_LOSS)
        AVG_PRECISION = np.median(AVG_PRECISION)
        AVG_RECALL = np.median(AVG_RECALL)
        y.append(AVG_LOSS)
        precision_l.append(AVG_PRECISION)
        recall_l.append(AVG_RECALL)

    print("Max precision:", max(precision_l))
    print("Max recall:", max(recall_l))
    fig = plt.plot(x, recall_l, label='linear', marker='o', color="green")
    plt.ylabel('Recall')
    plt.title('T/Recall')
    plt.show()
    plt.plot(x, precision_l, label='linear', marker='o', color="red")
    plt.title('T/Precision')
    plt.ylabel('Precision')
    plt.show()
    plt.plot(precision_l, recall_l, marker='o')
    plt.title('Precision/Recall')
    plt.ylabel('Recall')
    plt.show()


