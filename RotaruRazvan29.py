from Lab05 import *
from Lab07fct import *
from Lab07 import *
from eval_func import *
import sys

def concat_lists_of_dict(l1, l2):
    ans = []
    new_el = {}
    for e1 in l1:
        for e2 in l2:
            cont = False
            new_el = deepcopy(e1)
            for key in e2:
                if key in e1:
                    if not e1[key].__eq__(e2[key]):
                        cont = True
                new_el[key] = e2[key]
            if cont == False:
                ans.append(new_el)
    return ans

def get_partial_substitution(subst, theorem):
    partial_subst = {}
    for var in filter(is_variable, get_args(theorem)):
        if get_name(var) in subst:
            partial_subst[get_name(var)] = subst[get_name(var)]
    for fct in filter(is_function_call, get_args(theorem)):
        for var in get_args(fct):
            if get_name(var) in subst:
                partial_subst[get_name(var)] = subst[get_name(var)]
    return partial_subst


def add_coef(kb, coef, conclusion, *hypotheses):
    s = conclusion if not hypotheses else make_or(*([make_neg(s) for s in hypotheses] + [conclusion]))
    # if check_sentence(s):
    kb.append([s, coef])
    return

def get_coef(kb, theorem):
    for elm in kb:
        if theorem == elm[0]:
            return elm[1]
    return None

def print_substitution(subst, indent = 0, verbose = True):
    if not verbose:
        return
    ret = '\t' * indent
    ret += '{'
    for key in subst:
        if isinstance(subst[key], Constant):
            ret += str(key) + ' -> ' + str(get_value(subst[key]))
        else:
            ret += str(key) + ' -> ' + str(get_name(subst[key]))
        ret += ', '
    ret = ret[:-2]
    ret += '}'
    print(ret)
    return

def print_indent(string, indent = 0, verbose = True):
    if not verbose:
        return

    ret = '\t' * indent
    ret += string

    print(ret)
    return

def add_cond(condition):
    if condition == '':
        return
    if condition[0] == '?':
        return make_var(condition[1:])
    else:
        return make_const(condition)

def get_variables(atom):
    vrs = []
    if has_args(atom):
        for arg in get_args(atom):
            if is_constant(arg):
                continue
            if is_variable(arg):
                vrs.append(get_name(arg))
            if is_sentence(arg):
                aux_vrs = get_variables(arg)
                for elm in aux_vrs:
                    vrs.append(elm)
    return vrs

def has_variables(atom):
    if get_variables(atom) == []:
        return False
    return True

def can_evaluate(function):
    for arg in get_args(function):
        if not is_constant(arg):
            return False
    return True

def create_atom(atom_str):
    atom_name = atom_str[:atom_str.find('(')]
  
    cond_str = atom_str[atom_str.find('(') + 1: atom_str.find(')')]
    aux_cond = [x.strip() for x in cond_str.split(',')]
    
    if cond_str == '':
        aux_cond = []
    atom_conditions = []
    for condition in aux_cond:
        atom_conditions.append(add_cond(condition))

    return make_atom(atom_name, *atom_conditions)


def create_function(func_str):
    dp = func_str.find('(')
    name = func_str[:dp]
    func_str = func_str[dp+1:]
    terms = create_terms(func_str)[0]
    func = make_function_call(name, *terms)
    return func

def create_terms(terms_str):
    will_break = False
    ret = []
    while not will_break:
        dp = terms_str.find('(')
        ip = terms_str.find(')')
        if dp >= 0 and dp < ip:
            ret.append(create_function(terms_str[:ip+1]))
            terms_str = terms_str[ip+1:]
            continue
        vp = terms_str.find(',')
        if vp < 0:
            will_break = True
            np = ip
        elif ip >= 0 and ip >= vp:
            np = vp
        else:
            will_break = True
            np = ip 
        curr_term = terms_str[:np]
        terms_str = terms_str[np + 1:]
        if not curr_term:
            continue
        ret.append(add_cond(curr_term))
    return [ret, terms_str]

def create_condition(atom_str):
    cond = []
    while atom_str:
        if atom_str[0] == ',':
            atom_str = atom_str[1:]
        fd = atom_str.find('(')
        name = atom_str[:fd].strip(' ')
        atom_str = atom_str[fd+1:]
        [terms, atom_str] = create_terms(atom_str)
        # terms = ret[0]
        # atom_str = ret[1]
        cond.append(make_atom(name, *terms))
    return cond

def unify_substitution(subst):
    to_del = []
    for key in subst:
        if is_variable(subst[key]):
            name = get_name(subst[key])
            if name in subst:
                subst[key] = subst[name]
                to_del.append(name)
    for name in to_del:
        del subst[name]
    return subst

def contains(list1, subst):
    for elm in list1:
        same = True
        for key in elm:
            if key in subst:
                if not elm[key].__eq__(subst[key]):
                    same = False
        if same:
            return True
    return False

def unique_substitutions(list1): 
    unique_list = [] 
    
    for elm in list1:
        if contains(unique_list, elm):
            continue
        unique_list.append(elm)

    return unique_list

def unique(list1): 
  
    # intilize a null list 
    unique_list = [] 
      
    # traverse for all elements 
    for x in list1: 
        # check if exists in unique_list or not 
        if x not in unique_list: 
            unique_list.append(x) 
    return unique_list

def recursive_bc(kb, goal, substitutions, indent = 0, verbose = False, val = 0):
    resolved = [[False]] * len(substitutions)
    ans = []
    no_ans = True
    ret = 0

    print_indent('Solving', indent, verbose)
    print_formula(goal[0], False, indent, verbose)
    # for s in substitutions:
        # print_substitution(s, indent, verbose)
    func_found = False
    goal_args = get_args(goal[0])
    for i in range(len(goal_args)):
        if is_function_call(goal_args[i]):
            if not can_evaluate(goal_args[i]):
                continue
            func_found = True
            goal_args[i] = eval_function(goal_args[i])

    if func_found:
        replace_args(goal[0], goal_args)
        print_indent('After evalating the function the goal becomes:', indent, verbose)
        print_formula(goal[0], False, indent, verbose)
    

    for subst_index in range(len(substitutions)):
        subst = substitutions[subst_index] 

        sub_goal = deepcopy(goal[0])

        partial_subst = {}

        # for var in filter(is_variable, get_args(sub_goal)):
        #     if get_name(var) in subst:
        #         partial_subst[get_name(var)] = subst[get_name(var)]

        partial_subst = get_partial_substitution(subst, sub_goal)
        if partial_subst:
            print_indent('', indent, verbose)
            print_indent('<><><><><><><><><><><><><><><><>', indent, verbose)
            print_indent('Applying substitution ' + str(subst_index + 1) + ' of ' + str(len(substitutions)), indent, verbose)
            print_substitution(partial_subst, indent, verbose)
            print_indent('V V V V V V V V V V V', indent, verbose)
            sub_goal = substitute(sub_goal, partial_subst)
            func_found = False
            goal_args = get_args(sub_goal)
            for i in range(len(goal_args)):
                if is_function_call(goal_args[i]):
                    if not can_evaluate(goal_args[i]):
                        continue
                    func_found = True
                    goal_args[i] = eval_function(goal_args[i])

            if func_found:
                print_indent('After evalating the function the subgoal becomes:', indent, verbose)
                replace_args(sub_goal, goal_args)
            print_formula(sub_goal, False, indent, verbose)

        aux_subst = []
        modified = False

        print_indent('', indent, verbose)
        print_indent('Checking for facts that unifies the goal', indent, verbose)
        for fact in filter(is_fact, kb):
            # f = deepcopy(partial_subst)
            res = unify(sub_goal, fact)
         
            if res != False:
                if not modified:
                    print_indent('Found facts:', indent, verbose)
                print_formula(fact, False, indent, verbose)
                
                if use_coef:
                    aux_coef = get_coef(coefs, fact)
                    print_indent('with coefficient: ' + str(aux_coef), indent, verbose)
                    return aux_coef
                
                if res != True:
                    res = unify_substitution(res)
                    aux_subst.append(res)
                    modified = True
                    continue

                return True
         
        if modified:
            no_ans = False
         
            aux_ans = concat_lists_of_dict([subst], aux_subst)
            for a in aux_ans:
                if a not in ans:
                    ans.append(a)
         
        else:
            print_indent('No fact found', indent, verbose)

        # # ca sa mearga L3 si L4
        if (not modified) or has_variables(sub_goal):
        # if True:
            substitutions_bckp = deepcopy(substitutions)

            print_indent('', indent, verbose)
            print_indent('Checking for rules that unifies the goal', indent, verbose)

            visited = []
            found_rule = False
            for rule in filter(is_rule, kb):
                substitutions = substitutions_bckp

                new_args = {}
                
                if has_args(sub_goal) and has_args(rule):
                    rule_vars = get_variables(rule)
                    goal_vars = get_variables(sub_goal)

                    for elm in rule_vars:
                        if elm in goal_vars:
                            new_name = str(elm) + '_dup42'
                            new_args[elm] = make_var(new_name)
         
                    rule = substitute(rule, new_args)
                aux_subst = unify(get_conclusion(rule), sub_goal, subst)
                if aux_subst == False:
                    continue
                
                if rule in visited:
                    continue

                visited.append(rule)
                
                found_rule = True
                subst = aux_subst
         
                print_indent('Found rule:', indent, verbose)
                print_indent('-------------------------------------------', indent, verbose)
                print_formula(rule, False, indent, verbose)
                print_indent('-------------------------------------------', indent, verbose)

                if use_coef:
                    val = get_coef(coefs, rule)
                    l = [val] * len(get_premises(rule))
                    print_indent('with coefficient: ' + str(val), indent, verbose)
                    print_indent('', indent, verbose)

                if subst:
                    print_indent('Applying substitution:', indent, verbose)
                    print_substitution(subst, indent, verbose)
         
                new_goal = get_premises(rule)
                resolved[subst_index] = [False] * len(new_goal)

                aux_substitutions = [{}]
                modified = False
                
                for i in range(len(new_goal)):
                    prem = new_goal[i]
                    prem = substitute(prem, subst)
         
                    print_indent('Trying to prove premise ' + str(i + 1) + ' of ' + str(len(new_goal)), indent, verbose)
                    print_formula(prem, False, indent, verbose)
         
                    if is_sentence(prem):
                        prem = get_args(prem)[0]

                    if use_coef:
                        bc_coef = get_coef(coefs, prem)

                    print_indent('-> -> -> ->', indent, verbose)
                    sbs = deepcopy(aux_substitutions)
                    aux = recursive_bc(kb, [prem], sbs, indent + 1, verbose)
                    print_indent('<- <- <- <-', indent, verbose)

                    if aux == False:
                        print_indent("Premise couldn't be proved", indent, verbose)
                        print_indent("Rule doesn't match the goal", indent, verbose)
                        break

                    print_indent("PROVED", indent, verbose)
                    resolved[subst_index][i] = True

                    if use_coef:
                        l[i] = l[i] * aux
                        print_indent('Updated coefficient is: ' + str(l[i]), indent, verbose)
                        # print_indent(str(l), indent, verbose)
                        continue

                    if aux != [{}]:
                        print_indent('Updated substitution', indent, verbose)
                        for elm in aux:
                            print_substitution(elm, indent, verbose)
                        print_indent('', indent, verbose)

                    aux_substitutions = aux

                if False not in resolved[subst_index]:
                    no_ans = False 

                    print_indent('Rule proved', indent, verbose)

                    if use_coef:
                        minl = min(l)
                        print_indent('Minimum coefficient from premises: ' + str(minl), indent, verbose)
                        # print_indent(str(l), indent, verbose)
                        print_indent('Computing new coefficient of goal... ', indent, verbose)
                        ret = ret + minl - ret*minl
                        print_indent('\t' + str(ret), indent, verbose)
                    aux_substitutions = concat_lists_of_dict([substitutions[subst_index]], aux_substitutions)
                    for elm in aux_substitutions:
                        if elm not in ans:
                            ans.append(elm)

            if not found_rule:
                print_indent('No rule found', indent, verbose)
    
    if use_coef:
        return ret

    if no_ans:
        return False
    ans = unique_substitutions(ans)
    return ans


def backward_chaining(kb, theorem, verbose = False):
    goal = [theorem]
    coef = get_coef(coefs, goal)
    ans = recursive_bc(kb, goal, [{}], 0, verbose, coef)
    return ans

use_coef = False
verbose = False
if len(sys.argv) > 2:
    if '-v' in sys.argv:
        verbose = True
    if '-c' in sys.argv:
        use_coef = True

skb = []
ikb = []
coefs = []

f = open(sys.argv[1])
for line in f:
    if line.isspace():
        continue
    if line[0] == ':' or line[0] == '%' or line[0] == '#':
        continue
    line = "".join(line.split(' '))
    line.rstrip()
    if use_coef:
        index = line.find('%')
        if index == -1:
            coef = 1
        else:
            coef = float(line[index+1:].rstrip())
            line = line[:index]

    if line[0] == '?':
        # print('interogare :')
        aux = (line.strip('?')).strip(' ')
        interogation = create_atom(aux)
        add_statement(ikb, interogation)
    line = line.strip('\n')

    e_interogare = 0
    if line[0] == '?':
        e_interogare = 1

    result = [x.rstrip() for x in line.split(':')]

    e_afirmatie = 0
    if len(result) > 1:
        e_afirmatie = 1

    # print(line)
    if e_afirmatie == 0 and e_interogare == 0:
        aux_str = result[0]

        atom = create_atom(aux_str)
        add_statement(skb, atom)
        if use_coef:
            coefs.append([atom, coef])

    if e_afirmatie == 1 and e_interogare == 0:
        conclusion = create_atom(result[0])
        premises = create_condition(result[1])
        # premises_str = [(x.strip(')') + ')').strip(' ') for x in result[1].split('),')]
        # print(premises_str)

        args = [conclusion]
        # print(len(args))
        for premise in premises:
            args.append(premise)
            # print(args)
        add_statement(skb, *args)
        if use_coef:
            add_coef(coefs, coef, *args)

print("Printing Knowledge Base:")
# skb = get_sports_kb()
print_KB(skb)
print("")

print("Printing Intergoation Base:")
print_KB(ikb)

for i in range(len(ikb)):
    print("---------------------------------")
    print("for: ")
    print_formula(ikb[i])
    print("---------------------------------")
    ans = backward_chaining(skb, ikb[i], verbose)
    if use_coef:
        if ans == 0:
            print False
            continue
        print(ans)
        continue
    if ans != True and ans != False:
        for index in range(len(ans)):
            ans[index] = get_partial_substitution(ans[index], ikb[i])
        if ans == [{}]:
            print('True')
            continue
        for x in ans:
            print_substitution(x)
    else:
        print(ans)