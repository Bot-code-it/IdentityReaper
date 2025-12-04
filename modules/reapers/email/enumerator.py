from requests import Session,get as Get
from bs4 import BeautifulSoup
from json import dumps as JsonDumps,loads as JsonLoads
from hashlib import sha256 as SHA256
from hmac import new as NewHmac
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.useragent import UserAgent
class EmailReaper:
    def __init__(self):
        self.sites=[self.Amazon,self.Instagram,self.Spotify,self.X,self.Chess,self.Crazygames]
        self.AMAZON=Session()
        self.INSTAGRAM=Session()
        self.CHESS=Session()
        self.CRAZYGAMES=Session()
    def Amazon(self,email):
        base_url="https://www.amazon.com/ap/signin"
        headers={"User-Agent":UserAgent(),
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language":"en-US,en;q=0.5",
            "Accept-Encoding":"gzip, deflate, br",
            "Connection":"keep-alive"}
        try:
            signin_url=f"https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https://www.amazon.com%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
            response=self.AMAZON.get(signin_url,headers=headers,timeout=10)
            soup=BeautifulSoup(response.text, 'html.parser')
            data={}
            form=soup.find('form', {'name':'signIn'}) or soup.find('form')
            if form:
                for input_tag in form.find_all('input'):
                    if input_tag.get('name') and input_tag.get('value'):
                        data[input_tag['name']]=input_tag['value']
            data["email"]=email
            response=self.AMAZON.post(base_url,data=data,headers=headers,timeout=15)
            soup=BeautifulSoup(response.text, 'html.parser')
            password_field=soup.find("input", {"id":"ap_password"})
            password_alert=soup.find("div", {"id":"auth-password-missing-alert"})
            error_box=soup.find("div", {"id":"auth-error-message-box"})
            if password_field or password_alert:
                return {"service":"Amazon", "url":"https://www.amazon.com","exists":True, "error":False}
            elif error_box and "cannot find an account" in response.text.lower():
                return {"service":"Amazon", "url":"https://www.amazon.com","exists":False, "error":False}
            else:
                if "password" in response.text.lower() or "enter your password" in response.text.lower():
                    return {"service":"Amazon", "url":"https://www.amazon.com","exists":True, "error":False}
                else:
                    return {"service":"Amazon","url":"https://www.amazon.com","exists":False, "error":False}
        except Exception as e:
            return {"service":"Amazon","url":"https://www.amazon.com", "exists":False, "error":True,"msg":e}
    def Instagram(self,email):
        USERS_LOOKUP_URL='https://i.instagram.com/api/v1/users/lookup/'
        SIG_KEY_VERSION='4'
        IG_SIG_KEY='e6358aeede676184b9fe702b30f4fd35e71744605e39d2181a34cede076b3c33'
        def generate_signature(data_str):
            sig=NewHmac(IG_SIG_KEY.encode('utf-8'),data_str.encode('utf-8'),SHA256).hexdigest()
            return f"ig_sig_key_version={SIG_KEY_VERSION}&signed_body={sig}.{quote_plus(data_str)}"
        data={'login_attempt_count':'0',
            'directly_sign_in':'true',
            'source':'default',
            'q':email,
            'ig_sig_key_version':SIG_KEY_VERSION}
        data_str=JsonDumps(data)
        signed_data=generate_signature(data_str)
        headers={"Accept-Language":"en-US",
            "User-Agent":"Instagram 101.0.0.15.120",
            "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Encoding":"gzip, deflate",
            "X-FB-HTTP-Engine":"Liger",
            "Connection":"close"}
        try:
            response=self.INSTAGRAM.post(USERS_LOOKUP_URL,headers=headers,data=signed_data,timeout=10)
            result=response.json()
            if "message" in result and result["message"] == "No users found":
                return {"service":"Instagram","url":"https://www.instagram.com","exists":False, "error":False}
            else:
                return {"service":"Instagram","url":"https://www.instagram.com","exists":True, "error":False}
        except Exception as e:
            return {"service":"Instagram","url":"https://www.instagram.com","exists":False, "error":True,"msg":e}
    def Spotify(self, email):
        base_url="https://spclient.wg.spotify.com/signup/public/v1/account"
        try:
            response=Get(base_url,params={"validate":"1","email":email},timeout=10)
            resp=response.json()
            if resp['status']==1:
                return {"service":"Spotify","url":"https://open.spotify.com","exists":False,"error":False}
            elif resp['status']==20:
                return {"service":"Spotify","url":"https://open.spotify.com","exists":True,"error":False}
            else:
                return {"service":"Spotify","url":"https://open.spotify.com","exists":False,"error":True,"msg":resp['error']}
        except Exception as e:
            return {"service":"Spotify","url":"https://open.spotify.com","exists":False,"error":True,"msg":e}
    def X(self,email):
        base_url="https://api.twitter.com/i/users/email_available.json"
        params={"email":email}
        try:
            response=Get(base_url,params=params,timeout=10)
            resp=response.json()
            if not resp['valid'] and not resp['taken']:
                return {"service":"X (Twitter)","url":"https://x.com","exists":False,"error":True,"msg":resp['msg']}
            elif resp['taken']:
                return {"service":"X (Twitter)","url":"https://x.com","exists":True,"error":False}
            elif resp['valid'] and not resp['taken']:
                return {"service":"X (Twitter)","url":"https://x.com","exists":False,"error":False}
            else:
                return {"service":"X (Twitter)","url":"https://x.com","exists":False,"error":True,"msg":resp['msg']}
        except Exception as e:
            return {"service":"X (Twitter)","url":"https://x.com","exists":False,"error":True,"msg":e}
    def Chess(self,email):
        base_url="https://www.chess.com/rpc/chesscom.authentication.v1.EmailValidationService/Validate"
        headers = {"User-Agent":UserAgent(),
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://www.chess.com",
            "Referer": "https://www.chess.com/register"}
        payload={"email":email}
        data=JsonDumps(payload)
        try:
            response=self.CHESS.post(base_url,headers=headers,data=data,timeout=10).json()
            if response["status"]=="EMAIL_STATUS_TAKEN":
                return {"service":"Chess.com","url":"https://www.chess.com","exists":True,"error":False}
            if response["status"]=="EMAIL_STATUS_AVAILABLE":
                return {"service":"Chess.com","url":"https://www.chess.com","exists":False,"error":False}
            else:
                raise Exception(f"Status: {response['status']}")
        except Exception as e:
            return {"service":"Chess.com","url":"https://www.chess.com","exists":True,"error":True,"msg":e}
    def Crazygames(self,email):
        base_url="https://identitytoolkit.googleapis.com/v1/accounts:createAuthUri"
        params={"key":"AIzaSyAkBGn9sKEUBSMQ9CTFyHHxXas0tdcpts8"}
        headers={"User-Agent":UserAgent(),
                 "x-firebase-gmpid":"1:492838575572:web:423b0be4b4dabba02d0a41"}
        payload={"identifier":email,"continueUri":"https://www.crazygames.com/"}
        data=JsonDumps(payload)
        try:
            response=self.CRAZYGAMES.post(base_url,headers=headers,params=params,data=data,timeout=10)
            response=response.json()
            if response['registered']:
                return {"service": "Crazygames","url":"https://www.crazygames.com","exists": True,"error":False}
            else:
                return {"service": "Crazygames","url":"https://www.crazygames.com","exists": False,"error":False}
        except Exception as e:
            return {"service": "Crazygames","url":"https://www.crazygames.com","exists": False,"error":True,"msg":e}
    def GatherEmail(self,email):
        results=[]
        with ThreadPoolExecutor(max_workers=35) as executor:
            futures=[executor.submit(site,email) for site in self.sites]
            for future in as_completed(futures):
                result=future.result()
                if result:
                    results.append(result)
        return results
