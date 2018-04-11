# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 19:24:42 2017

@author: zli34
"""
import math
import numpy as np
import random
import matplotlib.pyplot as plt 
import copy

class Criminal(object):
    def __init__(self,prop,x,y,wealth,increase=1):
        self.prop=prop
        self.x=x
        self.y=y
        self.wealth=wealth
        self.increase=increase
    

class Gang(object):
    def __init__(self,member,x,y):
        self.member=member
        self.x=x
        self.y=y
        self.tot_prop=0
        for i in self.member:
            self.tot_prop=self.tot_prop+i.prop

    def crime(self,civilian,police,threshold):
        commit=True
        
        if self.tot_prop<threshold:
            commit=False
            
        #do a vision test to see if there is a policeman in the neighborhood
        for p in police:
            if p.x>=math.floor(self.x)-1 and p.x<=math.floor(self.x) and p.y>=math.ceil(self.y) and p.y<=math.ceil(self.y)+1:
                commit=False
                break
            if p.x>=math.floor(self.x) and p.x<=math.floor(self.x)+1 and p.y>=math.ceil(self.y) and p.y<=math.ceil(self.y)+1:
                commit=False
                break
            if p.x>=math.ceil(self.x) and p.x<=math.ceil(self.x)+1 and p.y>=math.ceil(self.y) and p.y<=math.ceil(self.y)+1:
                commit=False
                break
            if p.x>=math.ceil(self.x) and p.x<=math.ceil(self.x)+1 and p.y>=math.floor(self.y) and p.y<=math.floor(self.y)+1:
                commit=False
                break
            if p.x>=math.ceil(self.x) and p.x<=math.ceil(self.x)+1 and p.y>=math.floor(self.y)-1 and p.y<=math.floor(self.y):
                commit=False
                break
            if p.x>=math.floor(self.x) and p.x<=math.floor(self.x)+1 and p.y>=math.floor(self.y)-1 and p.y<=math.floor(self.y):
                commit=False
                break
            if p.x>=math.floor(self.x)-1 and p.x<=math.floor(self.x) and p.y>=math.floor(self.y)-1 and p.y<=math.floor(self.y):
                commit=False
                break
            if p.x>=math.floor(self.x)-1 and p.x<=math.floor(self.x) and p.y>=math.floor(self.y) and p.y<=math.floor(self.y)+1:
                commit=False
                break
            
        
        if commit==True:
            a=[]
            for c in civilian:
                if c.x>=math.floor(self.x) and c.x<=math.floor(self.x)+1 and c.y>=math.floor(self.y) and c.y<=math.floor(self.y)+1 and c.kind==1:
                    a.append(c)
            if len(a)>0:    
                victim=random.sample(a,1)[0]
                victim.wealth=0.5*victim.wealth
                victim.memory=victim.memory+self.member
                #remove the same elements in memory
                #victim.memory=[set(victim.memory)]
            
                for i in self.member:
                    i.wealth=i.wealth+victim.wealth/len(self.member)
                    i.prop=i.prop+i.increase
                    self.tot_prop=self.tot_prop+i.increase
            
            if len(a)==0:
                commit=False
            
                
        return commit
                
    
    def move(self,width,height):
        while True:
            d=random.sample([1,2,3,4],1)[0]
            if d==1 and self.x-1>=0:
                self.x=self.x-1
                for i in self.member:
                    i.x=i.x-1
                break
            if d==2 and self.y-1>=0:
                self.y=self.y-1
                for i in self.member:
                    i.y=i.y-1
                break
            if d==3 and self.x+1<=width:
                self.x=self.x+1
                for i in self.member:
                    i.x=i.x+1
                break
            if d==4 and self.y+1<=height:
                self.y=self.y+1
                for i in self.member:
                    i.y=i.y+1
                break
    
    
class Map(object):
    def __init__(self,width,height,cri_num,civ_num,pol_num,threshold):
        self.width=width
        self.height=height
        self.cri_num=cri_num
        self.civ_num=civ_num
        self.pol_num=pol_num
        self.threshold=threshold
        self.criminal=[]
        self.gang=[]
        self.civilian=[]
        self.police=[]
        self.crime_place=[]
    
    def populate(self):
        for i in range(self.cri_num):
            self.criminal.append(Criminal(prop=random.sample(range(1,11),1)[0],x=random.uniform(0,self.width),y=random.uniform(0,self.height),wealth=random.uniform(0,10)))
        for i in range(self.civ_num):
            self.civilian.append(Civilian(kind=np.random.binomial(1,2/3),x=random.uniform(0,self.width),y=random.uniform(0,self.height),wealth=random.uniform(0,1000)))
        for i in range(self.pol_num):
            self.police.append(Police(x=random.uniform(0,self.width),y=random.uniform(0,self.height)))
        
        
        for i in range(self.width):
            for j in range(self.height):
                a=[]
                for c in self.criminal:
                    #Criminals whose propensity are less than threshold form a big gang
                    if c.x>=i and c.x<i+1 and c.y>=j and c.y<j+1 and c.prop<self.threshold:
                        a.append(c)
                    if c.x>=i and c.x<i+1 and c.y>=j and c.y<j+1 and c.prop>=self.threshold:
                        self.gang.append(Gang(member=[c],x=i+0.5,y=j+0.5))
                if len(a)>0:            
                    self.gang.append(Gang(member=a,x=i+0.5,y=j+0.5))
                    
        
                
        #Plot
        ax=plt.subplot()
        ax.xaxis.set_major_locator(plt.MultipleLocator(1))
        ax.xaxis.grid(True,which='major')
        ax.yaxis.set_major_locator(plt.MultipleLocator(1))
        ax.yaxis.grid(True,which='major')
        
        a={0:"brown",1:"olive",2:"darkgray",3:"darkgreen",4:"darkorange",5:"yellow",6:"darkviolet",7:"firebrick",8:"pink",9:"gold",10:"lightblue"}
        for i in range(len(self.gang)):
            for c in self.gang[i].member:
                ax.scatter(c.x,c.y,color=a[i],marker='x')
        
        for c in self.civilian:
            if c.kind==0:
                ax.scatter(c.x,c.y,color="blue")
            if c.kind==1:
                ax.scatter(c.x,c.y,color="red")
            
        for p in self.police:
            ax.scatter(p.x,p.y,color="black",marker='o')
        
        ax.set_xlim(0,self.width)
        ax.set_ylim(0,self.height)
            
        plt.show()
                
    def update(self):
        #commit a crime
        new_place=[]
        for g in self.gang:
            if g.crime(self.civilian,self.police,self.threshold)==True:
                new_place.append([g.x,g.y])
                print("Crime happens at"+str([g.x,g.y])+".")
                
        if len(new_place)!=0:
            self.crime_place=new_place
        
        
                
        #police move
        random.shuffle(self.police)
        for i in range(len(self.police)):
            #move to the crime place immediately
            if i+1<=len(self.crime_place):
                self.police[i].move(self.width,self.height,self.crime_place[i])
            #randomly move
            if i+1>len(self.crime_place):
                self.police[i].move(width=self.width,height=self.height)
        
        
        #gangs split
        copy_gang=copy.deepcopy(self.gang)
        self.gang=[]
        for i in range(len(copy_gang)):
            k=0
            for j in range(len(copy_gang[i].member)):
                c=copy_gang[i].member[k]
                if c.prop>=self.threshold:
                    copy_gang[i].member.remove(c)
                    self.gang.append(Gang([c],copy_gang[i].x,copy_gang[i].y))
                    continue
                k=k+1
            if len(copy_gang[i].member)!=0:
                self.gang.append(Gang(copy_gang[i].member,copy_gang[i].x,copy_gang[i].y))
                
        
                    
                
        
        #gangs move
        for g in self.gang:
            g.move(self.width,self.height)
        
        
        
        #gangs form
        copy_gang=copy.deepcopy(self.gang)
        self.gang=[]
        for i in range(self.width):
            for j in range(self.height):
                a=[]
                #Gangs whose propensity are less than the threshold form a big gang
                for g in copy_gang:
                    if g.x>=i and g.x<i+1 and g.y>=j and g.y<j+1 and g.tot_prop<self.threshold:
                        a=a+g.member
                    if g.x>=i and g.x<i+1 and g.y>=j and g.y<j+1 and g.tot_prop>=self.threshold:
                        self.gang.append(Gang(member=g.member,x=g.x,y=g.y))
                if len(a)>0:
                    self.gang.append(Gang(member=a,x=i+0.5,y=j+0.5))
                    
        
        
        #civilians move
        for c in self.civilian:
            c.move(self.width,self.height)
        
        #Plot
        ax=plt.subplot()
        ax.xaxis.set_major_locator(plt.MultipleLocator(1))
        ax.xaxis.grid(True,which='major')
        ax.yaxis.set_major_locator(plt.MultipleLocator(1))
        ax.yaxis.grid(True,which='major')
        
        a={0:"brown",1:"olive",2:"darkgray",3:"darkgreen",4:"darkorange",5:"yellow",6:"darkviolet",7:"firebrick",8:"pink",9:"gold",10:"lightblue"}
        for i in range(len(self.gang)):
            for c in self.gang[i].member:
                ax.scatter(c.x,c.y,color=a[i],marker='x')
        
        for c in self.civilian:
            if c.kind==0:
                ax.scatter(c.x,c.y,color="blue")
            if c.kind==1:
                ax.scatter(c.x,c.y,color="red")
            
        for p in self.police:
            ax.scatter(p.x,p.y,color="black",marker='o')
        
        ax.set_xlim(0,self.width)
        ax.set_ylim(0,self.height)
            
        plt.show()
        






class Civilian(object):
    def __init__(self,kind,x,y,wealth,memory=[]):
        #1 is woman and kid; 0 is man
        self.kind=kind
        self.x=x
        self.y=y
        self.wealth=wealth
        self.memory=memory
    
    def move(self,width,height):
        #randomly move if his memory is NULL
        if len(self.memory)==0:
            while True:
                d=random.sample([1,2,3,4],1)[0]
                if d==1 and self.x-1>=0:
                    self.x=self.x-1
                    break
                if d==2 and self.y-1>=0:
                    self.y=self.y-1
                    break
                if d==3 and self.x+1<=width:
                    self.x=self.x+1
                    break
                if d==4 and self.y+1<=height:
                    self.y=self.y+1
                    break
        
        #his memory is not NULL
        if len(self.memory)!=0:
            a=[]
            for criminal in self.memory:
                if criminal.x>=math.floor(self.x)-1 and criminal.x<=math.floor(self.x) and criminal.y>=math.ceil(self.y) and criminal.y<=math.ceil(self.y)+1:
                    a.append([0,1,1,0])
                if criminal.x>=math.floor(self.x) and criminal.x<=math.floor(self.x)+1 and criminal.y>=math.ceil(self.y) and criminal.y<=math.ceil(self.y)+1:
                    a.append([1,1,1,0])
                if criminal.x>=math.ceil(self.x) and criminal.x<=math.ceil(self.x)+1 and criminal.y>=math.ceil(self.y) and criminal.y<=math.ceil(self.y)+1:
                    a.append([1,1,0,0])
                if criminal.x>=math.ceil(self.x) and criminal.x<=math.ceil(self.x)+1 and criminal.y>=math.floor(self.y) and criminal.y<=math.floor(self.y)+1:
                    a.append([1,1,0,1])
                if criminal.x>=math.ceil(self.x) and criminal.x<=math.ceil(self.x)+1 and criminal.y>=math.floor(self.y)-1 and criminal.y<=math.floor(self.y):
                    a.append([1,0,0,1])
                if criminal.x>=math.floor(self.x) and criminal.x<=math.floor(self.x)+1 and criminal.y>=math.floor(self.y)-1 and criminal.y<=math.floor(self.y):
                    a.append([1,0,1,1])
                if criminal.x>=math.floor(self.x)-1 and criminal.x<=math.floor(self.x) and criminal.y>=math.floor(self.y)-1 and criminal.y<=math.floor(self.y):
                    a.append([0,0,1,1])
                if criminal.x>=math.floor(self.x)-1 and criminal.x<=math.floor(self.x) and criminal.y>=math.floor(self.y) and criminal.y<=math.floor(self.y)+1:
                    a.append([0,1,1,1])
            
            
            b=[]
            for i in range(4):
                times=1
                for c in a:
                    times=c[i]*times
                b.append(times)
            
            if self.x-1<0:
                b[0]=0
                if self.y-1<0:
                    b[1]=0
                    if self.x+1>width:
                        b[2]=0
                        if self.y+1>height:
                            b[3]=0
                             
                
            count=0
            for i in b:
                if i==1:
                    count=count+1
                        
            d=random.sample(range(count),1)[0]
                
            e=0
            for i in b:
                if i==1 and e!=d:
                    b[i]=0
                    e=e+1
                        
            for i in range(4):
                if i==0:
                    self.x=self.x-b[i]
                if i==1:
                    self.y=self.y-b[i]
                if i==2:
                    self.x=self.x+b[i]
                if i==3:
                    self.y=self.y+b[i]
                    


class Police(object):
    def __init__(self,x,y):
        self.x=x
        self.y=y
        
    def move(self,width,height,place=[]):
        if len(place)==0:
            #randomly move
            while True:
                d=random.sample([1,2,3,4],1)[0]
                if d==1 and self.x-1>=0:
                    self.x=self.x-1
                    break
                if d==2 and self.y-1>=0:
                    self.y=self.y-1
                    break
                if d==3 and self.x+1<=width:
                    self.x=self.x+1
                    break
                if d==4 and self.y+1<=height:
                    self.y=self.y+1
                    break
                
        if len(place)!=0:
            #go to the crime place immediately
            self.x=place[0]
            self.y=place[1]        
                        
        
            
if __name__=='__main__':
    m=Map(width=5,height=5,cri_num=10,civ_num=20,pol_num=2,threshold=20)
    n_iter=50
    m.populate()
    for i in range(n_iter):
        m.update()








                            
            
                