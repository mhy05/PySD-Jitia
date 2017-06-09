import numpy as np
  
class namedarray(object):
    def __init__(self, array, shape):    
        self.object = {'array': array, 'shape': shape}

    def shorthander(self, operation, other_object, swapped=False):
        a, b = 'a', 'b'
        if swapped:
            a, b = b, a
        if type(other_object) == int:
            result_vars = {'a': self.object['array'], 'b': other_object}
            result = eval('%(a)s %(op)s %(b)s' % {'a': a,
                                                  'op': operation,
                                                  'b': b},
                          result_vars)
            return namedarray(result,self.object['shape'])
        if len(self.object['shape']) >= len(other_object['shape']):
            result = self.object['array']
            other_numeral = other_object['array']
            dct = other_object['shape'].copy()
            refdct = self.object['shape'].copy()
            copyofref = self.object['shape'].copy()
        else:
            result = other_object['array']
            other_numeral = self.object['array']
            dct = self.object['shape'].copy()
            refdct = other_object['shape'].copy()
            copyofref = other_object['shape'].copy()
            a, b = b, a

        difference = abs(len(refdct) - len(dct))

        for key, val in dct.iteritems():
            result = np.swapaxes(result, copyofref[key], val + difference)
            copyofref[copyofref.keys()[copyofref.values().index(val + difference)]] = copyofref[key]
            copyofref[key] = val + difference

        # Perform Operation Here Before Returning to Normal Shape
        result_vars = {'a': result, 'b': other_numeral}
        result = eval('%(a)s %(op)s %(b)s' % {'a': a,
                                              'op': operation,
                                              'b': b},
                      result_vars)
        ########################################################

        for val in sorted(refdct.itervalues()):
            key = refdct.keys()[refdct.values().index(val)]
            result = np.swapaxes(result, copyofref[key], val)
            copyofref[copyofref.keys()[copyofref.values().index(val)]] = copyofref[key]
            copyofref[key] = val
        return namedarray(result,refdct)

    def __add__(self, other_object):
        return self.shorthander('+', other_object)

    def __radd__(self, other_object):
        return self.shorthander('+', other_object, True)

    def __sub__(self, other_object):
        return self.shorthander('-', other_object)

    def __rsub__(self, other_object):
        return self.shorthander('-', other_object, True)

    def __mul__(self, other_object):
        return self.shorthander('*', other_object)

    def __rmul__(self, other_object):
        return self.shorthander('*', other_object, True)

    def __div__(self, other_object):
        return self.shorthander('/', other_object)

    def __rdiv__(self, other_object):
        return self.shorthander('/', other_object, True)

    def __neg__(self):
        return self.shorthander('*', -1)

    def __pos__(self):
        return self

    def __repr__(self):
        return repr(self.object['array'])

    def __getitem__(self, rhs):
        if rhs in ['array', 'shape']:
            return self.object[rhs]
        if isinstance(rhs,tuple):
            temp=list(rhs)
        else:
            temp=[rhs]
        shape={}
        roll=0
        for y in sorted(self.object['shape'].values()):
            x=self.object['shape'].keys()[self.object['shape'].values().index(y)]
            try:
                if isinstance(temp[y],int):
                    roll-=1
                    continue
            except:
                pass
            shape[x]=y+roll
        return namedarray(self.object['array'][rhs],shape)

    def __setitem__(self, rhs, value):
        dummyarray = namedarray(0,{})
        self.object['array'][rhs] = (namedarray(self.object['array'],self.object['shape']) * dummyarray + value)['array'][rhs]


class NamedArrayException(Exception):
    pass