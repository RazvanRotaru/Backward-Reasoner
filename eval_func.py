from Lab05 import *

def eval_function(func):
	name = get_head(func)
	if name == 'get':
		return make_const(get(*get_args(func)))
	if name == 'compute_triangle':
		return make_const(compute_triangle(*get_args(func)))
	if name == 'getShortest':
		return make_const(getShortest(*get_args(func)))
	if name == 'getMiddle':
		return make_const(getMiddle(*get_args(func)))
	if name == 'getLongest':
		return make_const(getLongest(*get_args(func)))
	if name == 'compute_pitagoras':
		return make_const(compute_pitagoras(*get_args(func)))

def get(T, L):
	triangle = get_value(T)
	l = get_value(L)
	if l == '0':
		return str(triangle[0]) + str(triangle[1])
	if l == '1':
		return str(triangle[1]) + str(triangle[2])
	else:
		return str(triangle[0]) + str(triangle[2])

def compute_triangle(LA, LB, LC):
	a = int(get_value(LA))
	b = int(get_value(LB))
	c = int(get_value(LC))



	ls = [a, b, c]
	m = max(ls)
	ls.remove(m)

	return str(sum(ls) - m)

def getShortest(LA, LB, LC):
	a = int(get_value(LA))
	b = int(get_value(LB))
	c = int(get_value(LC))

	ls = [a, b, c]
	
	return str(min(ls))

def getLongest(LA, LB, LC):
	a = int(get_value(LA))
	b = int(get_value(LB))
	c = int(get_value(LC))

	ls = [a, b, c]
	
	return max(ls)

def getMiddle(LA, LB, LC):
	a = int(get_value(LA))
	b = int(get_value(LB))
	c = int(get_value(LC))

	ls = [a, b, c]
	m = max(ls)
	ls.remove(m)
	m = min(ls)
	ls.remove(m)

	return str(ls[0])

def compute_pitagoras(LS, LM, LL):
	a = int(get_value(LS))
	b = int(get_value(LM))
	c = int(get_value(LL))

	res = a*a + b*b - c*c

	return str(res)
	