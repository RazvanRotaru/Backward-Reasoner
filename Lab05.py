
# coding: utf-8

# # Logica cu predicate (1). Reprezentare & Unificare
#  - Andrei Olaru
#  - Tudor Berariu
# 

# ## Scopul laboratorului
# 
# Scopul acestui laborator este familiarizarea cu reprezentarea logică a cunoștințelor și cu mecanismele de lucru cu cunoștințe reprezentate prin logica cu predicate de ordinul I (LPOI / FOPL).
# 
# În cadrul laboratorului, va fi necesar să vă alegeți o reprezentare internă pentru elementele din FOPL, și apoi să implementați procesul de unificare între două formule din logica cu predicate. 
# 
# 
# #### Resurse
# 
# * Cursul 5 de IA, slides 25-27
# * https://en.wikipedia.org/wiki/Unification_(computer_science)#Examples_of_syntactic_unification_of_first-order_terms
# * algoritmul lui Robinson (vezi pdf)
# 

# ## Reprezentare
# 
# În LPOI trebuie să putem reprezenta următoarele elemente:
# * _termen_ -- poate fi luat ca argument de către un predicat. Un termen poate fi:
#   * o constantă -- are o valoare
#   * o variabilă -- are un nume și poate fi legată la o valoare
#   * un apel de funcție -- are numele funcției și argumentele (e.g. add[1, 2, 3]). Se evaluează la o valoare. Argumentele funcției sunt tot termeni.
#     * Notă: În text vom scrie apelurile de funcții cu paranteze drepte, pentru a le deosebi de atomi.
# * _formulă (propoziție) logică_ -- se poate evalua la o valoare de adevăr, într-o interpretare (o anumită legare a numelor la o semantică). O formulă poate fi:
#   * un atom -- aplicarea unui predicat (cu un nume) peste o serie de termeni (argumentele sale)
#   * negarea unei formule
#   * un conector logic între două propoziții -- conjuncție sau disjuncție
#   
# 
# ### Cerința 1
# 
# Creați o reprezentare internă pentru formule logice. Pentru această reprezentare, vom avea:
# * o serie de funcții care o construiesc -- `make_*` și `replace_args`
# * o serie de funcții care o verifică -- `is_*`
# * o serie de funcții care accesează elementele din reprezentare -- `get_*`
# 
# 
# **Important:** Pentru a lucra mai ușor cu formulele, vom considera că pentru apelurile de funcții și pentru toate formulele (atât atomi cât și propoziții compuse), reprezentarea are un _head_ (după caz, numele funcției, numele predicatului, sau conectorul logic) și o listă de argumente (după caz, lista de argumente a funcției, lista de argumente a predicatului, o listă cu propoziția negată, sau lista de propoziții unite de conectorul logic (2 sau mai multe)).
# 
# **Notă:** la început, implementați funcțiile de verificare ca și cum argumentele date are fi reprezentate corect (deci doar pentru a deosebi între diversele tipuri de reprezentare). Ulterior, verificați și ca argumentele date să fie într-adevăr corect reprezentate.

# In[3]:


from operator import add
from copy import deepcopy
# from Lab05tester import test_batch


# In[17]:


### Reprezentare - construcție
class Constant:
    def __init__(self, value):
        self.value = value
    
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Constant):
            return self.value == other.value
        return False

    def print_self(self):
        print(self.value)

class Variable:
    def __init__(self, name, value = 0):
        self.name = name
        self.value = value
    
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Variable):
            return self.name == other.name
        return False
    
    def print_self(self):
        print(self.name + " = " + self.value)
        
class Function:
    def __init__(self, function, args):
        self.args = deepcopy(args)
        self.function = function
        
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Function):
            return self.function == other.function and self.args == other.args
        return False
        
class Atom:
    def __init__(self, predicate, args):
        self.args = deepcopy(args)
        self.predicate = predicate
        
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Atom):
            return self.predicate == other.predicate and self.args == other.args
        return False

class Sentence:
    def __init__(self, atoms, args, neg = False):
        self.atoms = deepcopy(atoms)
        self.args = deepcopy(args)
        self.neg = neg
    
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Sentence):
            return self.args == other.args and self.atoms == other.atoms and self.neg == other.neg
        return False
        
# întoarce un termen constant, cu valoarea specificată.
def make_const(value):
    # TODO
    const = Constant(value)
    return const

# întoarce un termen care este o variabilă, cu numele specificat.
def make_var(name):
    # TODO
    var = Variable(name)
    return var

# întoarce un termen care este un apel al funcției specificate, pe restul argumentelor date.
# E.g. pentru a construi termenul add[1, 2, 3] vom apela make_function_call(add, 1, 2, 3)
# !! ATENȚIE: python dă args ca tuplu cu restul argumentelor, nu ca listă. Se poate converti la listă cu list(args)
def make_function_call(function, *args):
    # TODO
    func = Function(function, list(args))
    return func

# întoarce o formulă formată dintr-un atom care este aplicarea predicatului dat pe restul argumentelor date.
# !! ATENȚIE: python dă args ca tuplu cu restul argumentelor, nu ca listă. Se poate converti la listă cu list(args)
def make_atom(predicate, *args):
    # TODO
    pred = Atom(predicate, list(args))
    return pred

# întoarce o formulă care este negarea propoziției date.
# get_args(make_neg(s1)) va întoarce [s1]
def make_neg(sentence):
    # TODO
    args = []
    atoms = [sentence]
    s = Sentence(atoms, args, True)
    return s

# întoarce o formulă care este conjuncția propozițiilor date (2 sau mai multe).
# e.g. apelul make_and(s1, s2, s3, s4) va întoarce o structură care este conjuncția s1 ^ s2 ^ s3 ^ s4
#  și get_args pe această structură va întoarce [s1, s2, s3, s4]
def make_and(sentence1, sentence2, *others):
    # TODO
    args = ["A"]
    atoms = [sentence1, sentence2]
    
    for i in others:
        atoms.append(i)
        
    s = Sentence(atoms, args)
    return s

# întoarce o formulă care este disjuncția propozițiilor date.
# e.g. apelul make_or(s1, s2, s3, s4) va întoarce o structură care este disjuncția s1 V s2 V s3 V s4
#  și get_args pe această structură va întoarce [s1, s2, s3, s4]
def make_or(sentence1, sentence2, *others):
    # TODO
    args = ["V"]
    atoms = [sentence1, sentence2]
    
    for i in others:
        atoms.append(i)
        
    s = Sentence(atoms, args)
    return s

# întoarce o copie a formulei sau apelul de funcție date, în care argumentele au fost înlocuite
#  cu cele din lista new_args.
# e.g. pentru formula p(x, y), înlocuirea argumentelor cu lista [1, 2] va rezulta în formula p(1, 2).
# Noua listă de argumente trebuie să aibă aceeași lungime cu numărul de argumente inițial din formulă.
def replace_args(formula, new_args):
    # TODO
    
    if isinstance(formula, Atom):
        new_atom_pred = formula.predicate
        formula = Atom(new_atom_pred, new_args)
    
    if isinstance(formula, Function):
        new_func = formula.function
        formula = Function(new_func, new_args)
    
    if isinstance(formula, Sentence):
        new_sthings = formula.args
        is_neg = formula.neg
        formula = Sentence(new_args, new_sthings, is_neg)
    
    return formula

    
    
### Reprezentare - verificare

# întoarce adevărat dacă f este un termen.
def is_term(f):
    return is_constant(f) or is_variable(f) or is_function_call(f)

# întoarce adevărat dacă f este un termen constant.
def is_constant(f):
    # TODO
    return isinstance(f, Constant)

# întoarce adevărat dacă f este un termen ce este o variabilă.
def is_variable(f):
    # TODO
    return isinstance(f, Variable)

# întoarce adevărat dacă f este un apel de funcție.
def is_function_call(f):
    # TODO
    return isinstance(f, Function)

# întoarce adevărat dacă f este un atom (aplicare a unui predicat).
def is_atom(f):
    # TODO
    return isinstance(f, Atom)

# întoarce adevărat dacă f este o propoziție validă.
def is_sentence(f):
    # TODO
    return isinstance(f, Sentence) or isinstance(f, Atom)

# întoarce adevărat dacă formula f este ceva ce are argumente.
def has_args(f):
    return is_function_call(f) or is_sentence(f)


### Reprezentare - verificare

# pentru constante (de verificat), se întoarce valoarea constantei; altfel, None.
def get_value(f):
    # TODO
    if isinstance(f, Constant):
        return f.value
    
    return None

# pentru variabile (de verificat), se întoarce numele variabilei; altfel, None.
def get_name(f):
    # TODO
    if isinstance(f, Variable):
        return f.name
    return None

# pentru apeluri de funcții, se întoarce funcția;
# pentru atomi, se întoarce numele predicatului; 
# pentru propoziții compuse, se întoarce un șir de caractere care reprezintă conectorul logic (e.g. ~, A sau V);
# altfel, None
def get_head(f):
    # TODO
    if isinstance(f, Function):
        return f.function
    if isinstance(f, Atom):
        return f.predicate
    if isinstance(f, Sentence):
        return "".join(f.args)
    return None

# pentru propoziții sau apeluri de funcții, se întoarce lista de argumente; altfel, None.
# Vezi și "Important:", mai sus.
def get_args(f):
    # TODO
    if isinstance(f, Function):
        return f.args
    if isinstance(f, Sentence):
        return f.atoms
    if isinstance(f, Atom):
        return f.args
    return []

# test_batch(0, globals())


# In[18]:


# Afișează formula f. Dacă argumentul return_result este True, rezultatul nu este afișat la consolă, ci întors.
def print_formula(f, return_result = False, indent = 0, verbose = True):
    if not verbose:
        return
    ret = "\t" * indent
    if is_term(f):
        if is_constant(f):
            ret += str(get_value(f))
        elif is_variable(f):
            ret += "?" + get_name(f)
        elif is_function_call(f):
            ret += str(get_head(f)) + "[" + "".join([print_formula(arg, True) + "," for arg in get_args(f)])[:-1] + "]"
        else:
            ret += "???"
    elif is_atom(f):
        ret += str(get_head(f)) + "(" + "".join([print_formula(arg, True) + ", " for arg in get_args(f)])[:-2] + ")"
    elif is_sentence(f):
        # negation, conjunction or disjunction
        args = get_args(f)
        if len(args) == 1:
            ret += str(get_head(f)) + print_formula(args[0], True)
        else:
            ret += "(" + str(get_head(f)) + "".join([" " + print_formula(arg, True) for arg in get_args(f)]) + ")"
    else:
        ret += "???"
    if return_result:
        return ret
    print(ret)
    return
    
# Verificare construcție și afișare
# Ar trebui ca ieșirea să fie similară cu: (A (V ~P(?x) Q(?x)) T(?y, <built-in function add>[1,2]))
# formula1 = make_and(
#     make_or(make_neg(make_atom("P", make_var("x"))), make_atom("Q", make_var("x"))),
#     make_atom("T", make_var("y"), make_function_call(add, make_const(1), make_const(2))))
# print_formula(formula1)


# ## Unificare
# 
# Unificarea a două formule logice ce conțin variabile înseamnă găsirea unei substituții astfel încât aplicarea acesteia pe cele două formule să rezulte în două formule identice.
# 
# O substituție conține asocieri de variabile la termeni. La aplicarea unei substituții, variabilele care apar în substituție sunt înlocuite, în formulă, cu termenii asociați, până când nu se mai poate face nicio înlocuire.

# In[19]:


# Aplică în formula f toate elementele din substituția dată și întoarce formula rezultată
def substitute(f, substitution):
    if substitution is None:
        return None
    if is_variable(f) and (get_name(f) in substitution):
        return substitute(substitution[get_name(f)], substitution)
    if has_args(f):
        return replace_args(f, [substitute(arg, substitution) for arg in get_args(f)])
    return f

def test_formula(x, copyy = False):
    fun = make_function_call(add, make_const(1), make_const(2))
    return make_and(make_or(make_neg(make_atom("P", make_const(x))), make_atom("Q", make_const(x))),                     make_atom("T", fun if copyy else make_var("y"), fun))

# Test (trebuie să se vadă efectele substituțiilor în formulă)
# test_batch(1, globals())


# ### Cerința 2
# 
# Implementați funcțiile `occur_check` și `unify`, conform algoritmului lui Robinson (vezi pdf).

# In[39]:


# Verifică dacă variabila v apare în termenul t, având în vedere substituția subst.
# Întoarce True dacă v apare în t (v NU poate fi înlocuită cu t), și False dacă v poate fi înlocuită cu t.
def occur_check(v, t, subst):
    # TODO
    
    if isinstance(t, Function) and (v in get_args(t)):
        return True
    if isinstance(t, Variable) and v == t:
        return True
    
    elif isinstance(t, Variable) and (t.name in subst):    
        return occur_check(v, substitute(t, subst), subst)
    elif isinstance(t, Function):
        for i in t.args:
            if occur_check(v, i, subst):
                return True
            
    return False

# Test!
# test_batch(2, globals())


# In[65]:


# Unifică formulele f1 și f2, sub o substituție existentă subst.
# Rezultatul unificării este o substituție (dicționar nume-variabilă -> termen),
#  astfel încât dacă se aplică substituția celor două formule, rezultatul este identic.
def unify(f1, f2, subst = None):
    S = []
    S.append([f1, f2])
    # print('unify primeste')
    # print_formula(f1)
    # print_formula(f2    )
    if subst is None:
        subst = {}
    # TODO
    
    while S:
        aux = S.pop()
        s = aux[0]
        t = aux[1]
        
        while isinstance(s, Variable) and (s.name in subst):
            # print_formula(s)
            s = substitute(s, subst)
            # print_formula(s)
        
        while isinstance(t, Variable) and (t.name in subst):
            t = substitute(t, subst)
            
        # print('====')
        # print_formula(s)
        # print_formula(t)
        # print('====')
        # print(s==t)
        # print(not s.__eq__(t))
        if not s.__eq__(t):
            # print('vvvv')
            # print_formula(s)
            # print_formula(t)
            # print('^^^^')
            # print('diferite')
            if isinstance(s, Variable):
                if occur_check(s, t, subst):
                    return False
                else:
                    subst.__setitem__(s.name,t)
                    
            elif isinstance(t, Variable):
                if occur_check(t, s, subst):
                    return False
                else:
                    subst.__setitem__(t.name,s)
            
            elif has_args(s) and has_args(t):
                if get_head(s) == get_head(t):
                    args_s = get_args(s)
                    args_t = get_args(t)
                    for i in range(0, len(args_s)):
                        S.append([args_s[i], args_t[i]])
                else:
                    return False
         
            else:
                return False
        
    return subst

# Test!
# test_batch(3, globals())

