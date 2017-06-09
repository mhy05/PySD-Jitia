"""
functions.py

These are supports for functions that are included in modeling software but have no
straightforward equivalent in python.

"""

import numpy as np
import scipy.stats as stats  # Todo: can we get away from the scipy dependency?
import re
# Todo: Pull this out of a class and make it flat for inclusion in the model file


class Functions(object):
    """Provides SD-specific calculations that are not available in python standard libraries,
    or have a different functional form to those specified in the libraries, and therefore
    are in need of translation.
    
    This is implemented as a class, with a local pointer to the model components class, 
    because some of these functions need to reference the internal state of the model.
    Mostly they are just referencing the simulation time.
    """

    def __init__(self, component_class):
        self.components = component_class


    def if_then_else(self, condition, val_if_true, val_if_false):
        """Replicates vensim's IF THEN ELSE function. """
        if condition:
            return val_if_true
        else:
            return val_if_false


    def pulse(self, start, duration):
        """ Implements vensim's PULSE function

        In range [-inf, start) returns 0
        In range [start, start+duration) returns 1
        In range [start+duration, +inf] returns 0
        """
        t = self.components.t
        return 1 if t >= start and t < start+duration else 0

    # Warning: I'm not totally sure if this is correct
    def pulse_train(self, start, duration, repeattime, end):
        """ Implements vensim's PULSE TRAIN function

        """

        t = self.components.t
        return 1 if t >= start and (t-start)%repeattime < duration else 0

    def ramp(self, slope, start, finish):
        """ Implements vensim's RAMP function """
        t = self.components.t
        if t < start:
            return 0
        elif t > finish:
            return slope * (start-finish)
        else:
            return slope * (t-start)

    def bounded_normal(self, minimum, maximum, mean, std, seed):
        """ Implements vensim's BOUNDED NORMAL function """
        np.random.seed(seed)
        return stats.truncnorm.rvs(minimum, maximum, loc=mean, scale=std)

def step(time, value, tstep):
    """" Impliments vensim's STEP function

    In range [-inf, tstep) returns 0
    In range [tstep, +inf] returns `value`
    """
    if np.shape(value)!=np.shape(tstep) and len(np.shape(value))==2:
        return np.swapaxes(np.where(time>=tstep,np.swapaxes(value,0,1),0),0,1)
    return np.where(time>=tstep,value,0)

def frange(x, y, jump):
    value=[]
    while x <= y:
        value.append(x)
        x += jump
    return value

def tabhl(ys,x,xinitial,xfinal,step):
    return lookup(x,frange(xinitial,xfinal,step),ys)

def lookup(x, xs, ys):
    """ Provides the working mechanism for lookup functions the builder builds """
    if not isinstance(xs,np.ndarray):
        return np.interp(x,xs,ys)
    if not isinstance(x,(list,np.ndarray)):
        x=x*np.ones(np.shape(xs))        
    if np.shape(x)!=np.shape(xs) and len(np.shape(xs))==2 and len(np.shape(x))>0:
        if len(np.shape(x))==2:
            x=x.swapaxes(0,1)
        else:
            if np.shape(xs)[0]==np.shape(x):
                x=np.swapaxes(np.resize(x,np.shape(np.swapaxes(xs,0,1))),0,1)
            else:
                x=np.resize(x,np.shape(xs))   
        np.reshape(x,np.shape(xs))       
    resultarray=np.ndarray(np.shape(x))
    for i,j in np.ndenumerate(x):
        resultarray[i]=np.interp(j,np.array(xs)[i],np.array(ys)[i])
    return resultarray


def if_then_else(condition,val_if_true,val_if_false):
    return np.where(condition,val_if_true,val_if_false)


def pos(number):  # dont divide by 0
    return np.maximum(number, 0.000001)

def active_initial(expr, initval):
    if _t == initial_time():
        return initval
    else:
        return expr

def tuner(number, factor):
    if factor>1:
        if number == 0:
            return 0
        else:
            return max(number,0.000001)**factor
    else:
        return (factor*number)+(1-factor)
        
def tune1(in_element,tuner):
    return np.maximum(1e-6,(tuner*in_element+(1.0-tuner)*1.0))         
        
def shorthander(orig,dct,refdct,dictionary):
    if refdct == 0:
        return orig
    elif len(refdct) == 1:
        return orig
    def getnumofelements(element,dictionary):
        if element=="":
            return 0
        position=[]
        elements=element.replace('!','').replace('','').split(',')
        for element in elements:
            if element in dictionary.keys():
                if isinstance(dictionary[element],list):
                    position.append((getnumofelements(dictionary[element][-1],dictionary))[0])
                else:
                    position.append(len(dictionary[element]))
            else:
                for d in dictionary.itervalues():
                    try:
                        (d[element])
                    except: pass
                    else:
                        position.append(len(d))
        return position
    def getshape(refdct):
        return tuple(getnumofelements(','.join([names for names,keys in refdct.iteritems()]),dictionary))
    def tuplepopper(tup,pop):
        tuparray=list(tup)
        for i in pop:
            tuparray.remove(i)
        return tuple(tuparray)
    def swapfunction(dct,refdct,counter=0):
        if len(dct)<len(refdct):
            tempdct = {}
            sortcount=0
            for i in sorted(refdct.values()):
                if refdct.keys()[refdct.values().index(i)] not in dct:
                    tempdct[refdct.keys()[refdct.values().index(i)]]=sortcount
                    sortcount+=1
            finalval=len(tempdct)
            for i in sorted(dct.values()):
                tempdct[dct.keys()[dct.values().index(i)]]=finalval+i
        else:
            tempdct=dct.copy()
        if tempdct==refdct:
            return '(0,0)'
        else:
            for sub,pos in tempdct.iteritems():
                if refdct.keys()[refdct.values().index(counter)]==sub:
                    tempdct[tempdct.keys()[tempdct.values().index(counter)]]=pos
                    tempdct[sub]=counter
                    try:
                        return '(%i,%i);'%(pos,counter)+swapfunction(tempdct,refdct,counter+1)
                    except:
                        print pos,counter,tempdct,refdct,counter
#############################################################################    
    if len(dct)<len(refdct):
        dest=getshape(refdct)
        copyoforig=np.ones(tuplepopper(dest,np.shape(orig))+np.shape(orig))*orig
    else:
        copyoforig=orig
    process=swapfunction(dct,refdct).split(';')
    for i in process:
        j=re.sub(r'[\(\)]','',i).split(',')
        copyoforig=copyoforig.swapaxes(int(j[0]),int(j[1]))
    return copyoforig

def sums(expression,count=0):
    operations = ['+','-','*','/']
    merge=[]
    if count == len(operations):
        return 'np.sum(%s)'%expression
    for sides in expression.split(operations[count]):
        merge.append(sum(sides,count+1))
    return operations[count].join(merge)

def sumv(expression,first,last,lastalt=''):
    if lastalt=='':
        if isinstance(first,(list,np.ndarray)):
            if isinstance(last,(list,np.ndarray)):
                return [np.sum(expression[first[x]-1:last[x]]) for x,y in np.ndenumerate(first)]
            return [np.sum(expression[x-1:last]) for x in first]
        elif isinstance(last,(list,np.ndarray)):
            return [np.sum(expression[first-1:x]) for x in last]
        return np.sum(expression[first-1:last])
    else:
        returnarray=np.ndarray(np.shape(expression))
        if isinstance(last,(list,np.ndarray)):
            last=np.resize(last,np.shape(expression))
            if isinstance(lastalt,(list,np.ndarray)):
                lastalt=np.resize(lastalt,np.shape(expression))
                for x,y in np.ndenumerate(returnarray):
                    returnarray[x]=np.sum(expression[last[x]-1:lastalt[x]])
                return returnarray
            for x,y in np.ndenumerate(returnarray):
                returnarray[x]=np.sum(expression[last[x]-1:lastalt])
            return returnarray
        elif isinstance(lastalt,(list,np.ndarray)):
            for x,y in np.ndenumerate(returnarray):
                if np.shape(lastalt)==np.shape(returnarray):
                    z=x
                else:
                    z=x[len(x)-1-first]
                returnarray[x]=np.sum(expression[last-1:lastalt[z]])
            return returnarray
        return np.sum(expression[last-1:lastalt],first)
    
def prdv(expression,first,last,lastalt=''):
    if lastalt=='':
        if isinstance(first,(list,np.ndarray)):
            if isinstance(last,(list,np.ndarray)):
                return [np.prod(expression[first[x]-1:last[x]]) for x,y in np.ndenumerate(first)]
            return [np.prod(expression[x-1:last]) for x in first]
        elif isinstance(last,(list,np.ndarray)):
            return [np.prod(expression[first-1:x]) for x in last]
        return np.prod(expression[first-1:last])
    else:
        returnarray=np.ndarray(np.shape(expression))
        if isinstance(last,(list,np.ndarray)):
            last=np.resize(last,np.shape(expression))
            if isinstance(lastalt,(list,np.ndarray)):
                lastalt=np.resize(lastalt,np.shape(expression))
                for x,y in np.ndenumerate(returnarray):
                    returnarray[x]=np.prod(expression[last[x]-1:lastalt[x]])
                return returnarray
            for x,y in np.ndenumerate(returnarray):
                returnarray[x]=np.prod(expression[last[x]-1:lastalt])
            return returnarray
        elif isinstance(lastalt,(list,np.ndarray)):
            for x,y in np.ndenumerate(returnarray):
                if np.shape(lastalt)==np.shape(returnarray):
                    z=x
                else:
                    z=x[len(x)-1-first]            
                returnarray[x]=np.prod(expression[last-1:lastalt[z]])
            return returnarray
        return np.prod(expression[last-1:lastalt],first)          

#     add the variable to the dct so that it's similar to refdct, then do the swap axes
#
# def ramp(self, slope, start, finish):
#     """ Implements vensim's RAMP function """
#     t = self.components._t
#     try:
#         len(start)
#     except:
#         if t<start:
#             return 0
#         elif t>finish:
#             return slope * (start-finish)
#         else:
#             return slope * (t-start)
#     else:
#         returnarray=np.ndarray(len(start))
#         for i in range(len(start)):
#             if np.less(t,start)[i]:
#                 returnarray[i]=0
#             elif np.greater(t,finish)[i]:
#                 try:
#                     len(slope)
#                 except:
#                     returnarray[i]=slope*(start[i]-finish[i])
#                 else:
#                     returnarray[i]=slope[i]*(start[i]-finish[i])
#             else:
#                 try:
#                     len(slope)
#                 except:
#                     returnarray[i]=slope*(t-start[i])
#                 else:
#                     returnarray[i]=slope[i]*(t-start[i])
#         return returnarray

def fifze(p,q,r):
    return np.where(r==0,p,q)

def fifge(p,q,r,s):
    return np.where(r>=s,p,q)

def sclprd(array1,s1,f,array2,s2,s1p='',s2p=''):
    if s1p=='' and s2p=='':
        return np.dot(array1[s1-1:f],array2[s2-1:f])
    elif s1p!='' and s2p=='':
        if isinstance(array2,(list,np.ndarray)):
            if s1p==1:
                array2=array2[s1p-1:f]
            else:
                array2=array2[:,range(s1p-1,f)].transpose()
            return np.dot(array1[s1-1:f],array2)
        else:
            if s1==0:
                array1=array1[f-1:array2].transpose()
            else:
                array1=array1[:,range(f-1,array2)]
            return np.dot(array1,s2[s1p-1:array2])
    else:
        if s1==0:
            array1=array1[f-1:array2].transpose()
        else:
            array1=array1[:,range(f-1,array2)]
        if s1p==1:
            s2=s2[s2p-1:array2].transpose()
        else:
            s2=s2[range(s2p-1,array2)]
        if s1==0 or s1p==1:
            return np.dot(array1,s2).transpose() 
        return np.dot(array1,s2)
    
def smooth(a,b):
    return 1    
    
def prod(*args):
    returnable=1
    for i in args:
        returnable*=i
    return returnable    
    
def initial(name, val, namedict={}, state=[]):
    try:
        namedict[name]
    except:
        namedict[name]=len(namedict)
        state.append("")
    if state[namedict[name]]=="":
        state[namedict[name]]=val
    return state[namedict[name]]

def smooth(expressions,Builder):
    result=[]
    for text,sub in expressions:
        flagsmooth=False
        flagsmoothi=False
        flagsmooth3=False
        flagsmooth3i=False
        smooth=re.findall(r'_smooth_\(',text)
        smoothi=re.findall(r'_smoothi_\(',text)
        smooth3=re.findall(r'_smooth3_\(',text)
        smooth3i=re.findall(r'_smooth3i_\(',text)
        occurrences=range(max(len(smooth),len(smoothi),len(smooth3),len(smooth3i)))
        for i in occurrences:
            for pos,val in enumerate(text):
                if re.match(r'_smooth_\(',text[pos:]):
                    begin=pos
                    flagsmooth=True
                    counter=1
                if re.match(r'_smoothi_\(',text[pos:]):
                    begin=pos
                    flagsmoothi=True
                    counter=1  
                if re.match(r'_smooth3_\(',text[pos:]):
                    begin=pos
                    flagsmooth3=True
                    counter=1  
                if re.match(r'_smooth3i_\(',text[pos:]):
                    begin=pos
                    flagsmooth3i=True
                    counter=1                                            
                if flagsmooth and pos>begin+9:
                    if re.match(r'\(',text[pos:]):
                        counter+=1
                    elif re.match(r'\)',text[pos:]):
                        counter-=1                    
                    if counter==0:
                        end=pos+1
                        smoothing=re.split(r',(?![\w\s\:]*\])',text[begin+9:end-1])
                        text=text.replace(text[begin:end],Builder.add_n_smooth(smoothing[0],smoothing[1],smoothing[0],1,sub)+'()')
                        flagsmooth=False
                        break
                if flagsmoothi and pos>begin+10:
                    if re.match(r'\(',text[pos:]):
                        counter+=1
                    elif re.match(r'\)',text[pos:]):
                        counter-=1                    
                    if counter==0:
                        end=pos+1
                        smoothing=re.split(r',(?![\w\s\:]*\])',text[begin+10:end-1])
                        text=text.replace(text[begin:end],Builder.add_n_smooth(smoothing[0],smoothing[1],smoothing[2],1,sub)+'()')
                        flagsmoothi=False
                        break   
                if flagsmooth3 and pos>begin+10:
                    if re.match(r'\(',text[pos:]):
                        counter+=1
                    elif re.match(r'\)',text[pos:]):
                        counter-=1                    
                    if counter==0:
                        end=pos+1
                        smoothing=re.split(r',(?![\w\s\:]*\])',text[begin+10:end-1])
                        text=text.replace(text[begin:end],Builder.add_n_smooth(smoothing[0],smoothing[1],smoothing[0],3,sub)+'()')
                        flagsmooth3=False
                        break  
                if flagsmooth3i and pos>begin+11:
                    if re.match(r'\(',text[pos:]):
                        counter+=1
                    elif re.match(r'\)',text[pos:]):
                        counter-=1                    
                    if counter==0:
                        end=pos+1
                        smoothing=re.split(r',(?![\w\s\:]*\])',text[begin+11:end-1])
                        text=text.replace(text[begin:end],Builder.add_n_smooth(smoothing[0],smoothing[1],smoothing[2],3,sub)+'()')
                        flagsmooth3i=False
                        break
        result.append((text,sub))
    return result
    
def delay(expressions,Builder):
    result=[]
    for text,sub in expressions:
        flagdelay=False
        flagdelayi=False
        flagdelay3=False
        flagdelay3i=False
        delay=re.findall(r'_delay_\(',text)
        delayi=re.findall(r'_delayi_\(',text)
        delay3=re.findall(r'_delay3_\(',text)
        delay3i=re.findall(r'_delay3i_\(',text)
        occurrences=range(max(len(delay),len(delayi),len(delay3),len(delay3i)))
        for i in occurrences:
            for pos,val in enumerate(text):
                if re.match(r'_delay_\(',text[pos:]):
                    begin=pos
                    flagdelay=True
                    counter=1
                if re.match(r'_delayi_\(',text[pos:]):
                    begin=pos
                    flagdelayi=True
                    counter=1  
                if re.match(r'_delay3_\(',text[pos:]):
                    begin=pos
                    flagdelay3=True
                    counter=1  
                if re.match(r'_delay3i_\(',text[pos:]):
                    begin=pos
                    flagdelay3i=True
                    counter=1                                            
                if flagdelay and pos>begin+8:
                    if re.match(r'\(',text[pos:]):
                        counter+=1
                    elif re.match(r'\)',text[pos:]):
                        counter-=1                    
                    if counter==0:
                        end=pos+1
                        delaying=re.split(r',(?![\w\s\:]*\])',text[begin+8:end-1])
                        text=text.replace(text[begin:end],Builder.add_n_delay(delaying[0],delaying[1],delaying[0],1,sub)+'()')
                        flagdelay=False
                        break
                if flagdelayi and pos>begin+9:
                    if re.match(r'\(',text[pos:]):
                        counter+=1
                    elif re.match(r'\)',text[pos:]):
                        counter-=1                    
                    if counter==0:
                        end=pos+1
                        delaying=re.split(r',(?![\w\s\:]*\])',text[begin+9:end-1])
                        text=text.replace(text[begin:end],Builder.add_n_delay(delaying[0],delaying[1],delaying[2],1,sub)+'()')
                        flagdelayi=False
                        break   
                if flagdelay3 and pos>begin+9:
                    if re.match(r'\(',text[pos:]):
                        counter+=1
                    elif re.match(r'\)',text[pos:]):
                        counter-=1                    
                    if counter==0:
                        end=pos+1
                        delaying=re.split(r',(?![\w\s\:]*\])',text[begin+9:end-1])
                        text=text.replace(text[begin:end],Builder.add_n_delay(delaying[0],delaying[1],delaying[0],3,sub)+'()')
                        flagdelay3=False
                        break  
                if flagdelay3i and pos>begin+10:
                    if re.match(r'\(',text[pos:]):
                        counter+=1
                    elif re.match(r'\)',text[pos:]):
                        counter-=1                    
                    if counter==0:
                        end=pos+1
                        delaying=re.split(r',(?![\w\s\:]*\])',text[begin+10:end-1])
                        text=text.replace(text[begin:end],Builder.add_n_delay(delaying[0],delaying[1],delaying[2],3,sub)+'()')
                        flagdelay3i=False
                        break
        result.append((text,sub))
    return result