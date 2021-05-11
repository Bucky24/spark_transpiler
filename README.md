## Spark Transpiler

### Language Details

#### Variables

Variables are typeless, and can be defined like so:

```
variable_name = <value or variable>
variable_name += <value or variable>
```

The following types of variables exist:

| Name | Example |
| ---| --- |
| String | "Double quotes" 'single quotes' |
| Integer | 1231523532 |
| Floating Point | 154235.23543243 |

The following operators exist for numeric variables:

```
variable ++
```

Variables can also be coerced:

```
variable2 = variable as String
```

#### Conditionals

Conditionals are of the format:

```
if <statement> <condition> <statement>
    <statements>
```

Where a condition can be one of `>`, `<`, `=>`, `=<`, `==`, `!=`

#### Loops

A loop can have the following formats:

```
for array as item
    <statements>

for map as key : item
    <statements>

for <statement>; <statement>; <statement>
    <statements>

while <statement> <condition> <statement>
    <statements>
```

#### Functions

Function must be defined with the `function` keyword:

```
function foo()
    <statements>
```

They can take parameters:

```
function bar(a, b, c)
    <statements>
```

To call a function, arguments must be on new lines:

```
bar(
    5
    "string"
    4.23432
)
```

#### Classes

Can extend other classes. Can contain functions inside them.
Special function `constructor` for creating new instances.

```
class Name extends OtherClass
    function constructor(a,b,c)
        <statements>
```

Creating an instance of a method is done just like a function:

```
instance = Name(
    a
    b
    c
)
```

Chaining instances is done as normal:

```
class Class1
    function hello()
        print("hello")

class Class2
    function constructor()
        this.inst_of_class1 = Class1()

inst_of_class2 = Class2()

inst_of_class2.inst_of_class1.hello()
```

This code prints "hello"