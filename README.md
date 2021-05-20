# Spark Transpiler

## What is it?

This project defines a language, Spark, that is meant to be a very simple to use language, but also flexible. Somewhat of a combination between Python and JavaScript, with a powerful and extensive standard library.

I created this project to serve as a rapid prototyping language and system, so that I can try out ideas quickly without needing to setup a lot of boilerplate. To that end, it will eventually have a very powerful and extensive standard library, geared towards rapid prototyping of web apps.

## Language Details

### Variables

Variables are typeless, and can be defined like so:

```
variable_name = <statement>
variable_name += <statement>
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
### Conditionals

Conditionals are of the format:

```
if <statement> <condition> <statement>
    <statements>
```

Where a condition can be one of `>`, `<`, `=>`, `=<`, `==`, `!=`

### Loops

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

### Functions

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

### Classes

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
        print(
            "hello"
        )

class Class2
    function constructor()
        this.inst_of_class1 = Class1()

inst_of_class2 = Class2()

inst_of_class2.inst_of_class1.hello()
```

This code prints "hello"

### Arrays

Arrays can be defined in the following way:
```
foo = [
    "bar"
    baz
    [
        "foo"
    ]
]
```

### Maps

Maps can be defined in the following way:
```
foo = {
	key: "value"
}
```

## Standard Library

### Common

These methods are available to both backend and frontend:

| Method | Description | Signature |
| --- | --- | --- |
| print | Prints text to the console | Can take in any number of params. Params must be castable to a string |

### Frontend

These methods are available to the frontend code:

| Method | Description | Signature |
| --- | --- | --- |
| render | Renders a Component to the page | Takes in a single instance of a Component |

#### Component class

The Component class represents a component and its children, and can be rendered to the page.

The following methods are available:

##### Constructor

Signature:
```
new Component(
    tag
	attributes
    children
)
```

| Param | Type | Description |
| --- | --- | --- |
| tag | string | The tag to render |
| attributes | map | Attributes to attach to the element |
| children | array of strings | Children to render in the component. Can be strings, or other Components |

#### Style

The style object allows encoding of CSS and attaching it to a component

##### Constructor

Signature:
```
new Style(
    {
        color: "#fff"
    }
)
```