This python module is an alternative to the "official" mbedrpc.
Example:
```
>>> from mbedrpc import *
>>> clnt = SerialRPC('/dev/ttyACM0')
```

Map a function already set up on the mbed:

```
>>> peek = clnt.bind('peek', RPCFunction)
>>> peek(0)
```

Create a new object:
```
>>> red = DigitalOut.new(clnt, 'LED5', 'red')
>>> red.write(1)
```
