# timer3
python timer class


## Example
```python
from timer3 import Timer3
import time

timer = Timer3()


@timer.timethis(name="inner function")
def inner():
    time.sleep(1)


@timer.timethis()
def outer():
    inner()
    time.sleep(2)


with timer.time("first context"):
    time.sleep(2)
    inner()

inner()
outer()
print(timer)
```
results in 
```
+------------------------------------+
|               Timer3               |
+------------------------------------+
| first context       3.00364574E+00 |
|   inner function    1.00124818E+00 |
| inner function      1.00114537E+00 |
| outer               3.00355612E+00 |
|   inner function    1.00147891E+00 |
+------------------------------------+
```

Additionally, the results can be exported as a csv table by:
```python
timer.export_csv("times.csv")
```