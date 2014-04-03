A generic client library and command line client for Pyjojo, which lives
[here](https://github.com/atarola/pyjojo). Together, they are
[Mojojojo](http://i.imgur.com/TW2EiMb.gif)!

## Installation

    pip install pymojo

## Usage

### Command Line Client

In brief, for a totally default Jojo...

List the Jojo's scripts by name:

    mojo list

Show details on a script called "echo":

    mojo show echo

Run the "echo" script:

    mojo run echo text='Hello, world!'

More officially, mojo works like this...

    mojo [ -e endpoint ] [ -p port ] [ -s ] [ -i ] [ -u username ]
         [ -w password ] action [ script ] [ params ]

The various arguments (see below) tell Mojo how to hook up to your Jojo. The
action is one of these three:

 * `list` - Lists all of the scripts the Jojo knows
 * `show` - Shows detail on one of these scripts
 * `run` - Executes a script on the remote system

The `show` and `run` actions require that you specify a `script` by name, which
you can discover with a `list`. The `run` action also optionally accepts a
series of key/value pairs to pass into said script as environment variables.
These should be written like this: `key1=value1 key2=value2`

#### Arguments

    (-e | --endpoint) hostname
      The hostname running your Jojo

    ( -p | --port) port
      The port Jojo is running on

    ( -s | --ssl )
      Use SSL encryption

    ( -i | --ignore-warnings)
      Ignore SSL certificate security warnings, such as those in response to
      self-signed certificates, certs signed by untrusted CAs, and actual
      unsecure SSL certificates

    ( -u | --user ) user
      Username to use against HTTP Basic Auth

    ( -w | --password ) password
      Password to use against HTTP Basic Auth
      
### Library

Mojo's constructor accepts the following arguments:

 * `endpoint` - The network path to the server. This should be an IP or domain.
   (default: "localhost")
 * `port` - The port Jojo listens on (default: 3000)
 * `use_ssl` - Whether or not to use HTTPS (default: False)
 * `verify` - Whether to bother verifying Jojo's SSL certificate (default: True)
 * `user` - The username for HTTP Basic Auth (default: None)
 * `password` - The password for HTTP Basic Auth (default: None)

So if all of those defaults are what you need, then getting your Mojo on is
quite simple indeed:

    from pymojo.mojo import Mojo

    mojo = Mojo()

As an example of using every last option Mojo's constructor accepts, here's how
to interact with a Jojo server running on `192.168.0.123:9090`, which uses a
self-signed SSL certificate and HTTP Basic Authentication...

    mojo = Mojo(endpoint="192.168.0.123", port=9090, use_ssl=True, verify=False,
                user="username", password="A good password")
    
Once you have a Mojo, it's easy to use:

    # Print a list of every script the Jojo knows about
    for s in mojo.scripts:
      print s

    # Get script details from Mojo's cache
    script = mojo.get_script("my_script")
    # script is now a JSON object detailing the remote script

    # Get script details, forcing a refresh of this data from the Jojo server
    script = mojo.get_script("my_script", False)
    # script is the script JSON data, and Mojo's cache has been updated

    # Run a Jojo script
    resp = mojo.run("my_script", {foo:"bar", bar:"foo"})
    # resp is a requests response object from which you can gather a
    # resp.status_code and get the JSON body with resp.json()

    # Reload the Jojo's configuration and Mojo's cache
    mojo.reload()

## Extending Mojo

Pyjojo is merely a remote script execution engine, and is meant to be extended
to meet the needs of its users. As-is, Pymojo can act on any custom scripts on
a Jojo server, but the specifics of a Jojo deployment can be easily wrapped up
in a class that inherits a Mojo.

Realistically, you'll use Jojo for things like remote service control or
software deployments, but for the sake of example, let's say our Jojo server
only knows how to execute one script, `echo.sh`, which looks like this:

    #!/bin/bash
    
    # -- jojo --
    # description: echo
    # param: text - Text to echo
    # -- jojo --
    
    echo ${TEXT}
    exit 0

We'll make a special kind of Mojo built to run this echo script. We'll call it
an Echojo.

    class Echojo(Mojo):
      def __init__(self, **kwargs):
        Mojo.__init__(self, **kwargs)
      
      def echo(self, text):
        return self.run("echo", {"text" : text})

Simply put, it takes the same Jojo configuration options that Mojo takes,
and then passes them on to the superconstructor. The `echo` function passes
data through the superclass's `run` function and passes the result back up.