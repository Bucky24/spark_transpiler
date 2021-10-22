# Spark Transpiler

## What is it?

This project defines a language, Spark, that is meant to be a very simple to use language, but also flexible. Somewhat of a combination between Python and JavaScript.

I created this project to serve as a rapid prototyping language and system, so that I can try out ideas quickly without needing to setup a lot of boilerplate. To that end, it will eventually have a very powerful and extensive standard library, geared towards rapid prototyping of web apps.

# Language Details

## Variables

Variables are typeless, and can be defined like so:

```
variable_name = <statement>
variable_name += <statement>
```

The following are examples of valid values for variables:

| Name | Example |
| ---| --- |
| String | "Double quotes" 'single quotes' |
| Integer | 1231523532 |
| Floating Point | 154235.23543243 |
| Boolean | true, false |

The following operators exist for numeric variables:

```
variable ++
```

The following operations can be performed on any statement:

```
<statement> + <statement>
<statement> - <statement>
<statement> / <statement>
<statement> * <statement>
```
## Conditionals

Conditionals are of the format:

```
if <statement> <condition> <statement>
    <statements>
else
    <statements>
```

Where a condition can be one of `>`, `<`, `=>`, `=<`, `==`, `!=`

## Loops

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

## Functions

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

However a function that takes no arguments can be called on a single line:
```
bar()
```

Functions can return any statement:
```
function foo(bar)
    return bar
```

## Classes

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

## Arrays

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

Accessing the contents of an array can be done as normal:

```
foo = [
    "bar"
]

bar = foo[0]
```

## Maps

Maps can be defined in the following way:
```
foo = {
    key: "value"
}
```

## JSX

The system will properly parse JSX format as well:
```
foo = <div>
    <div
        id="blah"
    >
        "some text"
    </div>
</div>
```

Note that this is basically syntactic sugar that does the same thing as making a new instance of a Component.

## Includes

It is possible to include methods and classes from another file. Note that when doing so, you cannot define a backend function, then use it in frontend code in another file, or vice versa.

`include.spark`:
```
#backend

class Foo
    function foo()

function bar()
```

`main.spark`:
```
#include Foo,bar from include.spark

inst = Foo()
bar()
```

# Standard Library

## Common

These methods and classes are available to both backend and frontend:

| Method | Description | Signature |
| --- | --- | --- |
| print | Prints text to the console | Can take in any number of params. Params must be castable to a string |

## Frontend

These methods are available to the frontend code:

| Method | Description | Signature |
| --- | --- | --- |
| render | Renders a Component to the page | Takes in a single instance of a Component, or JSX tag |

### Component class

The Component class represents a component and its children, and can be rendered to the page.

The following methods are available:

#### Constructor

Signature:
```
Component(
    tag
    attributes
    children
)
```

| Param | Type | Description |
| --- | --- | --- |
| tag | string | The tag to render. Optional |
| attributes | map | Attributes to attach to the element |
| children | array | Children to render in the component. Can be strings, or other Components |

If the constructor is called with only 2 parameters, these are expected to be the attributes and the children. This should only be done for classes that extend Component.

#### Re-render

The rerender method allows a component to rerender itself and all of its children, without rerendering the rest of the page

Signature:
```
someComponent.rerender()
```

#### Extending

Component can be extended in the following way:

```
class SomeElement extends Component
    function render()
        return <div>
            this.children
        </div>
```

And can be incorporated into JSX:

```
foo = <div>
    <SomeElement>
        <span>
            "foo"
        </span>
    </SomeElement>
</div>
```

### Style

The Style object allows encoding of CSS and attaching it to a component

#### Constructor

Signature:
```
Style(
    {
        color: "#fff"
    }
)
```

### Variable

The Variable class allows storing of data across re-renders.

#### Constructor

Signature:
```
Variable(
    defaultValue
)
```

| Param | Type | Description |
| --- | --- | --- |
| defaultValue | any | The value to start the Variable with. Optional |

#### Get

Returns the current value of the Variable
```
foo = Variable(
    0
)

bar = foo.get()
```

#### Set

Sets the current value of the Variable
```
foo = Variable(
    0
)

foo.set(
    1
)
```

### Api
The Api class on the frontend is used to call apis.

#### post/get

```
result = Api.post(
    apiName
    apiParameters
)
```

| Param | Type | Description |
| --- | --- | --- |
| apiName | string | The name of the api to call |
| apiParameters | any | The parameters to pass to the API method. Can be anything that can be turned into JSON |

The result of this method will be whatever the API returned on the backend.**

### State

The state object keeps track of app state across components.

#### init

The init method is called to hydrate the state with inital values.

```
State.init(
    {
        key: <some data, usually another object>
    }
)
```

| Param | Type | Description |
| --- | --- | --- |
| initial value | map | The initial value of the app state |

#### get

The get method is called to fetch a value out of the state.

```
value = State.get(
    "path.to.desired.value"
)
```

| Param | Type | Description |
| --- | --- | --- |
| path | string | The path in the state tree to fetch |

#### set

The set method is called to update a piece of the state.

```
value = State.set(
    "path.to.desired.value"
    newValueToSet
)
```

| Param | Type | Description |
| --- | --- | --- |
| path | string | The path in the state tree to fetch |
| value | any | The new value to set in the tree |

## Backend

### Table

The Table class is used for defining and performing CRUD operations on database schemas.

#### Constructor

Signature:
```
Table(
    tableName
    fieldsList
    storageType
)
```

| Param | Type | Description |
| --- | --- | --- |
| tableName | string | The name of the database table |
| fieldsList | array | An array of Field objects |
| storageType | Table Storage Type | The type of storage to setup for this table. Optional, defaults to Table.SOURCE_FILE |

The Field is an object with the following structure:

```
{
    name: "the name of the field"
    type: <one of the Table types below, Table.STRING for example>
    meta: <optional array of Table metas>
}
```

Table field types:

The following types exist for table Fields
| Name | Description |
| --- | --- |
| STRING | Defines a field that stores strings |
| INT | Defines a field that stores integers |

Table meta types:

The following meta entries exist for table Fields
| Name | Description |
| --- | --- |
| AUTO | Indicates the field is an auto-increment field |

Table storage types:

| Name | Description |
| --- | --- |
| SOURCE_FILE | Uses a local file for data storage |
| SOURCE_MYSQL | Attempts to use a MySql server for storage |

#### load

The load method is an instance method, and will perform a query on the database, returning all fields that match.

```
exampleTable = Table(
    "example"
    [
        {
            name: "field1"
            type: Table.STRING
        }
    ]
)

results = exampleTable.load(
    {
        field1: "foo"
    }
)
```

| Param | Type | Description |
| --- | --- | --- |
| search | map | A map with keys being the field to search and value being the value the field must contain. An empty map will return all rows. |

#### insert

The insert method is an instance method, and will insert a new row into the database

```
exampleTable = Table(
    "example"
    [
        {
            name: "field1"
            type: Table.STRING
        }
    ]
)

exampleTable.insert(
    {
        field1: "foo"
    }
)
```

| Param | Type | Description |
| --- | --- | --- |
| data | map | A map with keys being the field and value being the value to insert for that field |

#### update

The update method is an instance method, and will update all matching rows in the db

```
exampleTable = Table(
    "example"
    [
        {
            name: "field1"
            type: Table.STRING
        }
    ]
)

exampleTable.update(
    {
        field1: "foo"
    }
    {
        field1: "bar"
    }
)
```

| Param | Type | Description |
| --- | --- | --- |
| search | map | Similar to `load`, this map defines what rows should be updated. An empty map will update all rows |
| data | map | Similar to `insert`, this map defines what fields to update and what data to update them with

#### setConfig

The setConfig method is meant for setting connection data for storage types that require connection info.

For mysql the setConfig method should be called with an object containing the following:

| Param | Description |
| --- | --- |
| host | The hostname or IP of the database |
| user | The username of the database |
| password | The password for the user |
| database | The database to use |

### Api

The Api class on the backend is used to define apis.

#### post/get

```
Api.get(
    apiName
    function(parameters, RequestObject)
        return result
)
```

| Param | Type | Description |
| --- | --- | --- |
| apiName | string | The name of the api to call |
| apiMethod | function | The function to call whenever the API is called. The result of this method is returned as the API result |

The result of this method will be whatever the API returned on the backend.

The RequestObject has the following methods available on it:

#### setSession

This method takes in any jsonifyable data and sets it as a session cookie on the frontend.

```
Api.get(
    apiName
    function(parameters, req)
        req.setSession(
            {
                id: 5
            }
        )
)
```

#### getSession

This method will return any value stored in a session cookie from the frontend, or null if one does not exist.

```
Api.get(
    apiName
    function(parameters, req)
        sessionData = req.getSession()
        id = sessionData.id
)
```