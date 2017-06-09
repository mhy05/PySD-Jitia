from pysd import builder
import numpy as np
import re
import os
import pysd

def doc_supported_jitia_functions():
    """prints a list of all of the vensim functions that are supported
    by the translator.
    """
    rowline     = '+------------------------------+------------------------------+\n'
    headers     = '|            Jitia             |       Python Translation     |\n'
    underline   = '+==============================+==============================+\n'
    string = rowline + headers + underline
    for key, value in dictionary.iteritems():
        string += '|'   + key.center(30) +  '|'  + value.center(30) + '|\n'
        string += rowline
    for item in construction_functions:
        string += '|'   + item.center(30) + '|      Model Construction      |\n'
        string += rowline

    string += '\n `np` corresponds to the numpy package'

    return string


def translate_jitia(mdl_file):
    """
    Translate a jitia model file into a python class.

    Supported functionality:\n\n"""
    # model=mdl_file.replace('.dyn','.py')
    # builder.Builder(model,dictofsubs)
    
    f1 = open(mdl_file, 'r')
    f1=' '.join(f1)
    f1=re.sub(r'(MACRO(.|\n)*MEND)*','',f1)
    
    f2=re.findall(r'([A-Z]+ [^\n]*(\n    [^\n]*)*)',f1)
    for i,j in enumerate(f2):
        f2[i]=j[0]

    f3=[]
    for i in f2:
        f3.append(i.split('\n      '))
    exceptions=('FOR  ','N TIME=','SPEC','SAVE')
    symbols=r'(\,|\^|\(|\)|\[|\]|\=|\<|\>|(?<![0-9]e)\+(?![0-9])|(?<![0-9]e)\-(?![0-9])|(?<=[0-9])\+(?=[0-9])|(?<=[0-9])\-(?=[0-9])|\*|\/)'
    numbers=r'(?i)((\+|\-)*(?<!([a-zA-Z]|[0-9]|\_))([0-9]*\.?[0-9]+(e(\+|\-)?[0-9]*)*)(?!([a-zA-Z]|[0-9]|\_)))'
    functions=['MAX','MIN','POS','IF','THEN','ELSE','AND','OR','SUM','SUMV','SAMPLE','TABLE',
            'STEP','WEIGHT','TUNER','TUN','FIFZE','FIFGE','DELAY3M','DATAOFF','SCLPRD',
            'FAVAIL','PRDV','TUNE1','DATAOO','SMOOTH','DELAY','SUPPOS','AVVAL','SUPPOS','TABHL'] 
    functiondic={'MISSING()':'0','MAX':'np.maximum','MIN':'np.minimum','SUM':'np.sum','if_then_else':'np.where','SUMV':'functions.sumv',
                'ABS':'abs', 'INTEGER':'int', 'EXP':'np.exp','PI':'np.pi', 'SIN':'np.sin', 'COS':'np.cos', 'SQRT':'np.sqrt', 
                'TAN':'np.tan','LOGNORMAL':'np.random.lognormal', 'RANDOM NORMAL':'functions.bounded_normal','POISSON':'np.random.poisson',
                'LN':'np.log', 'EXPRND':'np.random.exponential','RANDOM UNIFORM':'np.random.rand','ARCCOS':'np.arccos','ARCSIN':'np.arcsin',
                'ARCTAN':'np.arctan','STEP':'functions.step', 'MODULO':'np.mod', 'PULSE':'functions.pulse','PULSE TRAIN':'functions.pulse_train', 
                'RAMP':'functions.ramp', 'FIFZE':'functions.fifze', 'FIFGE':'functions.fifge','SCLPRD':'functions.sclprd', 'PRDV':'functions.prdv',
                'SMOOTH3I':'_smooth3i_','SMOOTH3':'_smooth3_','SMOOTHI':'_smoothi_','SMOOTH':'_smooth_','LOGN':'np.log', 'ROUND':'np.round',
                'DELAY3I':'_delay3i_','DELAY3':'_delay3_','DELAY1I':'_delayi_','DELAY1':'_delay_','DELAYI':'_delayi_','DELAY':'_delay_',
                'FLOOR':'np.floor','VECTORMIN':'np.min','VECTORMAX':'np.max','PROD':'np.prod','TABHL':'functions.tabhl'}
    
    functiondiccase='('+'|'.join(functiondic)+')'                
    
    def unique(seq):
        Set = set(seq)
        return list(Set)

    checking=[]
    subscripts=[]
    for variable in f3:
        if variable[0].startswith('FOR  '):
            checking.append(''.join(variable).split('  ',1)[-1])
            subscripts.append(''.join(variable).split('  ',1)[-1])
        elif variable[0].startswith('SAVE '):
            checking.append(''.join(variable).split(' ',1)[-1])
        else:
            checking.append(','.join(re.findall(r'((?<=[A-Z] )[^\=]*(?=\=))',variable[0])))
    checking.append(','.join(functions))
    checking.append(','.join(functiondic.keys()))
    checking=' '.join(checking)
    checking=re.sub(r'(\,|\=|\^|\(|\))',' ',checking)
    checking=checking.split(' ')
    checking=filter(None,checking)
    checking=unique(checking)
    checking='|'.join(checking)
    checking='(?i)^('+re.sub(r'(%s|%s)'%(symbols,numbers),'',checking).replace('||','|')+')$'
    subscripts=','.join(subscripts)
    subscripts=re.sub('\^','',subscripts)
    subscripts=re.sub('=',',',subscripts)
    subscripts=subscripts.split(',')
    subscripts.append('\*')
    subscripts=filter(None,subscripts)
    # for i,j in enumerate(subscripts):
    #     if re.search(r'\d+\-\d+',j):
    #         subscripts[i]=''
    #         j=j.split('-')
    #         for k in range(int(j[0]),int(j[1])):
    #              subscripts[i]+=str(k)+'|'
    #         subscripts[i].strip('|')
    subs=r'(?i)('+'|'.join(subscripts)+')'
    # subs = re.sub('(\d+)-(\d+)',lambda s:'|'.join(['%s'%x for x in range(int(s.group(1)),int(s.group(2))+1)]),subs)
    for position,variable in enumerate(f3):
        for j in range(len(variable)):
            if not variable[-1].endswith(' ') and not variable[0].startswith(exceptions):
                variable.pop(-1)
            else: break               
        for counter,value in enumerate(variable):
            value=re.sub(symbols,' ',value)
            value=re.sub(numbers,' ',value)
            value=re.sub('\s+',' ',value)
            value=value.split(' ')
            if counter!=0:
                if len(variable[counter])<40 and variable[counter][-1]!='^':                
                    variable[counter+1:]=''
                if not re.search('(\d|\=|\>|\<|\+|\-|\*|\/|\(|\)|\[|\]|\:|\,)',
                                variable[counter]) and len(variable[counter])>55:                                
                    variable[counter:]=''                    
                for word in value:
                    if not re.search(checking,word) and word!='' and not re.search(r'(?i)(else|then)',word):
                        variable[counter:]=''
                        break
        for j in range(len(variable)):
            if not variable[-1].endswith(' ') and not variable[0].startswith(exceptions) and variable[0]!=variable[-1]:            
                variable.pop(-1)            
            else: break
        
        f3[position]=''.join(variable).strip().replace('^',' ').replace('\n',' ')
        f3[position]=re.sub(r'^(.*?)\((.*?)\)(\=)',r'\1[\2]\3',f3[position])
        f3[position]=re.sub('\((?=%s\s*(\,|\)))'%subs,'[',f3[position])
        f3[position]=re.sub(r'(\[%s\s*(\,\s*%s)*\s*)\)'%(subs,subs), r'\1]', f3[position])
        # if re.match('(?i)\w *c school duration',f3[position]):
        #     print f3[position]
        f3[position]=re.sub(r'(?i)(%s)'%functiondiccase,lambda s:s.group(1).upper(),f3[position])
        # if f3[position].startswith('N  LKNPE'):
        #     print f3[position]
    auxiliaries=[]
    levels=[]
    tables=[]
    initials=[]
    subscripts=[]

    for variable in f3:
        if variable.startswith('FOR  '):
            subscripts.append(variable.split('  ',1)[-1])
        elif variable.startswith(('A  ','C  ','R  ')):
            auxiliaries.append(variable.split('  ',1)[-1])
        elif variable.startswith('SPEC '):
            auxiliaries.append(variable.split(' ',1)[-1])
        elif variable.startswith('L  '):
            levels.append(variable.split('  ',1)[-1])
        elif variable.startswith('T  '):
            tables.append(variable.split('  ',1)[-1])
        elif variable.startswith('N '):
            if variable.startswith('N TIME'):
                variable=variable.replace('TIME',' INITIAL TIME')
            initials.append(variable.split('  ',1)[-1])
    dictofsubs = {} 
    for i in subscripts: 
        Family=builder.make_python_identifier(i.split("=")[0]) 
        if not re.search('-',i):
            Elements=i.split("=")[1].split(",") 
            for i in range(len(Elements)): 
                Elements[i]=builder.make_python_identifier(Elements[i].strip()) 
            dictofsubs[Family]=dict(zip(Elements,range(len(Elements)))) 
        elif not re.search(r'[a-zA-Z]',i.split('=')[1]):
            Elements=i.split("=")[1].split("-")
            Elements=range(int(Elements[0]),int(Elements[1])+1)
            for i,j in enumerate(Elements):
                Elements[i]=str(j)
            dictofsubs[Family]=dict(zip(Elements,range(len(Elements)))) 
        elif re.search('-',i.split('=')[1]):
            Elements=i.split('=')[1]
            dictofsubs[Family]=re.sub(r'([\w\s]+)',
                                    lambda s: builder.make_python_identifier(s.group(1)),Elements)    
        for subfamily in dictofsubs:
            if isinstance(dictofsubs[subfamily],str):
                fromelem=dictofsubs[subfamily].split('-')[0]
                toelem=dictofsubs[subfamily].split('-')[1]
                for family in dictofsubs:
                    if fromelem in dictofsubs[family] and toelem in dictofsubs[family] and isinstance(dictofsubs[family],dict):
                        dictofsubs[subfamily]=range(dictofsubs[family][fromelem],dictofsubs[family][toelem]+1)
                        dictofsubs[subfamily].append(family)                                      
    def getelempos(allelements): 
        getelempos.sumfor=''
        position=[]     
        elements=allelements.replace(' ', '').split(',') 
        for pos,element in enumerate(elements): 
            if element in dictofsubs.keys():
                if isinstance(dictofsubs[element],dict):            
                    position.append(':') 
                else:
                    position.append(sorted(dictofsubs[element][:-1]))
            else: 
                if element=='*':
                    position.append(':')
                    if len(position)==1 or (position[-2]==':' and len(position)>1):
                        sumat=pos
                    else:
                        sumat=pos-1
                    getelempos.sumfor=','+str(sumat)
                for d in dictofsubs.itervalues(): 
                    try: 
                        position.append(d[element]) 
                    except: pass 
        if len(re.findall(r'\*',allelements))>1:
            getelempos.sumfor=''
        return tuple(position)
    getelempos.sumfor=''
    
    def getnumofelements(element):
        """

        Parameters
        ----------
        element <string of subscripts>

        returns a list of the sizes of the dimensions. A 4x3x6 array would return
        [4,3,6]

        """
        # todo: make this elementstr or something
        if element=='':# or ("subscript_"+element) in subscripts:
            return 0
        position=[]
        elements=element.replace('!','').replace('','').split(',')
        for element in elements:
            if element in dictofsubs.keys():
                if isinstance(dictofsubs[element],list):
                    position.append((getnumofelements(dictofsubs[element][-1]))[0])
                else:
                    position.append(len(dictofsubs[element]))
            else:
                if element=='*':
                    position.append(1)
                for d in dictofsubs.itervalues():
                    try:
                        (d[element])
                    except: pass
                    else:
                        position.append(len(d))

        return position
    pysd.builder.dictofsubs=dictofsubs
    pysd.builder.getelempos=getelempos
    pysd.builder.getnumofelements=getnumofelements
     
#######################################################
    new_model=mdl_file.replace('.dyn','.py')
    Builder=builder.Builder(new_model,dictofsubs)
    macrolist=macroextractor(mdl_file)
#######################################################                                           
    lookups=[]    
    for line in tables:
        line=re.findall(r'([^\[\=]*)(\[([^\]]*)\])?\=(.*)',line)[0]
        identifier=builder.make_python_identifier(line[0])
        sub=re.sub(r'([^\[\]\(\)\+\-\*\/\,\.]+)',
                        lambda s: builder.make_python_identifier(s.group(1))if not re.match('\d*$',s.group(1)) else s.group(1), line[2])
        expression=line[3].split(',')
        # if line[0].startswith('Data Table for Inventory by LOS and Rank'):
        #     print sub,identifier
        copairlist=[]
        for i in range(len(expression)/2):
            copair=(expression[2*i],expression[2*i+1])
            copairlist.append(copair)
        lookups.append([identifier,[sub],[copairlist]])
    for pos1,value1 in enumerate(lookups):
        for pos2,value2 in enumerate(lookups):
            if pos1!=pos2:
                try: 
                    if value1[0]==value2[0]:
                        lookups[pos1][1]+=value2[1]
                        lookups[pos1][2]+=value2[2]
                        lookups[pos2]=''
                except: pass
    lookups=filter(None,lookups)
    lookuptofix=[]
    for line in lookups:
        lookuptofix.append(line[0])
        try:
            Builder.add_lookup(line[0],'',line[1],line[2])
        except Exception as e:
            print line[0]
            print e
    lookuptofix='(?i)('+'|'.join(lookuptofix)+')\(\)\[*[^\]\(]*\]*\('
    stocks=[]
    init_val=[]                
    for line in levels:
        line=re.findall(r'([^\[\=]*)(\[([^\]]*)\])?\=.*?\+DT\*\((.*)\)',line)[0]
        identifier=builder.make_python_identifier(line[0])
        sub=re.sub(r'([^\[\]\(\)\+\-\*\/\,\.]+)',
                        lambda s: builder.make_python_identifier(s.group(1)), line[2])
        expression=formatexpression(line[3],identifier,functiondic,macrolist)                                           
        expression=re.sub(r'\[([^\]]*)\]',
                        lambda s: '[' + ','.join(map(str,getelempos(s.group(1).replace('()',''))))+']'+getelempos.sumfor, expression)
        expression=re.sub(r'\,(%s\(\))\)'%subs,
                        lambda s: ','+','.join(map(str,getnumofelements(s.group(1).replace('()',''))))+')', expression)
        expression=re.sub(r'%s'%lookuptofix,r'\1(',expression)
        subinexpression='[' + ','.join(map(str,getelempos(sub)))+']'
        expression=re.sub(r'(?<!\(|\w|,)(\w+)\(\)\[\:(\,\:)*\]',r'functions.shorthander(\1(),\1.dimension_dir,loc_dimension_dir,_subscript_dict)'+subinexpression,expression.replace(' ',''))
        stocks.append([identifier,[sub],[expression],[],[]])
    for line in initials:
        line=re.findall(r'([^\[\=]*)(\[([^\]]*)\])?\=(.*)',line)[0]
        identifier=builder.make_python_identifier(line[0])        
        sub=re.sub(r'([^\[\]\(\)\+\-\*\/\,\.]+)',
                        lambda s: builder.make_python_identifier(s.group(1)), line[2])
        expression=formatexpression(line[3],identifier,functiondic,macrolist)                                     
        expression=re.sub(r'\[([^\]]*)\]',
                        lambda s: '[' + ','.join(map(str,getelempos(s.group(1).replace('()',''))))+']'+getelempos.sumfor, expression)        
        expression=re.sub(r'\,(%s\(\))\)'%subs,
                        lambda s: ','+','.join(map(str,getnumofelements(s.group(1).replace('()',''))))+')', expression)       
        expression=re.sub(r'%s'%lookuptofix,r'\1(',expression)       
        subinexpression='[' + ','.join(map(str,getelempos(sub)))+']'
        if not re.search(r'(np.sum|functions.sumv|functions.prdv|functions.sclprd|smooth|delay|functions.tabhl)',expression):
            expression=re.sub(r'(\w+)\(\)\[\:(\,\:)*\]',r'functions.shorthander(\1(),\1.dimension_dir,loc_dimension_dir,_subscript_dict)'+subinexpression,expression.replace(' ',''))        
            # expression=re.sub(r'((?<!(\w|\[|\]|\+|\-|\.))[\d\.]+(?!(\w|\[|\]|\+|\-|\.)))',lambda s: s.group(1) if re.search(r'\.',s.group(1)) else s.group(1)+'.0',expression)
        init_val.append([identifier,[sub],[expression]])  
    for pos1,value1 in enumerate(stocks):
        for pos2,value2 in enumerate(stocks):
            if pos1!=pos2:
                try: 
                    if value1[0]==value2[0]:
                        stocks[pos1][1]+=value2[1]
                        stocks[pos1][2]+=value2[2]
                        stocks[pos2]=''
                except: pass
    stocks=filter(None,stocks)
    for pos1,value1 in enumerate(stocks):
        for pos2,value2 in enumerate(init_val):
            try: 
                if value1[0]==value2[0]:
                    stocks[pos1][3]+=value2[1]
                    stocks[pos1][4]+=value2[2]
                    init_val[pos2]=''
            except: pass
    init_val=filter(None,init_val)
    
    for line in stocks:
        try:
            Builder.add_stock(line[0],line[1],line[2],line[4],line[3])
        except:
            print line[0]

    flaux=[]
    for line in auxiliaries:
        line=re.findall(r'([^\[\=]*)(\[([^\]]*)\])?\=(.*)',line)[0]
        identifier=builder.make_python_identifier(line[0])
        sub=re.sub(r'([^\[\]\(\)\+\-\*\/\,\.]+)',
                        lambda s: builder.make_python_identifier(s.group(1)), line[2])  
        
        expression=formatexpression(line[3],identifier,functiondic,macrolist)
        expression=re.sub(r'\[([^\]]*)\]',
                        lambda s: '[' + ','.join(map(str,getelempos(s.group(1).replace('()',''))))+']'+getelempos.sumfor, expression)                          
        expression=re.sub(r'(\,(\w*)\(\)([\,\)]))',
                        lambda s: ','+','.join(map(str,getnumofelements(s.group(2))))+s.group(3) if s.group(2) in dictofsubs.keys() else s.group(1), expression)        
        expression=re.sub(r'(?<!\w)%s'%lookuptofix,r'\1(',expression)
        subinexpression='[' + ','.join(map(str,getelempos(sub)))+']'
        if not re.search(r'(np.sum|functions.sumv|functions.prdv|functions.sclprd|smooth|delay|functions.tabhl)',expression):
            expression=re.sub(r'(\w+)\(\)\[\:(\,\:)*\]',r'functions.shorthander(\1(),\1.dimension_dir,loc_dimension_dir,_subscript_dict)'+subinexpression,expression.replace(' ',''))        
            # expression=re.sub(r'((?<!(\w|\[|\]|\+|\-|\.))[\d\.]+(?!(\w|\[|\]|\+|\-|\.)))',lambda s: s.group(1) if re.search(r'\.',s.group(1)) else s.group(1)+'.0',expression)      
        expression=smooth(expression,[sub],Builder)
        expression=delay(expression,[sub],Builder)
        # if len(re.findall(r'(?<!\,|\[)[\+\-\*\/]',expression))!=len(re.findall(r'(?<!\,|\[)[\+\-\*\/]',line[3])):
        #     print identifier
        flaux.append([identifier,[sub],[expression]])
    for pos,line_init in enumerate(init_val):
        for line_aux in flaux:
            if line_init[0]==line_aux[0]:
                init_val[pos][0]='_init_'+line_init[0]
        # init_val[pos][2]=['functions.initial("%s",'%(line_init[0]+line_init[1][0])+line_init[2][0]+')']
    flaux=flaux+init_val
    for pos1,value1 in enumerate(flaux):
        for pos2,value2 in enumerate(flaux):
            if pos1!=pos2:
                try: 
                    if value1[0]==value2[0]:
                        flaux[pos1][1]+=value2[1]
                        flaux[pos1][2]+=value2[2]
                        flaux[pos2]=''
                except: pass
    flaux=filter(None,flaux)
    for line in flaux:
        Builder.add_flaux(line[0],line[1],line[2])


    Builder.write()
    macros(mdl_file,checking,functiondic)
    return new_model
           
translate_jitia.__doc__ += ''

def macros(mdl_file,checking,functiondic):
    macros = open(mdl_file, 'r')
    macros=' '.join(macros)
    new_model=mdl_file.replace('.dyn','.py')
    macros=re.findall(r'(MACRO(.|\n)*?MEND)',macros)
    for i,j in enumerate(macros):
        macros[i]=j[0]
        
    def add_flaux(filename, identifier, expression, doc=''):
        expression = re.sub(r'@(.*?)@',lambda s: s.group(1).replace('_element()',''),expression[0])
        docstring = ('Type: Flow or Auxiliary\n        '+
                    '\n        '.join(doc.split('\n')))

        funcstr = ('    def %s():\n'%identifier +
                '        """%s"""\n'%docstring +
                '        return %s \n\n'%expression)

        with open(filename, 'a') as outfile:
            outfile.write(funcstr)

        return 'self.%s()'%identifier

    def add_stock(filename, identifier, expression, initial_condition):
        expression=expression[0]
        initial_condition=initial_condition[0]
        dfuncstr = ('    def d%s_dt():                       \n'%identifier +
                    '        return %s                           \n\n'%expression
                )
        ifuncstr = ('    def %s_init():                      \n'%identifier +
                    '        return %s                           \n\n'%initial_condition
                )
        sfuncstr = ('    def %s():                            \n'%identifier +
                    '        """ Stock: %s =                      \n'%identifier +
                    '                 %s                          \n'%expression +
                    '                                             \n' +
                    '        Initial Value: %s                    \n'%initial_condition +
                    '        Do not overwrite this function       \n' +
                    '        """                                  \n' +
                    '        return %s_state[namedict[name]]      \n'%identifier +
                    '                                             \n'
                )
        with open(filename, 'a') as outfile:
            outfile.write(dfuncstr)
            outfile.write(ifuncstr)
            outfile.write(sfuncstr)
            
    symbols=r'(\,|\^|\(|\)|\[|\]|\=|\<|\>|(?<!e)\+(?![0-9])|(?<!e)\-(?![0-9])|(?<=[0-9])\+(?=[0-9])|(?<=[0-9])\-(?=[0-9])|\*|\/)'
    numbers=r'(?i)((\+|\-)*(?<!([a-zA-Z]|[0-9]|\_))([0-9]*\.?[0-9]+(e(\+|\-)[0-9]*)*)(?!([a-zA-Z]|[0-9]|\_)))'
    function=['MAX','MIN','IF','THEN','ELSE','AND','OR','SUM','SUMV','TABLE',
        'STEP','FIFZE','FIFGE','SCLPRD','PRDV','SMOOTH','AVVAL','SUPPOS','TABHL']         
    
    for value in macros:
        macrolist=[]    
        macro=re.findall(r'([A-Z]+ [^\n]*(\n  [^\n]*)*)',value.replace('$',''))
        for i,j in enumerate(macro):
            macro[i]=j[0]
        for value in macro:
            macrolist.append(value.replace('^\n',' ').split('\n'))
        for position,variable in enumerate(macrolist):
            for j in range(len(variable)):
                if not variable[-1].endswith(' ') and not variable[0].startswith('MACRO') and not len(variable)==1:
                    variable.pop(-1)
                else: break
            for counter,value in enumerate(variable):
                value=re.sub(symbols,' ',value)
                value=re.sub(numbers,' ',value)
                value=re.sub('\s+',' ',value)
                value=value.split(' ')
                if len(variable[counter])<45:
                    variable[counter+1:]=''
                if counter!=0:
                    if not re.search('(\d|\=|\>|\<|\+|\-|\*|\/|\(|\)|\,)',
                                    variable[counter]) and len(variable[counter])>55:
                        variable[counter:]=''
                    for word in value:
                        if not re.search(checking,word) and word!='' and not re.search(r'(?i)(else|then)',word):
                            if counter==1:
                                if len(re.findall(r'\(',variable[counter-1]))!=len(re.findall(r'\)',variable[counter-1])):
                                    break
                            if re.search(r'(?i)(if|then|else) *$',variable[counter-1]):
                                break
                            variable[counter:]=''
                            break
            for j in range(len(variable)):
                if not variable[-1].endswith(' ') and not variable[0].startswith('MACRO') and not len(variable)==1:
                    variable.pop(-1)
                else: break
            macrolist[position]=''.join(variable).strip().replace('^','')
        auxiliaries=[]
        levels=[]
        tables=[]
        initials=[]
        for variable in macrolist:
            if variable.startswith('MACRO'):
                macrodef=variable.split(' ',1)[-1]
            elif variable.startswith(('A  ','C  ','R  ')):
                auxiliaries.append(variable.split('  ',1)[-1])
            elif variable.startswith('SPEC '):
                auxiliaries.append(variable.split(' ',1)[-1])
            elif variable.startswith('L  '):
                levels.append(variable.split('  ',1)[-1])
            elif variable.startswith('T  '):
                tables.append(variable.split('  ',1)[-1])
            elif variable.startswith('N '):
                initials.append(variable.split('  ',1)[-1])
    ######################################################################################
        inter=re.findall(r'\(.*\)',macrodef)[0].replace('(','').replace(')','').split(',')
        for val in inter:
            function.append(val)
        listofmacros=macroextractor(mdl_file)
        macrodef=re.sub(r'((?<![0-9])[a-zA-Z][^\[\]\(\)\+\-\*\/\,\.\=\>\<\@]+)',
                            lambda s: pysd.builder.make_python_identifier(s.group(1)), macrodef)
        stocks=[]
        init_val=[]
        for line in levels:
            line=re.findall(r'([^\[\=]*)(\[([^\]]*)\])?\=.*?\+DT\*\((.*)\)',line)[0]
            identifier=pysd.builder.make_python_identifier(line[0])
            sub=re.sub(r'([^\[\]\(\)\d\+\-\*\/\,\.]+)',
                            lambda s: pysd.builder.make_python_identifier(s.group(1)), line[2])
            expression=formatexpression(line[3],identifier,functiondic,listofmacros,function)
            stocks.append([identifier,[sub],[expression],[],[]])
        for line in initials:
            line=re.findall(r'([^\[\=]*)(\[([^\]]*)\])?\=(.*)',line)[0]
            identifier=pysd.builder.make_python_identifier(line[0])
            sub=re.sub(r'([^\[\]\(\)\d\+\-\*\/\,\.]+)',
                            lambda s: pysd.builder.make_python_identifier(s.group(1)), line[2])
            expression=formatexpression(line[3],identifier,functiondic,listofmacros,function)           
            init_val.append([identifier,[sub],[expression]])  
        for pos1,value1 in enumerate(stocks):
            for pos2,value2 in enumerate(stocks):
                if pos1!=pos2:
                    try: 
                        if value1[0]==value2[0]:
                            stocks[pos1][1]+=value2[1]
                            stocks[pos1][2]+=value2[2]
                            stocks[pos2]=''
                    except: pass
        stocks=filter(None,stocks)
        for pos1,value1 in enumerate(stocks):
            for pos2,value2 in enumerate(init_val):
                try: 
                    if value1[0]==value2[0]:
                        stocks[pos1][3]+=value2[1]
                        stocks[pos1][4]+=value2[2]
                        init_val[pos2]=''
                except: pass
        init_val=filter(None,init_val)
        macrodefadd=',namedict={}'
        stateinit=''
        statedt=''
        for line in stocks:
            macrodefadd+=','+line[0]+'_state=[]'
            stateinit+='        '+line[0]+'_state.append("")\n'
            statedt+=('    if '+line[0]+'_state[namedict[name]]=="":\n'+
                    '        '+line[0]+'_state[namedict[name]]='+line[0]+'_init()\n'+
                    '    else:\n'+
                    '        '+line[0]+'_state[namedict[name]]+=d'+line[0]+'_dt()\n')
        with open(new_model, 'a') as outfile:
            outfile.write('def '+re.sub(r'\((.*)\)',r'(name,\1'+macrodefadd+'):\n\n',macrodef))
        for line in stocks:
            try:
                add_stock(new_model,line[0],line[2],line[4])
            except:
                pass
        flaux=init_val
        for line in auxiliaries:
            line=re.findall(r'([^\[\=]*)(\[([^\]]*)\])?\=(.*)',line)[0]
            identifier=pysd.builder.make_python_identifier(line[0])
            sub=re.sub(r'([^\[\]\(\)\d\+\-\*\/\,\.]+)',
                            lambda s: pysd.builder.make_python_identifier(s.group(1)), line[2])
            expression=formatexpression(line[3],identifier,functiondic,listofmacros,function)
            flaux.append([identifier,[sub],[expression]])
        for pos1,value1 in enumerate(flaux):
            for pos2,value2 in enumerate(flaux):
                if pos1!=pos2:
                    try: 
                        if value1[0]==value2[0]:
                            flaux[pos1][1]+=value2[1]
                            flaux[pos1][2]+=value2[2]
                            flaux[pos2]=''
                    except: pass
        flaux=filter(None,flaux)
        for line in flaux:
            add_flaux(new_model,line[0],line[2])
        lookups=[]
        for line in tables:
            line=re.findall(r'([^\[\=]*)(\[([^\]]*)\])?\=(.*)',line)[0]
            identifier=pysd.builder.make_python_identifier(line[0])
            sub=re.sub(r'([^\[\]\(\)\d\+\-\*\/\,\.]+)',
                            lambda s: pysd.builder.make_python_identifier(s.group(1)), line[2])
            expression=line[3].split(',')
            copairlist=[]
            for i in range(len(expression)/2):
                copair=(expression[2*i],expression[2*i+1])
                copairlist.append(copair)
            lookups.append([identifier,[sub],[copairlist]])
        for pos1,value1 in enumerate(lookups):
            for pos2,value2 in enumerate(lookups):
                if pos1!=pos2:
                    try: 
                        if value1[0]==value2[0]:
                            lookups[pos1][1]+=value2[1]
                            lookups[pos1][2]+=value2[2]
                            lookups[pos2]=''
                    except: pass
        lookups=filter(None,lookups)
        for line in lookups:
            try:
                add_lookup(new_model,line[0],'',line[1],line[2])
            except:
                pass
        levelcalc=('    try:\n'+
                '        namedict[name]\n'+
                '    except:\n'+
                '        namedict[name]=len(namedict)\n'+
                stateinit+
                statedt+
                '    return '+re.sub(r'\(.*\)','()\n\n',macrodef))
        with open(new_model, 'a') as outfile:
            outfile.write(levelcalc)

# def ifthel(string):
#     def ifthenelse(strings,state=0,func=['','','']):
#         if state==0:
#             matchstr='then'
#         elif state==1:
#             matchstr='else'
#         else:
#             matchstr=chr(1)
#         if len(strings)<=1 or state==2 and re.match(r'(?i)else',strings[1:]):
#             if func[state][-1]!='}':
#                 func[state]+=strings[0]
#             return '{'+','.join(func)+'}'        
#         else:
#             if re.match(r'(?i)%s'%matchstr,strings[1:]):
#                 if func[state][-1]!='}':
#                     func[state]+=strings[0]
#                 return ifthenelse(strings[1:],state+1,func)
#             elif (re.match(r'(?<![a-zA-Z])(?i)if ',strings[1:]) ) and re.search(r'(?i)if.*then.*else',strings[1:]):
#                 func[state]+=strings[0]
#                 temp=ifthenelse(strings[1:],0,['','',''])
#                 func[state]+=temp
#                 return ifthenelse(strings[(-4)*len(re.findall('\{',temp))+
#                                          len(temp):],state,func)
#             else:
#                 func[state]+=strings[0]
#                 return ifthenelse(strings[1:],state,func)
#     return re.sub(r'(?<!(<|>|!))=','==',
#                   re.sub(r'(?<=(\(|\,))(?i)(if|then|else)','',
#                          ifthenelse(string,0,['','',''])
#                          .replace('{','if_then_else(')
#                          .replace('}',')')
#                          .replace('<>','!=')))
                        
def ifthel(string):
    string = string.replace('\n',' ')
    strip = string
    if re.search('(?i)(?<!\w)if .*then.*else',strip):
        while(re.search('(?i)(?<!\w)if .*then.*else.*',strip)):
            strip = re.findall('(?i)if(.*)',strip)[-1]
        strip = re.match('(?i)((.*)then(.*?)else(.*?))(then|else|$)',strip).groups()[:-1]
        return ifthel(string.replace(strip[0],'{%s,%s,%s}'%(strip[1],strip[2],strip[3])))
    else:
        return re.sub('(?<![\<\>])=','==',re.sub('(?i)if{','if_then_else(',string).replace('}',')')).replace('<>','!=')                                            
                        
def macroextractor(mdl_file):
    macros = open(mdl_file, 'r')
    macros=' '.join(macros)
    macros=re.findall(r'MACRO.*',macros)
    for position,variable in enumerate(macros):
        macros[position]=pysd.builder.make_python_identifier(re.findall('MACRO ([^\(\=]*)',variable)[0])
    return '|'.join(macros)

def formatexpression(line,identifier,functiondic,listofmacros,function=['']):
    expression=re.sub(r'\s+',' ',line)
    expression=re.sub(r'(?i)(if.*?[\<\>\=].*?\s)(AND|OR)(\s.*?[\<\>\=].*?then)',
                    r'\1@\2@\3',expression)
    if re.search(r'(?i)if.*then.*else',expression):
        expression=ifthel(expression)        
    expression=re.sub(r'((?<![0-9])[a-zA-Z][^\[\]\(\)\+\-\*\/\,\.\=\>\<\@]+)',
                    (lambda s: functiondic[s.group(1)] if s.group(1) in functiondic 
                    else pysd.builder.make_python_identifier(s.group(1)) if s.group(1) in function and len(function)!=1
                    else pysd.builder.make_python_identifier(s.group(1))+'()'),
                    expression).replace('step(','step(time(),') 
    expression=re.sub(r'(?<!\w)(%s)\(\)\('%listofmacros,r'\1("%s",'%identifier,expression)
    # expression=re.sub(r'\[([^\]]*)\(\)\]',
    #                 lambda s: '[' + ','.join(map(str,getelempos(s.group(1).replace('()',''))))+']', expression)
    return expression                   

def getsubs(mdl_file):
    f1 = open(mdl_file, 'r')
    f1=' '.join(f1)
    f1=re.sub(r'(MACRO(.|\n)*MEND)*','',f1)
    
    f2=re.findall(r'([A-Z]+ [^\n]*(\n    [^\n]*)*)',f1)
    for i,j in enumerate(f2):
        f2[i]=j[0]

    f3=[]
    for i in f2:
        f3.append(i.split('\n      '))
            
    subscripts=[]
    for variable in f3:
        if variable[0].startswith('FOR  '):
            subscripts.append(''.join(variable).replace('^','').split('  ',1)[-1])
    subscripts=filter(None,subscripts)
    return subscripts
    
def smooth(text,sub,Builder):
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
    return text
    
def delay(text,sub,Builder):
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
    return text    