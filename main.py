from dag_tree import *
from apyori import apriori
from igraph import Graph, plot
import pickle
import matplotlib.pyplot as plt

TRANSACTION_LENGTH = 5
TRANSACTION_NUMBER = 1000000
MAX_TEST_COUNT = 100
MIN_SUPPORT = 0.4
MIN_CONFIDENCE = 0.7
AVERAGE_LOSS_ITER = 100


def generateRules(dataset):
    apriori_result = apriori(dataset, min_support=MIN_SUPPORT, min_confidence=MIN_CONFIDENCE)
    association_rules = []
    sets = set()
    for itemset in apriori_result:
        support = itemset[1]
        for association_rule in itemset[2]:
            if len(association_rule[0]) > 0 and len(association_rule[1]) > 0:
                items_base = tuple(association_rule[0])
                items_add = tuple(association_rule[1])
                confidence = association_rule[2]
                association_rules.append((items_base, items_add, support, confidence))
                sets.add((items_base, items_add))
    return association_rules, sets


def generate_transactions(model, count):
    transaction_dataset = []
    for i in range(count):
        transaction = generateTransaction(model, [])
        item_transaction = []
        for i in range(len(transaction)):
            if transaction[i] == 1:
                item_transaction.append(i + 1)
        transaction_dataset.append(item_transaction)
    return transaction_dataset


if __name__ == '__main__':
    root = generateRandomTreeWeighted(TRANSACTION_LENGTH, 1000)
    #root = generatePath(TRANSACTION_LENGTH, p10=0.5, p11=0.8)
    #root = pickle.load(open('lastgraph', 'rb'))
    numerate_graph(root, [0])
    g = Graph()
    g.add_vertex(0)
    generate_igraph(root, g)

    layout = g.layout_reingold_tilford(mode="in", root=0)
    p = plot(g, target="graph.png", layout=layout, vertex_label=g.vs['name'], vertex_color=g.vs['color'])

    transaction_dataset = generate_transactions(root, TRANSACTION_NUMBER)

    true_association_rules, true_set = generateRules(transaction_dataset)

    for rule in true_association_rules:
        print(f'{rule[0]} => {rule[1]} with sup={rule[2]} conf={rule[3]}')

    print("True association rules count:", len(true_association_rules))

    x = [i for i in range(5, MAX_TEST_COUNT, 5)]
    y = []
    for tran_num in x:
        AVG_LOSS = 0
        for _ in range(AVERAGE_LOSS_ITER):
            test_dataset = generate_transactions(root, tran_num)
            association_rules, specific_set = generateRules(test_dataset)

            loss = len(specific_set.symmetric_difference(true_set)) / tran_num

            AVG_LOSS += loss

        AVG_LOSS /= AVERAGE_LOSS_ITER
        print("Average loss:", AVG_LOSS)
        y.append(AVG_LOSS)

    print("Min loss:", min(y))
    print("Max loss:", max(y))
    print("Average loss among all transactions:", sum(y) / len(y))

    plt.plot(x, y, label='linear')
    plt.show()

    pickle.dump(root, open("lastgraph", 'wb'))

