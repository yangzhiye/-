#!/usr/bin/env python
# coding:utf8

import random
from collections import defaultdict
from BayesNetwork import BayesNetwork

# 根据某个随机变量的分布进行采样
def sample(dist):
	rand = random.random()
	sd = 0
	for val in sorted(dist):
		if sd <= rand < sd + dist[val]:
			return val
		sd += dist[val]

# 直接采样
def direct_sample(bn):
	vl = bn.get_topo_order()
	event = {}
	for rv in vl:
		parents = bn.query_parents(rv)
		condition = {k:event[k] for k in parents}
		cond_dist = bn.query_cond_dist(rv, condition)
		event[rv] = sample(cond_dist)
	return event

# 判断事件event与证据evidence是否一致
def is_consistent(event, evidence):
	return all(event[rv] == evidence[rv] for rv in evidence)

# 规范化处理
def normalize(C):
	s = float(sum(C.values()))
	return {k:C[k]/s for k in C}
	
# 拒绝采样
def rejection_sample(variable, evidence, bn, N):
	C = defaultdict(int)
	for i in xrange(N):
		event = direct_sample(bn)
		if is_consistent(event, evidence):
			val = event[variable]
			C[val] += 1
	return normalize(C)

# 加权采样,返回一个样本及其对应的权值
def weighted_sample(bn, evidence):
	vl = bn.get_topo_order()
	event = {}
	w = 1.0

	for rv in vl:
		parents = bn.query_parents(rv)
		condition = {k:event[k] for k in parents}
		cond_dist = bn.query_cond_dist(rv, condition)
		if evidence.has_key(rv):
			val = evidence[rv]
			event[rv] = val
			w *= cond_dist[val]
		else:
			event[rv] = sample(cond_dist)

	return event, w

# 使用似然加权方法计算分布
def likelihood_weighting(variable, evidence, bn, N):
	W = defaultdict(float)

	for i in xrange(N):
		event, w = weighted_sample(bn, evidence)
		val = event[variable]
		W[val] += w
	return normalize(W)

def gibbs_sample(variable, evidence, bn, N):
	C = defaultdict(int)
	
	# 初始化
	event = direct_sample(bn)
	Z = []                      # 非证据变量
	for rv in event:
		if rv in evidence:
			event[rv] = evidence[rv]
		else:
			Z.append(rv)
	# 迭代
	for i in range(N):
		for z in Z:
			cond_dist = bn.query_whole_cond_dist(z, event)
			event[z] = sample(cond_dist)
			val = event[variable]
			C[val] += 1

	return normalize(C)
		
if __name__ == '__main__':
	bn = BayesNetwork()
	bn.load_from_file('wet_glass.txt')
	# 直接采样示例
	print 'Direct sample'
	for i in range(5):
		print direct_sample(bn)

	# 拒绝采样示例
	print 'Rejection sample'
	print rejection_sample('Rain', {'Sprinkler':'True'}, bn, 1000)

	# 加权采样示例
	print 'weighted sample'
	print likelihood_weighting('Rain', {'Sprinkler':'True'}, bn, 1000)

	# 吉布斯采样示例
	print 'gibbs sample'
	print gibbs_sample('Rain', {'Sprinkler':'True'}, bn, 1000)
