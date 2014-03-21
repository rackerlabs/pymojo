import base64
import json
import requests

class Mojo:
  def __init__(self, endpoint, port=3000, use_ssl=False,
               verify=True, user=None, password=None):
    """Constructs a Mojo by connecting to a Jojo and caching its scripts"""
    self.endpoint = "http"
    if use_ssl:
      self.endpoint += "s"
    self.endpoint += "://" + endpoint + ":" + str(port)

    self.verify = verify
    self.user = user
    self.password = password

    if (user is not None) & (password is not None):
      self.auth = True
    else:
      self.auth = False

    scripts = self.__get_scripts()
    if isinstance(scripts, dict):
      self.scripts = scripts
    else:
      self.scripts = {}

  def __call(self, path, method="GET", data=""):
    """Makes a call to a Jojo"""
    s = requests.Session()
    headers = {
      "Content-Type" : "application/json"
    }

    if self.auth:
      headers["Authorization"] = "Basic " + base64.b64encode(self.user + ":" + self.password)

    req = requests.Request(method,
      self.endpoint + path,
      data=data,
      headers=headers
    ).prepare()

    resp = s.send(req, verify=self.verify)

    return resp


  def __get_scripts(self):
      """Gets a collection of scripts that live on the Jojo"""
      resp = self.__call("/scripts", method="GET")
      if resp.status_code == 200:
        return resp.json()['scripts']
      return resp

  def reload(self):
    """Reloads the Jojo's script cache, then stashes that data in the Mojo"""
    r = self.__call("/reload", method="POST")
    self.scripts = self.__get_scripts()

  def get_script(self, name, use_cache=True):
    """Gets data about a script in the Jojo, from the cache or from the Jojo"""
    if use_cache:
      if self.scripts[name] is not None:
        return self.scripts[name]
      else:
        return None
    else:
      resp = self.__call("/scripts/" + name)
      if resp.status_code == 200:
        self.scripts[name] = resp.json()['script']
        return self.scripts[name]
      else:
        return None

  def run(self, name, params={}):
    data = None
    if len(params) > 0:
      data = json.dumps(params)

    resp = self.__call("/scripts/" + name, method="POST", data=data)
    if resp.status_code == 200:
      return resp.json()
    return resp