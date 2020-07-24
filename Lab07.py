#!/usr/bin/env python
# coding: utf-8

# # Logica cu predicate (3). Înlănțuire înainte în Sisteme bazate pe reguli
# 
# - Tudor Berariu
# - Andrei Olaru
# 
# ## 1. Introducere
# ### Scopul laboratorului
# 
# Scopul acestui laborator îl reprezintă înțelegerea și implementarea demonstrării teoremelor prin înlănțuire înainte.
# 
# ### Clauze definite. Reguli. Fapte
# 
# În cadrul acestui laborator vom folosi un tip anume de formule, mai precis **clauze definite**. Acestea sunt clauze Horn cu exact un literal pozitiv.
# 
# $$\neg p_1 \vee \neg p_2 \vee \ldots \vee \neg p_N \vee c$$
# 
# În scrierea echivalentă:
# 
# $$\left( p_1 \wedge p_2 \wedge \ldots \wedge p_N \right) \rightarrow c$$
# 
# devine evident ce reprezintă clauzele definite. Ele au o formă asemănătoare regulilor.
# 
# Vom numi **regulă** o clauză definită cu cel puțin un literal negativ și vom numi **fapt** o clauză definită cu un singur literal (cel pozitiv).
# 
# ### Problema de rezolvat
# 
# Problema pe care o vom rezolva astăzi se enunță astfel: *dată fiind o bază de cunoștințe* `kb` *formată din clauze definite (fapte și reguli), să se demonstreze o teoremă* `t`.

# ## 2. Funcții utile din laboratoarele anterioare
# 
# ### Cerința 0
# 
# Salvați rezolvarea laboratorului 5 (*Reprezentare și Unificare*) cu numele `Lab05.py`. Vom folosi și funcțiile deja implementate din Laboratorul 6. Din acesta, funcțiile importante pentru astăzi sunt:
#  - `make_var`, `make_const`, `make_atom` - utile pentru a construi atomi. De exemplu, $$Vreme(maine, Frig)$$ se construiește astfel:
#      
#      `make_atom("Vreme", make_var("maine"), make_const("Frig"))`
#  
#  - `unify` și `substitute` - utile pentru calcularea celui mai general unificator pentru două formule și pentru aplicarea unei substituții
#  - `is_positive_literal` și `is_negative_literal`
#  - `add_statement` - adaugă o clauză definită unei baze de cunoștințe. Avem două variante de utilizare în acest laborator:
#    * `add_statement(kb, Atom)` - adaugă în kb faptul Atom
#    * `add_statement(kb, C, P1, P2, Pn)` - adaugă în kb regula $\left( p_1 \wedge p_2 \wedge p_N \right) \rightarrow c$ sub forma:
#    
#    `make_or(make_neg(P1), make_neg(P2), make_neg(Pn), C)`
#    
# ### Cerința 1
# 
# Faceți următoarea modificare funcției `unify`: antetul funcției
# 
#     def unify(f1, f2):
#         ...
#         subst = {}
# 
# trebuie transformat astfel încât să primească un al treilea parametru, o substituție de pornire
# 
#     def unify(f1, f2, subst=None):
#         if not subst:
#             subst = {}
# 
# **Nu uitați** ca după modificarea lui `unify` să descărcați din nou laboratorul 5 ca fișier Python și să dați Kernel restart în acest fișier.

# In[1]:


from Lab05 import make_var, make_and, make_const, make_atom, make_or, make_neg,                 is_variable, is_sentence, is_constant, is_atom, is_function_call,                 print_formula, get_args, get_head, get_name, get_value ,                unify, substitute
from Lab07fct import add_statement, is_positive_literal, is_negative_literal,                 make_unique_var_names, print_KB
from LPTester import *


# ## 3. Baza de cunoștințe
# 
# Să se completeze reprezentarea bazei de cunoștințe de mai jos știind că ea corespunde următoarelor afirmații:
# 
# [TODO 2.1:] *Dacă a plouat două zile la rând, a treia zi va fi frumos.* [TODO 2.2:] *Dacă a fost frumos trei zile la rând, în cea de-a patra zi va ploua.* [TODO 2.3:] *Un student merge întotdeauna la munte dacă este frumos într-o zi de weekend. Cine merge la munte și practică un sport de iarnă va avea activități legate de acel sport de iarnă.*
# 
# *Arsenie și Nectarie sunt studenți. Arsenie practică volei și schi, iar Nectarie practică schi și sanie. Voleiul este un sport de vară, în timp ce schiul și sania sunt sporturi de iarnă. Vineri plouă; luni, marți și miercuri este frumos*
# 
# ### Cerința 2:
# 
# Completați mai jos clauzele definite pentru primele 3 propoziții.
# * `add_statement` are ca argumente
#   * baza de cunoștințe
#   * concluzia
#   * premisele (ca argumente individuale)

# In[137]:


def get_sports_kb():
    sports_kb = []
    # Predicatul 'Consecutive'
    add_statement(sports_kb, make_atom('Consecutive', make_const('Luni'), make_const('Marti')))
    add_statement(sports_kb, make_atom('Consecutive', make_const('Marti'), make_const('Miercuri')))
    add_statement(sports_kb, make_atom('Consecutive', make_const('Miercuri'), make_const('Joi')))
    add_statement(sports_kb, make_atom('Consecutive', make_const('Joi'), make_const('Vineri')))
    add_statement(sports_kb, make_atom('Consecutive', make_const('Vineri'), make_const('Sambata')))
    add_statement(sports_kb, make_atom('Consecutive', make_const('Sambata'), make_const('Duminica')))
    # Predicatul 'Weekend'
    add_statement(sports_kb, make_atom('Weekend', make_const('Sambata')))
    add_statement(sports_kb, make_atom('Weekend', make_const('Duminica')))
    # Predicatul 'Ploua'
    add_statement(sports_kb, make_atom('Ploua', make_const('Vineri')))
    # TODO 2.1: Dacă a plouat două zile la rând, a treia zi va fi frumos.
    add_statement(sports_kb, make_atom('Frumos',  make_var('day3')), make_atom('Ploua', make_var('day1')),
                 make_atom('Ploua', make_var('day2')), make_atom('Consecutive', make_var('day1'), make_var('day2')),
                 make_atom('Consecutive', make_var('day2'), make_var('day3')))
    # Predicatul 'Frumos'
    add_statement(sports_kb, make_atom('Frumos', make_const('Luni')))
    add_statement(sports_kb, make_atom('Frumos', make_const('Marti')))
    add_statement(sports_kb, make_atom('Frumos', make_const('Miercuri')))
    # TODO 2.2: Dacă a fost frumos trei zile la rând, în cea de-a patra zi va ploua.
    add_statement(sports_kb, make_atom('Ploua', make_var('day4')), make_atom('Frumos', make_var('day1')),
                 make_atom('Frumos', make_var('day2')), make_atom('Frumos', make_var('day3')),
                 make_atom('Consecutive', make_var('day1'), make_var('day2')), make_atom('Consecutive', make_var('day2'), make_var('day3')),
                 make_atom('Consecutive', make_var('day3'), make_var('day4')))
    # Predicatul 'Student'
    add_statement(sports_kb, make_atom('Student', make_const('Nectarie')))
    add_statement(sports_kb, make_atom('Student', make_const('Arsenie')))
    # MergeLaMunte (cine, cand)
    # TODO 2.3: Un student merge întotdeauna la munte dacă este frumos într-o zi de weekend.
    add_statement(sports_kb, make_atom('MergeLaMunte', make_var('Student'), make_var('when')), make_atom('Weekend', make_var('when')),
                 make_atom('Frumos', make_var('when')))
    # Predicatul 'SportDeVara'
    add_statement(sports_kb, make_atom('SportDeVara', make_const('Volei')))
    # Predicatul 'SportDeIarna'
    add_statement(sports_kb, make_atom('SportDeIarna', make_const('Schi')))
    add_statement(sports_kb, make_atom('SportDeIarna', make_const('Sanie')))
    # Predicatul 'PracticaSport'
    add_statement(sports_kb, make_atom('PracticaSport', make_const('Nectarie'), make_const('Schi')))
    add_statement(sports_kb, make_atom('PracticaSport', make_const('Nectarie'), make_const('Sanie')))
    add_statement(sports_kb, make_atom('PracticaSport', make_const('Arsenie'), make_const('Schi')))
    add_statement(sports_kb, make_atom('PracticaSport', make_const('Arsenie'), make_const('Volei')))
    # Predicatul 'Activitate'
    add_statement(sports_kb, make_atom('Activitate', make_var('who'), make_var('what'), make_var('when')),
                  make_atom('MergeLaMunte', make_var('who'), make_var('when')),
                  make_atom('PracticaSport', make_var('who'), make_var('what')))
    make_unique_var_names(sports_kb)
    return sports_kb


# print("Baza de cunoștințe se prezintă astfel:")
# skb = get_sports_kb()
# print_KB(skb)
# print("==================== \n Baza de cunoștințe arată intern astfel:")
# print("" + "".join([(str(s) + "\n") for s in skb]))


# ## 4. Funcții auxiliare
# 
# **Cerința 3:** Implementați funcțiile `get_premises`, `get_conclusion`, `is_fact` și `is_rule`. Toate acestea primesc o clauză definită (în baza de cunoștințe dată, poate fi un atom singur sau o disjuncție de literali) și întorc ceea ce specifică numele lor.

# In[138]:


def get_premises(formula):
    # TODO
    ans = []
    for i in get_args(formula):
        if is_negative_literal(i):
            ans.append(i)
    return ans

def get_conclusion(formula):
    # TODO
    ans = None
    for i in get_args(formula):
        if is_atom(i):
            ans = i
    return ans
  
def is_fact(formula):
    # TODO
    if is_positive_literal(formula):
        return True
    return False

def is_rule(formula):
    # TODO
    for i in get_args(formula):
        if is_negative_literal(i):
            return True
    return False

# # Test!
# # formula: P(x) ^ Q(x) -> R(x)
# x = make_or(make_neg(make_atom('Frumos', make_var('day1'))),
#                  make_neg(make_atom('Frumos', make_var('day2'))), make_neg(make_atom('Frumos', make_var('day3'))),
#                  make_neg(make_atom('Consecutive', make_var('day1'), make_var('day2'))), make_neg(make_atom('Consecutive', make_var('day2'), make_var('day3'))),
#                  make_neg(make_atom('Consecutive', make_var('day3'), make_var('day4'))), make_atom('Ploua', make_var('day4')))
# f = make_or(make_neg(make_atom("P", make_var("x"))), make_neg(make_atom("Q", make_var("x"))), make_atom("R", make_var("x")))
# print(" ; ".join([print_formula(p, True) for p in get_premises(x)])) # Should be P(?x) ; Q(?x)
# print_formula(get_conclusion(f)) # Should be R(?x)
# print(is_rule(f)) # must be True
# print(is_fact(f)) # must be False
# print(is_fact(get_conclusion(f))) # must be True
# print(is_rule(get_conclusion(f))) # must be False


# # In[139]:


def equal_terms(t1, t2):
    if is_constant(t1) and is_constant(t2):
        return get_value(t1) == get_value(t2)
    if is_variable(t1) and is_variable(t2):
            return get_name(t1) == get_name(t2)
    if is_function_call(t1) and is_function(t2):
        if get_head(t1) != get_head(t2):
            return all([equal_terms(get_args(t1)[i], get_args(t2)[i]) for i in range(len(get_args(t1)))])
    return False

def is_equal_to(a1, a2):
    # verificăm atomi cu același nume de predicat și același număr de argumente
    if not (is_atom(a1) and is_atom(a2) and get_head(a1) == get_head(a2) and len(get_args(a1)) == len(get_args(a2))):
        return False
    return all([equal_terms(get_args(a1)[i], get_args(a2)[i]) for i in range(len(get_args(a1)))])


# ## 5. Demonstrarea teoremelor prin înlănțuire înainte
# 
# ### Cerința 4
# 
# Implementați funcția `apply_rule(rule, facts)` care primește o regulă și un set de fapte și întoarce toate faptele care pot fi determinate prin aplicarea regulii pe faptele date.
# 
# Folosiți-vă de `unify`, `substitute`, dar și de `get_premises` și `get_conclusion` implementate mai devreme.

# In[166]:


from copy import deepcopy
# from __future__ import print_function
import itertools
from Lab05 import Sentence, Atom

def apply_rule(rule, facts):
    # TODO
    subst = {}
    prem = {}
    ans = []
    values = {}
    fact_values = {}
    
    for fact in facts:
        vals = []
        for arg in get_args(fact):
            vals.append(get_value(arg))
        if get_head(fact) not in values:
            values[get_head(fact)] = [tuple(vals)]
        else:
            values[get_head(fact)].append(tuple(vals))
            
        if get_head(fact) not in fact_values:
            fact_values[get_head(fact)] = [fact]
        else:
            fact_values[get_head(fact)].append(fact)
    
    for r in get_premises(rule):
        if isinstance(r, Sentence):
            var = get_name(get_args(get_args(r)[0])[0])
            prm = get_head(get_args(r)[0])
            prem[(prm, var)] = get_args(r)[0]
            continue
        var = get_name(get_args(r)[0])
        prem[(get_head(r), var)] = [r]

    index_h = {}
    max_index_h = {}
    for (pred, var) in prem:
        index_h[(pred, var)] = 0
        max_index_h[(pred, var)] = 0
        if pred in values:
            max_index_h[(pred, var)] = len(values[pred])
    
    
    pred = []
    for x in prem:
        pred.append(x)
    current_p = 0
    subst = {}
    while 1:
        p = pred[current_p]
        prd = p[0]
        val = p[1]
        p_index = index_h[p]
            
        if p_index == max_index_h[p]:
            index_h[p] = 0
            
            if current_p == 0:
                break
                
            current_p = current_p - 1
            p = pred[current_p]
            
            for x in get_args(prem[p]):
                name = get_name(x)
                if name in subst:
                    del subst[name]
            index_h[p] = index_h[p] + 1
            continue
        
        b_subst = deepcopy(subst)
        
        aux_subst = unify(prem[p], fact_values[prd][p_index], subst)
        if aux_subst!=False:
            subst = aux_subst
            if current_p == len(pred) - 1:
                ans.append(substitute(get_conclusion(rule),subst))
                subst = {}
                current_p = 0
                
                next_index = index_h[p] + 1
                    
                index_h[p] = next_index
                p = pred[current_p]

                continue
        else:
            subst = b_subst
            index_h[p] = index_h[p] + 1
            if index_h[p] == max_index_h[p]:
                index_h[p] = 0
                current_p = current_p - 1
                index_h[pred[current_p]] = index_h[pred[current_p]] + 1
                p = pred[current_p]
                for x in get_args(prem[p]):
                    name = get_name(x)
                    if name in subst:
                        del subst[name]
            continue
            
        
        if current_p < len(pred) - 1:
            current_p = current_p + 1
            continue
        index_h[p] = index_h[p] + 1

    return ans

# # Test!
# # Rule: P(x) => Q(x)
# # Facts: P(1)
# print("Expected: ", print_formula(make_atom('Q', make_const(1)), True), "Result:")
# for f in apply_rule( 
#         make_or(make_neg(make_atom("P", make_var("x"))), make_atom("Q", make_var("x"))), \
#         [make_atom("P", make_const(1))]):
#     print_formula(f) # should be Q(1)
# print("=====")
# # Rule: P(x) ^ Q(x) => R(x)
# # Facts: P(1), P(2), P(3), Q(3), Q(2)
# print("Expected: ", print_formula(make_atom('R', make_const(2)), True), ";",
#       print_formula(make_atom('R', make_const(3)), True), "Result:")
# for f in apply_rule( 
#         make_or(
#             make_neg(make_atom("P", make_var("x"))),
#             make_neg(make_atom("Q", make_var("x"))),
#             make_atom("R", make_var("x"))),
#         [make_atom("P", make_const(x)) for x in [1, 2, 3]] + \
#         [make_atom("Q", make_const(x)) for x in [3, 2]]):
#     print_formula(f) # should be R(2) and R(3)
# print("=====")
# # Rule: P(x) ^ Q(y) ^ R(x, y) => T(x, y)
# # Facts: P(1), P(2), P(3), Q(3), Q(2), R(3, 2)
# print("Expected: ", print_formula(make_atom('T', make_const(3), make_const(2)), True), "Result:")
# for f in apply_rule( 
#         make_or(
#             make_neg(make_atom("P", make_var("x"))),
#             make_neg(make_atom("Q", make_var("y"))),
#             make_neg(make_atom("R", make_var("x"), make_var("y"))),
#             make_atom("T", make_var("x"), make_var("y"))),
#         [make_atom("P", make_const(x)) for x in [1, 2, 3]] + \
#         [make_atom("Q", make_const(x)) for x in [3, 2]] + \
#         [make_atom("R", make_const(3), make_const(2))]):
#     print_formula(f) # should be T(3, 2)
# print("=====")
# # Rule: P(x) ^ Q(y) ^ R(x, y, z) => T(z)
# # Facts: P(1), P(2), P(3), Q(3), Q(2), R(1, 1, 1), R(2, 1, 2), R(2, 3, 5), R(4, 2, 3), R(1, 2, 6)
# print("Expected: ", print_formula(make_atom('T', make_const(5)), True), ";", 
#       print_formula(make_atom('T', make_const(6)), True), "Result:")
# for f in apply_rule( 
#         make_or(
#             make_neg(make_atom("P", make_var("x"))),
#             make_neg(make_atom("Q", make_var("y"))),
#             make_neg(make_atom("R", make_var("x"), make_var("y"), make_var("z"))),
#             make_atom("T", make_var("z"))),
#         [make_atom("P", make_const(x)) for x in [1, 2, 3]] + \
#         [make_atom("Q", make_const(x)) for x in [3, 2]] + \
#         [make_atom("R", make_const(x), make_const(y), make_const(z)) \
#              for x, y, z in [(1, 1, 1), (2, 1, 2), (2, 3, 5), (4, 2, 3), (1, 2, 6)]]):
#     print_formula(f) # should be T(5) and T(6)


# In[167]:


def forward_chaining(kb, theorem, verbose = True):
    # Salvăm baza de date originală, lucrăm cu o copie
    local_kb = deepcopy(kb)
    # Două variabile care descriu starea căutării
    got_new_facts = True   # s-au găsit fapte noi la ultima căutare
    is_proved = False      # a fost demostrată teorema
    # Verificăm dacă teorema este deja demonstrată
    for fact in filter(is_fact, local_kb):
        if unify(fact, theorem):
            if verbose: print("This already in KB: " + print_formula(fact, True))
            is_proved = True
            break
    while (not is_proved) and got_new_facts:
        got_new_facts = False
        for rule in filter(is_rule, local_kb):
            # Pentru fiecare regulă
            new_facts = apply_rule(rule, list(filter(is_fact, local_kb)))
            new_facts = list(filter(lambda fact: not any(list(filter(lambda orig: is_equal_to(fact, orig), local_kb))), new_facts))
            if new_facts:
                if verbose: print("Applied rule: " + print_formula(rule, True) + ", obtained " + str(len(new_facts)) + " new facts.")
                if any(filter(lambda t: is_variable(t), get_args(get_conclusion(rule)))) and                     any(filter(lambda fact: is_equal_to(fact, get_conclusion(rule)), new_facts)):
                        print("Demonstration is too general, the conclusion is not instantiated (facts obtained:", 
                              ",".join([print_formula(f, True) for f in new_facts]),").")
                        return False
                got_new_facts = True
                for fact in new_facts:
                    #if verbose: print("New fact: " + print_formula(fact, True))
                    if unify(fact, theorem) != False:
                        is_proved = True
                        add_statement(local_kb, fact)
                        if verbose: print("Now in KB: " + print_formula(fact, True))
                        break
                    add_statement(local_kb, fact)
            if is_proved:
                break
    if verbose:
        if is_proved:
            print("The theorem is TRUE!")
        else:
            print("The theorem is FALSE!")
    return is_proved


# In[168]:


# def test_result(result, truth):
#     print("Test OK!" if result == truth else "Test FAILED!")

# test_kb = skb
# print("================== 0")
# test_result(forward_chaining(deepcopy(test_kb), make_atom("Frumos", make_var("x")), True), True)
# print("================== 1")
# test_result(forward_chaining(deepcopy(test_kb), make_atom("Ploua", make_var("x")), True), True)
# print("================== 2")
# test_result(forward_chaining(deepcopy(test_kb), make_atom("Ploua", make_const("Joi")), True), True)
# print("================== 3")
# test_result(forward_chaining(deepcopy(test_kb), make_atom("Frumos", make_const("Sambata")), True), True)
# print("================== 4")
# test_result(forward_chaining(deepcopy(test_kb),
#                              make_atom("Activitate",
#                                        make_const("Arsenie"), make_var("sport"), make_const("Sambata")), True), True)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




