import requests


class WikiAPIService(object):
    """docstring for WikiService."""
    session = None
    username = None
    password = None
    domain = None
    api_url = None

    def __init__(self, username, password, domain, api_url):
        super(WikiAPIService, self).__init__()
        self.username = username
        self.password = password
        self.domain = domain
        self.api_url = api_url

    class WrongPasswordError(Exception):
        pass

    class UploadError(Exception):
        pass

    class CredentialsError(Exception):
        pass

    class FileAlreadyExistsError(Exception):
        pass

    class PageAlreadyExistsError(Exception):
        pass

    def login(self):
        """
        Login to wiki with in constructor given username/password/domain/url
        @raise CredentialsError, if no user with found or fields are empty
        @raise WrongPasswordError, if given password is wrong
        """
        if ((self.username is not None) & (self.username != "")) & (
                (self.password is not None) & (self.password != "")):
            self.session = requests.Session()
            login_params = {
                "action": "login",
                "lgname": self.username,
                "lgpassword": self.password,
                "lgdomain": self.domain,
                "format": "json"
            }
            login_response = self.session.post(url=self.api_url, params=login_params)
            login_token = login_response.json().get('login').get('token')
            if login_token is None:
                raise self.CredentialsError
            login_params['lgtoken'] = login_token
            success_response = self.session.post(url=self.api_url, params=login_params)
            if success_response.json().get('login').get('result') != "Success":
                raise self.WrongPasswordError
        else:
            raise self.CredentialsError

    def isSessionActive(self):
        """
        Checks status of used session
        @return: True, if session is active
                 False, if session has expired or wasn't created
        """
        test_params = {
            "action": "query",
            "prop": "info",
            "titles": "Main%20Page",
            "format": "json"
        }
        if self.session is None:
            return False
        test_response = self.session.get(url=self.api_url, params=test_params)
        if test_response.json().get('error') is None:
            return True
        else:
            return False

    def loadImage(self, image_bytes, filename, extension, comment=None, text=None):
        """
        Provides to upload as byte array formatted images. Byte array should be formatted accordingly its
        image extension
        @param image_bytes: array of image bytes
        @param filename: name of file without extension and dot Example: "photo23_12"
        @param extension: any acceptable image extension in wiki-system Example: "png"
        @param comment: supply comment for file, will be displayed in wiki
        @param text: supply text for file, will be displayed in wiki
        @return: full name of uploaded file Example: "photo23_12.png"
        @raise: FileAlreadyExistsError, if the file already exists in wiki-system
        @raise UploadError, if given data are wrong
        """
        if not self.isSessionActive():
            self.login()
        if (filename is None) or (image_bytes is None) or (extension is None):
            raise self.UploadError
        filename += (".%s" % extension)
        upload_params = {
            "action": "upload",
            "filename": filename,
            "format": "json"
        }
        if comment is not None:
            upload_params["comment"] = comment
        if text is not None:
            upload_params["text"] = text
        upload_params["token"] = self.getEditToken()
        file = {
            "file": (filename, image_bytes)
        }
        response_upload = self.session.post(url=self.api_url, data=upload_params, files=file)
        if "Warning" == response_upload.json()["upload"]["result"]:
            if "exists" in response_upload.json()["upload"]["warnings"]:
                raise self.FileAlreadyExistsError()
        elif "Success" == response_upload.json()["upload"]["result"]:
            return filename
        # write success catch

    def createPage(self, title, text):
        """
        Provides to create new page with given title and text (wiki-formatted). Cannot delete or edit page,
        if it was already created
        @param title: title of the new page Example: "Ludwig IV the king"
        @param text: text of the new page Example: "He was a king"
        @raise PageAlreadyExistsError, if page with given name already exits
        """
        if not self.isSessionActive():
            self.login()
        createPage_params = {
            "action": "edit",
            "title": title,
            "text": text,
            "createonly": "true",
            "format": "json",
            "token": self.getEditToken()
        }
        createPage_response = self.session.post(url=self.api_url, data=createPage_params).json()
        if createPage_response.get('error').get('code') == 'articleexists':
            raise self.PageAlreadyExistsError

    def editPage(self, title, text):
        """
        Provides to replace old text of page with given title with new given text (wiki-formatted)
        @param title: title of the page Example: "Ludwig IV the king"
        @param text: new text of the page Example: "He was a great king"
        """
        if not self.isSessionActive():
            self.login()
        editPage_params = {
            "action": "edit",
            "title": title,
            "text": text,
            "nocreate": "true",
            "format": "json",
            "token": self.getEditToken()
        }
        self.session.post(url=self.api_url, data=editPage_params)

    def getPageWikiText(self, title):
        """
        Provides to get text (wiki-formatted) of page with given title
        @param title: title of page Example: "Ludwig IV the king"
        @return: text (wiki-formatted) Example: "He was a great king"
        """
        if not self.isSessionActive():
            self.login()
        getWikiText_params = {
            "action": "parse",
            "prop": "wikitext",
            "page": title,
            "format": "json"
        }
        wikiText_response = self.session.get(url=self.api_url, params=getWikiText_params)
        if "error" in wikiText_response.json():
            return None
        else:
            wikiText = wikiText_response.json().get('parse').get('wikitext')
            return wikiText

    def getEditToken(self):
        """
        Provides to get a token, that requires for any edits in wiki-engine
        @return: token as string (already formatted)
        """
        if not self.isSessionActive():
            self.login()
        getToken_params = {
            "action": "query",
            "prop": "info",
            "intoken": "edit",
            "format": "json",
            "titles": "Main_Page"
        }
        token_response = self.session.get(url=self.api_url, params=getToken_params)
        csrf_token = token_response.json().get('query').get('pages').get('1').get('edittoken')
        return csrf_token

    def logout(self):
        """
        Provides to logout from current user-session
        """
        if self.isSessionActive():
            logout_params = {
                "action": "logout",
                "format": "json"
            }
            self.session.get(url=self.api_url, params=logout_params)
            self.session = None
