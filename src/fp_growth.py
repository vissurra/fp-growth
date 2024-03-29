from itertools import combinations


class FpGrowth:
    """
    fp-growth algorithm
    """

    def __init__(self, min_support=3):
        """
        init
        :param min_support: the min support used to filter
        """
        self.min_support = min_support
        self.item_header_table = ItemHeaderTable()
        self.tree = Tree()
        self.conditional_pattern_bases = {}

    def build(self, item_sets):
        """
        build item header table and fp tree
        :param item_sets: the item set list
        """
        # remove the repeats
        item_sets = [list(set(item for item in item_set)) for item_set in item_sets]

        self._build_item_header_table(item_sets=item_sets)
        self.item_header_table.show()

        item_sets = [self.item_header_table.filter_and_sort_item_set(item_set) for item_set in item_sets]

        self._build_tree(item_sets=item_sets)
        self.tree.show()

        self._build_conditional_pattern_bases()

    def find_frequency_item_sets(self, min_item_count=2):
        """
        find all frequent item sets
        :param min_item_count: min item count of item set
        :return: frequent item set list
        """
        result = []
        for item, conditional_pattern_base in self.conditional_pattern_bases.items():
            frequent_item_sets = FpGrowth._find_frequent_item_sets(item, conditional_pattern_base, min_item_count)
            result += frequent_item_sets
        return result

    def _build_item_header_table(self, item_sets):
        """
        build item header table
        :param item_sets: the item set list
        """

        # traverse to count the frequency of item
        raw_items = {}
        for item_set in item_sets:
            for item in item_set:
                raw_items[item] = (raw_items[item] + 1) if item in raw_items else 1

        # filter low frequency item
        items = [key for key in raw_items.keys()]
        for item in items:
            if raw_items[item] < self.min_support:
                raw_items.pop(item)

        # sort from largest to smallest
        sorted_items = sorted(raw_items.items(), key=lambda kv: kv[1], reverse=True)

        # add item to item head table
        for key, value in sorted_items:
            self.item_header_table.add(item=key, frequency=value)

    def _build_tree(self, item_sets):
        """
        build fp-tree
        :param item_sets: item set list
        """
        for item_set in item_sets:
            new_nodes = Tree.add_item_set(root=self.tree.root, item_set=item_set)
            for new_node in new_nodes:
                self.item_header_table.add_item_header_pointer(new_node)

    def _build_conditional_pattern_bases(self):
        """
        set conditional pattern base, key is item, value is conditional pattern base stored in list
        """
        for item_header in reversed(self.item_header_table.get_table()):
            base = {}
            for pointer in item_header.pointers:
                head = pointer
                tail = head.parent
                while tail.item is not None:
                    item = tail.item
                    base[item] = (base[item] + head.frequency) if item in base else head.frequency
                    tail = tail.parent
            # filter low frequency candidates
            items = [key for key in base.keys()]
            for item in items:
                if base[item] < self.min_support:
                    base.pop(item)
            if len(base) > 0:
                self.conditional_pattern_bases[item_header.item] = list(base.keys())

    @staticmethod
    def _find_frequent_item_sets(item, base, min_item_count):
        """
        find frequent item sets
        :param item: item
        :param base: conditional pattern base
        :param min_item_count: the min item count of frequent item set
        :return: frequent item set list
        """
        all_frequent_item_sets = []
        # i is the count of items which to be combined with item
        for i in range(1, len(base) + 1):
            item_sets = [item_set for item_set in combinations(base, i) if len(item_set) >= min_item_count - 1]
            for item_set in item_sets:
                all_frequent_item_sets.append([item] + list(item_set))
        return all_frequent_item_sets


class ItemHeaderTable:
    """
    the item header table, stored in a dict for the convenience of querying
    """

    def __init__(self):
        """
        init, set table as a dict
        """
        self._table = {}

    def show(self):
        print('-' * 20, 'item header table begin', '-' * 20)
        for _, value in self._table.items():
            print(value)
        print('-' * 20, 'item header table end', '-' * 20)

    def get_table(self):
        """
        return table as a list
        :return: table list
        """
        return [value for _, value in self._table.items()]

    def add(self, item, frequency):
        """
        add item header
        :param item: item name
        :param frequency: the count of items in item sets
        """
        self._table[item] = ItemHeader(item=item, frequency=frequency)

    def add_item_header_pointer(self, pointer):
        """
        add a node to item header, raise ValueError if item not in table
        :param pointer: the node of fp-tree
        """
        if pointer.item not in self._table:
            raise ValueError('item header table can not find the item: {}'.format(pointer))
        self._table[pointer.item].add_pointer(pointer)

    def get(self, item):
        """
        get a item header by item
        :param item: item
        :return: item header
        """
        return self._table[item]

    def contain(self, item):
        """
        item exist or not
        :param item: item
        :return: exist or not
        """
        return item in self._table

    def filter_and_sort_item_set(self, item_set):
        """
        filter low frequency item, and sort item set by item frequency
        :param item_set: item set
        :return: new item set
        """
        item_set = [item for item in item_set if self.contain(item)]
        item_set = sorted(item_set, key=lambda item: self._table[item].frequency, reverse=True)
        return item_set


class ItemHeader:
    """
    item header
    """

    def __init__(self, item, frequency):
        """
        init, use set to store the pointers
        :param item: item
        :param frequency: the count of items in item sets
        """
        self.item = item
        self.frequency = frequency
        self.pointers = set()

    def add_pointer(self, pointer):
        """
        add a node
        :param pointer: node of fp-tree
        """
        self.pointers.add(pointer)

    def __str__(self):
        return 'ItemHeader[{}, {}]'.format(self.item, self.frequency)


class Tree:
    """
    fp-tree
    """

    def __init__(self):
        self.root = Node()

    def show(self):
        print('-' * 20, 'fp tree begin', '-' * 20)
        self.root.show()
        print('-' * 20, 'fp tree end', '-' * 20)

    @staticmethod
    def add_item_set(root, item_set):
        """
        add one item set to fp-tree by recursion, yield all new nodes
        :param root: root node
        :param item_set: item set need to be added to the root node
        """
        item = item_set[0]
        for child in root.children:
            if item == child.item:
                # item exists, item frequency plus 1
                child.frequency += 1
                next_root = child
                break
        else:
            # item not exist, create a node
            node = Node(item=item, frequency=1, parent=root)
            root.children.append(node)
            next_root = node
            yield node

        if len(item_set) > 1:
            # set the next item in item set
            new_nodes = Tree.add_item_set(root=next_root, item_set=item_set[1:])
            for node in new_nodes:
                yield node


class Node:
    """
    fp-tree node
    """

    def __init__(self, item=None, frequency=0, parent=None):
        """
        init
        :param item: item
        :param frequency: the count of node been achieved
        :param parent: parent node
        """
        self.item = item
        self.frequency = frequency
        self.parent = parent
        self.children = []

    def show(self, indent=0):
        print('{}[{}, {}]'.format('  ' * indent, self.item, self.frequency))
        for child in self.children:
            child.show(indent=indent + 1)

    def __str__(self):
        return 'Node[{}, {}]'.format(self.item, self.frequency)
