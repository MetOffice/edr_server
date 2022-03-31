# EDR Server Implementations
The Data interfaces defined in the `core` packages are used by the packages under
`edr_server.impl` to provide server implementations based on different technologies.

They are all abstracted from the data interface implementation in the same way,
so any data interface that correctly implements the data interface can be used with any server implementation.

These are the implementations currently available:
* [tornado](https://www.tornadoweb.org/en/stable/) (version 6.1 and higher)