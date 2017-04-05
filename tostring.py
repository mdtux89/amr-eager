import copy
from collections import defaultdict

def _to_string(triples, root, level, last_child, seen, prefix, indexes, nodes):
    if len(root.split("/")) == 2:
        conc = root.split("/")[1].strip()
    else:
        conc = root.split()[0]
    children = [t for t in triples if str(t[0]) == root.split()[0]]
    if root in seen:
        root = root.split()[0]
        children = []
    else:
        var = root
        if " / " in root:
            var = root.split()[0]
        nodes.append((var,conc))
        indexes[var].append(prefix)
    if " / " in root:
        seen.append(root)
        graph = "(" + root
        if len(children) > 0:
            graph += "\n"
        else:
            graph += ")"
    else:
        graph = root
    j = 0
    for k, t in enumerate(children):
        if str(t[0]) == root.split()[0]:
            next_r = t[3]
            if t[4] != "":
                next_r += " / " + t[4]
            for i in range(0, level):
                graph += "    "
            seen2 = copy.deepcopy(seen)
            graph += t[2] + " " + _to_string(triples, next_r, level + 1, k == len(children) - 1, seen, prefix + "." + str(j), indexes, nodes)[0]
            if next_r not in seen2 or " / " not in next_r:
                j += 1
    if len(children) > 0:
        graph += ")"
    if not last_child:
        graph += "\n"

    return graph, indexes, nodes

def to_string(triples, root):
    children = [t for t in triples if str(t[0]) == root]
    assert(len(children)==1)
    if children[0][4] == "":
        return "(e / emptygraph)", defaultdict(list), []
    return _to_string(triples, children[0][3] + " / " + children[0][4], 1, False, [], "0", defaultdict(list), [])

