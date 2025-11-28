#-*- coding:utf-8 -*-

class Dog:
    dog_name='jeni'
    
    def barks(self,name):
        print(name,'멍멍!!')

class Cat:
    pass

def main():
    dog1=Dog()
    dog1.dog_name='kk'
    dog1.barks(dog1.dog_name)

if __name__=='__main__':
    main()
    