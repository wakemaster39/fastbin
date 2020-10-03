#Fastbin

[![codecov](https://codecov.io/gh/wakemaster39/fastbin/branch/master/graph/badge.svg?token=H9WAVWZ7YY)](undefined)
[![Actions Status](https://github.com/wakemaster39/fastbin/workflows/Tests/badge.svg)](https://github.comwakemaster39/fastbin/actions)
[![Version](https://img.shields.io/pypi/v/fastbin)](https://pypi.org/project/fastbin/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/fastbin.svg)](https://pypi.org/project/fastbin/)
[![Pyversions](https://img.shields.io/pypi/pyversions/fastbin.svg)](https://pypi.org/project/fastbin/)

_Fastbin_ is a drop in replacement of [pycasbin](https://github.com/casbin/pycasbin) the python implementation of the
great authorization management [casbin](https://github.com/casbin/casbin).

_Fastbin_ is designed to address the primary concern when working with large sets of rules; Performance.

The root cause of working with large rule sets is the following: https://github.com/casbin/pycasbin/blob/88bcf96eb0586acd5a2cf3d3bd22a7802a0bfb27/casbin/core_enforcer.py#L238

Iterating over 10,000 rules to get a yes or no answer takes time, there really isn't a way around the fact. This limitation
comes from the generalization that casbin attempts to support. Independent on the format of your request, or policy definition
casbin if able to support your authorization mechanism.

_Fastbin_ makes a minimal set of assumptions to allow efficient filtering of the model so that the number of rules you
are iterating over to get a result is much smaller and performance can be maintained. Using _Fastbin_ when working with
rule sets of any size, it is possible to keep resolution of enforcement sub millisecond.

## Usage
Assuming your model and policies meet the requirements discussed [below](#required-assumptions), to use _Fastbin_
it takes the same arguments as the standard enforcer with additionally taking an ordered list of integers
representing the index position for a rule that should used to enable the cache.

_Fastbin_ used a nested dictionary structure to manage its cache, it based on the assumption that keys are exact matches
and can be used to filter on. For example, if you have rules that follow a similar format to `["/user99", "/obj99999", "read"]`,
and a matcher of `m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act` we can say that if we pre-filtered out all rules
that the objects or the action didn't match we would have a much smaller ruleset to manage.

Rather iterating on all the rules knowing the majority will not pass the `r.obj == p.obj && r.act == p.act` of the matcher,
we can tell _Fastbin_ to cache the rules based on `obj` and then the `action`. Then when it comes to enforcing a rule,
_Fastbin_ uses the incoming data to filter down the policies down to the minimal number based on the cache and
then then rest of the normal casbin enforcement logic takes place.

```python
"""
# Request definition
[request_definition]
r = sub, obj, act

# Policy definition
[policy_definition]
p = sub, obj, act
"""

import time

from fastbin import FastEnforcer

adapter = "/path/to/adapter" # or adapter of your choice
enforcer = FastEnforcer([1,2], "/path/to/model", adapter)

for x in range(100):
    for y in range(100000):
        enforcer.add_policy(f"/user{x}", f"/obj{y}", "read")


s = time.time()
# this is the absolute worst case last entry and should require iterating 10M rows and be very slow
a = enforcer.enforce("/user99", "/obj99999", "read")
print(a, (time.time() - s) * 1000)

# Output:
# True 0.8349418640136719
```

## Required Assumptions

 The two assumptions that are
required are:

* The order of the fields in the request and the policy to be used in the cache are at the same index position

Valid Rule Sets:
```
# Request definition
[request_definition]
r = sub, obj, act

# Policy definition
[policy_definition]
p = sub, obj, act
```
```
# Request definition
[request_definition]
r = sub, obj, act

# Policy definition
[policy_definition]
p = sub, obj, act, protected, before
```

Invalid Rul Sets:
```
# Request definition
[request_definition]
r = sub, obj, act

# Policy definition
[policy_definition]
p = sub, act, obj  # Not the act, obj have been swapped
```
```
# Request definition
[request_definition]
r = sub, obj, act

# Policy definition
[policy_definition]
p = sub, obj, protected, before, act # There are extra keys between the values
```

* The keys being used to cache do not require processing to extract from the cache.

Some people attempt to shrink the size of their rule sets but combing rules by using patterns in their rules such as setting
the action to be `read,write` and using a regex to split and match these values. This is not supported by _Fastbin_ and
is actually an anti-pattern now as you will be loosing performance.


### Why Not Filtered Policies?

Filtered policies are highly recommended and should be used in conjunction with _Fastbin_. _Fastbin_ is great at helping
working with large rule sets, but it cannot aid in the loading of those large policies from disk. This is where
loading filter policies really helps. If you can take you 1 million entry rule set, and shrink down the possible rules
you care about down to 1-10 thousand rules that can load in a reasonable amount of time, _Fastbin_ will then help
ensure enforcement against these rules is fast as well.


## Contributing

```
poetry run pre-commit install -t pre-commit -t commit-msg && poetry run pre-commit autoupdate && poetry run pre-commit run --all
```
