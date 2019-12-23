class FlowLogGraph:

    def __init__(self, name):
        self.lines = ""
        self.flow_log = []
        FlowLogGraph.openfile(self, name)
        FlowLogGraph.sorting_pairs(self)
        FlowLogGraph.graph_drawing(self, name)

    def openfile(self, name):
        text_file = open(name, "r")
        self.lines = text_file.readlines()
        text_file.close()

    def sorting_pairs(self):
        flow_log = []
        for line in self.lines:
            split_line = line.split()
            if split_line[12] == "ACCEPT":
                temporary = [split_line[3], split_line[4], ""]
                if flow_log.count(temporary) == 0:
                    flow_log.append(temporary)
        for line in flow_log:
            new = [line[1], line[0], ""]
            for row in flow_log:
                if row == new:
                    line[2] = "both"
                    flow_log.pop(flow_log.index(new))
        self.flow_log = flow_log

    def graph_drawing(self, name):
        from graphviz import Digraph
        new_name = name[0:len(name)-4]
        g = Digraph(new_name)
        for line in self.flow_log:
            g.edge(line[0], line[1], dir=line[2])
        g.view()
