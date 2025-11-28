#-*- coding:utf-8 -*-

lists=[]
sets=()
dicts={}

lists.append('a')
lists.append('c')
lists.append('b')

print(lists)
lists.sort()
print(lists)

sets=('a','b')
print(sets)


dicts['건아']=4.0
a=dicts.get('건아')
print(a,dicts)