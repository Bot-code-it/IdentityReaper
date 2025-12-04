from requests import Session
from bs4 import BeautifulSoup
from json import dumps as JsonDumps
from hashlib import sha256 as SHA256
from hmac import new as NewHmac
from urllib.parse import quote_plus
from modules.useragent import UserAgent
class PhonenumberReaper:
    def __init__(self):
        self.sites=[self.Amazon,self.Instagram]
        self.AMAZON=Session()
        self.INSTAGRAM=Session()
    def Amazon(self,country_code,phone):
        country_code_clean=country_code.strip(" +")
        if country_code_clean == '91':
            base_url="https://www.amazon.in"
        elif country_code_clean == '44':
            base_url="https://www.amazon.co.uk"
        else:
            base_url="https://www.amazon.com"
        headers={
            "User-Agent":UserAgent(),
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language":"en-US,en;q=0.5",
            "Accept-Encoding":"gzip, deflate, br",
            "Connection":"keep-alive"}        
        try:
            signin_url=f"{base_url}/ap/signin?openid.pape.max_auth_age=0&openid.return_to={base_url}%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=inflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
            response=self.AMAZON.get(signin_url, headers=headers, timeout=15)
            soup=BeautifulSoup(response.text, 'html.parser')
            data={}
            form=soup.find('form', {'name':'signIn'}) or soup.find('form')
            if form:
                for input_tag in form.find_all('input'):
                    if input_tag.get('name') and input_tag.get('value'):
                        data[input_tag['name']]=input_tag['value']
            
            data["email"]=f"{country_code}{phone}"
            
            response=self.AMAZON.post(f"{base_url}/ap/signin",data=data,headers=headers,timeout=15)
            soup=BeautifulSoup(response.text, 'html.parser')
            password_field=soup.find("input", {"id":"ap_password"})
            password_alert=soup.find("div", {"id":"auth-password-missing-alert"})
            error_box=soup.find("div", {"id":"auth-error-message-box"})
            
            if password_field or password_alert:
                return {"service":"Amazon", "exists":True, "error":False}
            elif error_box and "cannot find an account" in response.text.lower():
                return {"service":"Amazon", "exists":False, "error":False}
            else:

                if "password" in response.text.lower() or "enter your password" in response.text.lower():
                    return {"service":"Amazon", "exists":True, "error":False}
                else:
                    return {"service":"Amazon", "exists":False, "error":False}
                
        except Exception as e:
            return {"service":"Amazon", "exists":False, "error":True,"msg":e}
    
    def Instagram(self,country_code,phone):
        country_code=country_code.strip(' +')
        phone_number=f"{country_code}{phone}"
        USERS_LOOKUP_URL='https://i.instagram.com/api/v1/users/lookup/'
        SIG_KEY_VERSION='4'
        IG_SIG_KEY='e6358aeede676184b9fe702b30f4fd35e71744605e39d2181a34cede076b3c33'
        def generate_signature(data_str):
            sig=NewHmac(IG_SIG_KEY.encode('utf-8'),data_str.encode('utf-8'),SHA256).hexdigest()
            return f"ig_sig_key_version={SIG_KEY_VERSION}&signed_body={sig}.{quote_plus(data_str)}"
        data={'login_attempt_count':'0',
            'directly_sign_in':'true',
            'source':'default',
            'q':phone_number,
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
                return {"service":"Instagram", "exists":False, "error":False}
            else:
                return {"service":"Instagram", "exists":True, "error":False}
                
        except Exception as e:
            return {"service":"Instagram", "exists":False, "error":True,"msg":e}
    def GatherPhonenumber(self,country_code,phone):
        results=[]
        for function in self.sites:
            results.append(function(country_code,phone))
        return results
