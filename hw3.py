import time
import re

class World(object):
	def __init__(self, nodes, q_lr, disc):
		self.nodes = nodes
		self.qnum = sum([1 if isinstance(v, Vortex) or isinstance(v, Round) or isinstance(v, Teleport) else 0 for v in self.nodes.values()])
		self.vnum = sum([1 if isinstance(v, Star) or isinstance(v, Teleport) else 0 for v in self.nodes.values()])
		self.disc = disc
		self.qlr = q_lr
		self.qtable = [ [0 if self.nodes[j].det_pass.get(i) else -1  for i in range(self.qnum)] for j in range(self.qnum)]

	def run_story(self, episodes):
		node = self.nodes[episodes[0]]
		for num in episodes[1:]:
			reward, new_node = node.makemove(num)
			if new_node is node:
				print("_\n")
				continue

			if isinstance(node, Teleport):
				print("Teleporting")
				break

			prev_val = self.qtable[node.num][new_node.num] if self.qtable[node.num][new_node.num]>0  else 0
			prev_a = (1-self.qlr) * prev_val
			self.qtable[node.num][new_node.num] = prev_a + self.qlr * ( reward + self.disc * max(self.qtable[new_node.num] + [0]))
			print(self.q_table())
			node = new_node

	def q_table(self):
		outstr = "-" * (self.qnum * 8) + "\n"
		outstr += "|" +"|".join( ["\t|".join(["{:.4}".format(float(i)) if i>=0 else "_" for i in self.qtable[i]]) + "\t|\n" for i in range(self.qnum)] ) 
		outstr += "-" * (self.qnum * 8) + "\n"
		return outstr

	def iter_one(self):
		r_val = {}
		workable = lambda x : isinstance(x, Star)
		print("Value Table")
		for i in self.nodes.values():
			if workable(i):
				r_val[i.num] = i.calc_value(self.disc)

		print("\nPolicy Table")
		for i in self.nodes.values():
			if workable(i):
				i.vscore = r_val[i.num]
				print(i.pols())
		print("--\n")

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

	def __str__(self):
		outstr = f"{self.__doc__} {self.num}: \n"
		if len(self.det_pass):
			outstr += ", \n".join([f"{k} : {v}" for k, v in self.det_pass.items()] ) + "\n"  
		elif len(self.actions):
			outstr += ", \n".join([f"{k} : {v}" for k, v in self.actions.items()] ) + "\n"  
		return outstr

	def pols(self):
		outstr = f"{self.num} " + ",".join([str(i) for i in self.best_pol])
		return outstr


class Round(Node):
	"Round Node"
	def __init__(self, **kwargs):
		Node.__init__(self, kwargs["nodenum"])

	def makemove(self, num):
		try:
			return self.det_pass[num]["reward"], self.det_pass[num]["ptr"]
		except:
			return 0, self

class Star(Node):
	"Star Node"
	def __init__(self, **kwargs):
		Node.__init__(self, kwargs["nodenum"])
		self.vtable = {} 
		self.best_pol = []
		self.vscore = 0
		self.a_score = {}

	def add_action_prob(self, **kwargs):
		a_no = kwargs["action_num"]
		n_no = kwargs["nodenum"]
		self.vtable[a_no] = 0

		self.actions[a_no][n_no] = {
			"r": kwargs["reward"],
			"prob" : kwargs["prob"],
			"ptr" : kwargs["ptr"]
		}

	def add_action(self, num):
		self.actions[num] = {}

	def calc_value(self, gamma, times=0):
		scores = {}
		green = "\033[1;32;40m{} : {:.5}\x1b[0m\t"
		white = "{} : {:.5}\t"
		
		for ac_no, node_ in self.actions.items():
			v_scores = {}
			for node_n, s_node in node_.items():
				val = s_node["prob"] * (s_node["r"] + gamma * s_node["ptr"].vscore)
				scores[node_n] = val
				v_scores[node_n] = val

			self.a_score[ac_no] = sum(v_scores.values())
		

		mx = max(v_scores.values())
		mx_a = max(self.a_score.values())
		self.best_pol = []
		
		for k, v in self.a_score.items():
			if v == mx_a:
				self.best_pol.extend(self.actions[k])

		print(self.num, ": |", " ".join([green.format(k, v) if v == mx_a else white.format(k, v) for k, v in sorted(self.a_score.items(), key=lambda x: x[0])]), "|")
		return max(self.a_score.values())
		
class Teleport(Star):
	"Teleport Node"
	def __init__(self, **kwargs):
		Star.__init__(self, **kwargs)
		self.vtable = {} 
		self.best_pol = []
		self.vscore = 0

	
class Vortex(Node):
	"Vortex Node"
	def __init__(self, **kwargs):
		Node.__init__(self, kwargs["nodenum"])

class Goal(Node):
	"Goal Node"
	def __init__(self, **kwargs):
		Node.__init__(self, kwargs["nodenum"])
		self.vscore = 0

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

def pos_act_parser(nodes, raw_act_trs):
	for n_id, ac_id in raw_act_trs:
		for i in ac_id:
			nodes[n_id].add_action(i)

def undet_act_parser(nodes, raw_act_table):
	for a_no, node_ in raw_act_table.items():
		for node_num, pos_nodes in node_.items():
			for k, prob in pos_nodes.items():
				if k == "r":
					continue
				nodes[node_num].add_action_prob(action_num=a_no, nodenum=k, prob=prob, reward=pos_nodes["r"], ptr=nodes[k])

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
	nodep = lambda x: (x[0], x[1], x[2])
	actiondivider = lambda x: (x[0], x[1:])

	wd["nodenames"] = list(inpfunc().strip())
	wd["alpha"], wd["gamma"] = [float(i) for i in inpfunc().strip().split()]

	wd["total_transition"] = int(inpfunc().strip())
	wd["transitions"] = [ nodep([int(i) for i in inpfunc().strip().split()]) for _ in range(wd["total_transition"]) ]

	wd["total_actions"] = int(inpfunc().strip())
	wd["actions"] = [  actiondivider([int(x) for x in inpfunc().strip().split()]) for _ in range(wd["total_actions"]) ]
	wd["action_table"] = action_parser(inpfunc)

	return wd

def do():
	filename = "input.inp"

	global file_o, ctr
	file_o = open(filename).readlines()
	ctr = 0
	wd = parseinput(fake_inp)
	nodes = nodemaker(wd["nodenames"])
	det_edge_parser(nodes, wd["transitions"])
	pos_act_parser(nodes, wd["actions"])
	undet_act_parser(nodes, wd["action_table"])
	dict_printer(nodes)
	world = World(nodes, wd["alpha"], wd["gamma"])

	while True:
		try:
			inp = input()
			if inp == "$":
				break
		except EOFError:
			break
		ep_list = [int(i) for i in inp.split()]
		world.run_story(ep_list)

	while True:
		try:
			inp = input()
		except EOFError:
			break
		if inp == "$":
			break
		if inp == "c":
			world.iter_one()


if __name__ == "__main__":
	# st = time.time()
	do()
	# print(time.time() - st)