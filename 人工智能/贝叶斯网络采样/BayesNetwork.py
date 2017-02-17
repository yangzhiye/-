#!/usr/bin/env python
# coding:utf8

from collections import defaultdict
import copy

# 规范化处理
def normalize(C):
	s = float(sum(C.values()))
	return {k:C[k]/s for k in C}

class BayesNetwork:
	def __init__(self):
		self.variable_matrix = []

	def read_vn_from_file(self, fp):
		line = fp.readline()
		return line.split()

	def read_am_from_file(self, fp, n):
		adj_matrix = []
		for i in range(n):
			line = fp.readline()
			row = map(int, line.strip().split())
			adj_matrix.append(row)

		return adj_matrix

	def parse_cpt(self, line):
		line = ''.join(line.split())
		parts = line.split('|')
		condition = {}
		if len(parts) > 1:
			# 解析条件
			for item in parts[0].split(','):
				rv, val = item.split('=')
				condition[rv] = val
		# 解析随机变量及其分布
		variable, dist_str = parts[-1].split('=')
		dist = defaultdict(float)
		for item in dist_str[1:-1].split(','):
			val, prob = item.split(':')
			dist[val] = float(prob)
		
		return condition, variable, dist
		
	def read_cpt_from_file(self, fp):
		cpt = defaultdict(dict)
		while True:
			line = fp.readline()
			line = line.strip()
			if not line:
				break
			condition, variable, dist = self.parse_cpt(line)
			cond_tuple = tuple([(rv, condition[rv])
								for rv in sorted(condition.keys())])
			cpt[variable][cond_tuple] = dist

		return cpt

	# 从配置文件中读取BN
	def load_from_file(self, fname):
		fp = open(fname, 'r')
		while True:
			line = fp.readline()
			if not line:
				break
			if not line.strip():
				continue
			seg = line.strip()[:-1]
			if seg == 'Variable Name':
				self.variable_list = self.read_vn_from_file(fp)
			elif seg == 'Adjacendy Matrix':
				self.adj_matrix = self.read_am_from_file(fp, len(self.variable_list))
			elif seg == 'CPT':
				self.CPT = self.read_cpt_from_file(fp)

	# 查询指定随机变量的条件概率分布
	def query_cond_dist(self, variable, condition):
		cond_tuple = tuple([(rv, condition[rv])
							for rv in sorted(condition.keys())])
		return copy.copy(self.CPT[variable][cond_tuple])

	# 获取网络中所有随机变量的一个拓扑序列
	def get_topo_order(self):
		topo_order = []
		n = len(self.variable_list)
		am = copy.deepcopy(self.adj_matrix)
		for k in range(n):
			# 寻找起始节点
			for i in range(n):
				if i in topo_order or any(am[j][i] for j in range(n)):
					continue
				else:
					break
			topo_order.append(i)
			# 更新邻接矩阵
			for i in range(n):
				for j in range(n):
					am[i][j] = 0
					am[j][i] = 0
		return [self.variable_list[i] for i in topo_order]
	
	# 查询指定随机变量的父结点列表
	def query_parents(self, variable):
		n = len(self.variable_list)
		try:
			idx = self.variable_list.index(variable)
		except ValueError:
			return []
		return [self.variable_list[j] for j in range(n)
				if self.adj_matrix[j][idx]]

	# 查询指定随机变量子结点列表
	def query_children(self, variable):
		n = len(self.variable_list)
		try:
			idx = self.variable_list.index(variable)
		except ValueError:
			return []
		return [self.variable_list[j] for j in range(n)
				if self.adj_matrix[idx][j]]

	# 给定其它所有随机变量的取值,计算指定随机变量的分布
	def query_whole_cond_dist(self, variable, evidence):
		parents = self.query_parents(variable)
		condition = {k:evidence[k] for k in parents}
		cond_dist = self.query_cond_dist(variable, condition)
		
		children = self.query_children(variable)
		for val in cond_dist:
			for c in children:
				parents = self.query_parents(c)                
				condition = {k:evidence[k] for k in parents}
				condition[variable] = val
				c_cond_dist = self.query_cond_dist(c, condition)
				cond_dist[val] *= c_cond_dist[evidence[c]]

		return normalize(cond_dist)
		
if __name__ == '__main__':
	BN = BayesNetwork()
	BN.load_from_file('wet_glass.txt')
	print BN.get_topo_order()
	print BN.adj_matrix 
	print BN.query_parents('Rain')
	print BN.query_cond_dist('Cloudy', {})