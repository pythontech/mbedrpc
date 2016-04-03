#=======================================================================
#       Alternative, nore pythonic interface to RPC on mbed
#=======================================================================
import serial

debug = True

class RPCClient(object):
    def __init__(self):
        self._objmap = {}

    def keys(self):
        """List all objects and classes."""
        return self.rpcl('','')

    def __getitem__(self, name):
        obj = self._objmap.get(name)
        if not obj:
            if name not in self.keys():
                raise KeyError('Object %r not known' % name)
            obj = self.bind(name, GenericRPCObject)
        return obj

    def bind(self, name, cls):
        """Map a named remote object to a local instance."""
        obj = cls(self, name)
        self._objmap[name] = obj
        return obj

    def new(self, cls, name, args, impl=None):
        if impl is None:
            impl = GenericRPCObject
        self.rpc(cls, 'new', list(args) + [name]) # Assume name is last arg
        obj = self.bind(name, impl)
        return obj

class SerialRPC(RPCClient):
    def __init__(self, device, baud=9600):
        super(SerialRPC, self).__init__()
        self.ser = serial.Serial(device)
        self.ser.setBaudrate(baud)

    def rpc(self, name, method, args=[]):
        if name:
            path = '/%s/%s' % (name, method)
        else:
            path = '/%s' % (method,)
        req = ' '.join([path] + [str(a) for a in args])
        if debug: print 'send: %r' % req
        self.ser.write(req+'\n')
        resp = self.ser.readline().strip()
        if debug: print 'recv: %r' % resp
        return resp

    def rpcl(self, name, method, args=[]):
        """RPC call interpreting result as list of items."""
        resp = self.rpc(name, method, args)
        if resp:
            return resp.split()
        return

class RPCObject(object):
    def __init__(self, clnt, name):
        self._clnt = clnt
        self._name = name

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self._name)

    def _call(self, method, args):
        res = self._clnt.rpcl(self._name, method, args)
        # Fix up weird appending of methd name
        if len(res) > 0  and  res[-1] == method:
            res.pop()
        return res

class GenericRPCObject(RPCObject):
    """Generic local object with methods found by inspection."""
    def __init__(self, clnt, name):
        super(GenericRPCObject, self).__init__(clnt, name)
        self._methods = clnt.rpcl(name, '')
        for meth in self._methods:
            self._add_method(meth)

    def _add_method(self, meth):
        def m(*args):
            return self._call(meth, args)
        setattr(self, meth, m)

class DigitalOut(RPCObject):

    @classmethod
    def new(cls, clnt, pin, name=None):
        if name is None:
            name = pin
        obj = clnt.new('DigitalOut', name, [pin], cls)
        print obj
        return obj

    def write(self, value):
        self._call('write', [value])

class RPCFunction(RPCObject):
    def __call__(self, *args):
        return self._call('run', args)

if __name__=='__main__':
    import glob
    ttys = glob.glob('/dev/ttyACM*')
    if not ttys:
        raise Exception('No /dev/ttyACM* device found')
    tty = ttys[0]
    print 'Using %s' % tty
    r = SerialRPC(tty)
    for obj in r.keys():
        print obj
    pass
