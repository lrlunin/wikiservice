import requests
import urllib
import os

class WikiService(object):
    """docstring for WikiService."""
    session = None
    username = None
    password = None
    domain = None
    api_url = None
    def __init__(self, username, password, domain, api_url):
        super(WikiService, self).__init__()
        self.username = username
        self.password = password
        self.domain = domain
        self.api_url = api_url
        self.login()

    class WrongPasswordError(Exception):
        pass

    class UploadError(Exception):
        pass

    class FileAlreadyExistsError(Exception):
        pass

    def login(self):
         if (self.username is not None) & (self.password is not None):
             print("Logging into wiki...")
             self.session = requests.Session()
             login_params = {
             "action" : "login",
             "lgname" : self.username,
             "lgpassword" : self.password,
             "lgdomain" : self.domain,
             "format" : "json"
             }
             login_response = self.session.post(url = self.api_url, params = login_params)
             login_token = login_response.json()['login']['token']
             login_params['lgtoken'] = login_token
             success_response = self.session.post(url = self.api_url, params = login_params)
             if (success_response.json()['login']['result'] != "Success"):
                 raise self.WrongPasswordError("Could not authenticate with password")
             else:
                 return success_response.json()['login']['result']

    def isSessionActive(self):
        test_params = {
        "action" : "query",
        "prop" : "info",
        "titles" : "Main%20Page",
        "format" : "json"
        }
        test_response = self.session.get(url = self.api_url, params = test_params)
        if ("error" in test_response.json()):
            return False
        else:
            return True

    def loadImage(self, filePath, uploadWithName = None, comment = None, text = None):
        if (not self.isSessionActive()):
            self.login()
        if uploadWithName is None:
            uploadWithName = os.path.basename(filePath)
        upload_params = {
        "action" : "upload",
        "filename" : uploadWithName,
        "format" : "json"
        }
        if (comment is not None):
            upload_params["comment"] = comment
        if (text is not None):
            upload_params["text"] = text
        upload_params["token"] = self.getEditToken()
        file = {
        "file" : (uploadWithName, open(filePath, "rb"))
        }
        response_upload = self.session.post(url = self.api_url, data = upload_params, files = file)
        if ("Warning" == response_upload.json()["upload"]["result"]):
            if ("exists" in response_upload.json()["upload"]["warnings"]):
                raise self.FileAlreadyExistsError("File with name %s already in wiki" % uploadWithName)
        elif ("Success" == response_upload.json()["upload"]["result"]):
            return uploadWithName
        #write success catch


    def createPage(self, title, text, createOnly = True):
        if (not self.isSessionActive()):
            self.login()
        createPage_params = {
        "action" : "edit",
        "title" : title,
        "text" : text,
        "createOnly" : "true" if createOnly else "false",
        "format" : "json",
        "token" : self.getEditToken()
        }
        self.session.post(url = self.api_url, data = createPage_params)

    def editPage(self, title, text):
        if (not self.isSessionActive()):
            self.login()
        editPage_params = {
        "action" : "edit",
        "title" : title,
        "text" : text,
        "nocreate" : "true",
        "format" : "json",
        "token" : self.getEditToken()
        }
        self.session.post(url = self.api_url, data = editPage_params)

    def getPageWikiText(self, title):
        if (not self.isSessionActive()):
            self.login()
        getWikiText_params = {
        "action" : "parse",
        "prop" : "wikitext",
        "page" : title,
        "format" : "json"
        }
        wikiText_response = self.session.get(url = self.api_url, params = getWikiText_params)
        if ("error" in wikiText_response.json()):
            return None
        else:
            wikiText = wikiText_response.json()["parse"]["wikitext"]
            return wikiText

    def getEditToken(self):
        if (not self.isSessionActive()):
            self.login()
        getToken_params = {
        "action" : "query",
        "prop": "info",
        "intoken": "edit",
        "format": "json",
        "titles" : "Main_Page"
        }
        token_response = self.session.get(url = self.api_url, params = getToken_params)
        csrf_token = token_response.json()["query"]["pages"]["1"]["edittoken"]
        return csrf_token
