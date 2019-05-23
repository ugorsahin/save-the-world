import time
import re

class Node(object):

	def __init__(self, nodenum):
		self.num = nodenum
		self.det_pass = {}
		self.actions = {}

	def add_det_pass(self, nodeptr, reward):
		self.det_pass[nodeptr.num] = {
			"ptr" : nodeptr,
			"reward" : reward
		}

	def add_action(self, num):
		self.actions[num] = 0
	
	def __str__(self):
		outstr = f"Regular Node {self.num}: "
		outstr += ", ".join([f"{k}, {v}" for k, v in self.det_pass.items()] ) + " "  
		outstr += " - ".join([f"{k}" for k in self.actions] )  + "\n"
		return outstr

class Round(Node):
	def __init__(self, **kwargs):
		Node.__init__(self, kwargs["nodenum"])

class Star(Node):
	def __init__(self, **kwargs):
		Node.__init__(self, kwargs["nodenum"])

class Teleport(Node):
	def __init__(self, **kwargs):
		Node.__init__(self, kwargs["nodenum"])

class Vortex(Node):
	def __init__(self, **kwargs):
		Node.__init__(self, kwargs["nodenum"])

class Goal(Node):
	def __init__(self, **kwargs):
		Node.__init__(self, kwargs["nodenum"])

def nodemaker(raw_nodes):
	d_types = {
		"R" : Round,
		"V" : Vortex,
		"O" : Teleport,
		"S" : Star,
		"G" : Goal,
	}

	nodeworld = {}

	for idx, i in enumerate(raw_nodes):
		nodeworld[idx] = d_types[i](nodenum=idx)

	return nodeworld

def det_edge_parser(nodes, raw_edges):
	for f_node, e_node, reward in raw_edges:
		nodes[f_node].add_det_pass(nodes[e_node], reward)

def pos_act_parser(nodes, raw_act_table):
	for n_id, ac_id in raw_act_table:
		for i in ac_id:
			nodes[n_id].add_action(i)

def action_parser(inpfunc):
	long_ = []	
	divide = lambda x: (int(x[0]), float(x[1]) / 100)  
	na = {}
	while True:
		inp_0 = inpfunc()
		if inp_0 == "E":
			break

		id_ = int(inp_0.replace("action : ", "").strip())
		na[id_] = {}

		while True:
			inp_1 = inpfunc().strip()
			if inp_1 == "#":
				break
			inp_1 = int(inp_1)
			na[id_][inp_1] = {"r" : float(inpfunc())}
			while True:
				inp_3 = inpfunc().strip()
				if inp_3 == "$":
					break
				node_no, prob = divide([i for i in inp_3.split()])
				na[id_][inp_1][node_no] = prob

	return na
			
def fake_inp():
	global file_o
	global ctr
	outp = file_o[ctr]
	ctr += 1
	return outp

def dict_printer(dicti, l=0):
	for k, v in dicti.items():
		print(" "*l, k, ":", end="")
		if type(v) == dict:
			print()
			dict_printer(v, l+1)
		else:
			print(" "*l, v)

def parseinput(inpfunc):
	wd = {}
	nodep = lambda x: (int(x[0]), x[1], x[2])
	actiondivider = lambda x: (x[0], x[1:])

	wd["nodenames"] = list(inpfunc().strip())
	wd["alpha"], wd["gamma"] = [float(i) for i in inpfunc().strip().split()]

	wd["total_transition"] = int(inpfunc().strip())
	wd["transitions"] = [ nodep([float(i) for i in inpfunc().strip().split()]) for _ in range(wd["total_transition"]) ]

	wd["total_actions"] = int(inpfunc().strip())
	wd["actions"] = [  actiondivider([int(x) for x in inpfunc().strip().split()]) for _ in range(wd["total_actions"]) ]
	wd["action_table"] = action_parser(inpfunc)

	# for k, v in wd.items():
	# 	print(k, v)

	return wd

if __name__ == "__main__":
	filename = "input.inp"

	file_o = open(filename).readlines()
	ctr = 0
	wd = parseinput(fake_inp)
	# dict_printer(wd)
	nodes = nodemaker(wd["nodenames"])
	det_edge_parser(nodes, wd["transitions"])
	pos_act_parser(nodes, wd["actions"])
	dict_printer(nodes)
