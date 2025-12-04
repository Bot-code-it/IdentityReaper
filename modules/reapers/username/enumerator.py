from requests import Session
from requests.exceptions import Timeout as TimeoutException,ConnectionError as ConnectionException
from concurrent.futures import ThreadPoolExecutor,as_completed
from json import load as JSONload,dumps as JSONdumps,loads as JSONloads
from re import match as MatchRE
from os.path import dirname, join as joinPath, realpath
from modules.useragent import UserAgent
class UsernameReaper:
    def __init__(self):
        self.session=Session()
        self.AdvanceSiteData=self.LoadDatabase(joinPath(dirname(realpath(__file__)),"Data","AdvanceSiteData.json"))
        self.BasicSiteData=self.LoadDatabase(joinPath(dirname(realpath(__file__)),"Data","BasicSiteData.json"))
    def generateHeaders(self):
        headers={"User-Agent":UserAgent(),
            "Accept":"text/html,application/xhtml+xml,application/xml,application/json;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding":"gzip, deflate, br, zstd",
            "DNT":"1",
            "Connection":"keep-alive",
            "Upgrade-Insecure-Requests":"1",
            "Sec-Fetch-Dest":"document",
            "Sec-Fetch-Mode":"navigate",
            "Sec-Fetch-Site":"none",
            "Cache-Control":"private, s-maxage=0, max-age=0, must-revalidate, no-store",
            "sec-ch-ua":'"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"'}
        return headers
    def LoadDatabase(self,filepath):
        try:
            with open(filepath,'r',encoding='utf-8') as f:
                data=JSONload(f)
                return data
        except Exception as e:
            print(e)
            return {}
    def check_username(self,site_name,site_data,username):
        try:
            url=site_data['url'].format(username)
            probe_url=site_data.get('urlProbe',url).format(username)
            regex_check=site_data.get('regexCheck')
            if regex_check and not MatchRE(regex_check,username):
                return None
            method=site_data.get('request_method','GET')
            headers=self.generateHeaders()
            site_headers=site_data.get("headers", {})
            headers.update(site_headers)
            payload=site_data.get('request_payload',{})
            if payload:
                payload=JSONloads(JSONdumps(payload).replace('{}',username))
            if method=='POST':
                response=self.session.post(probe_url,headers=headers,json=payload,timeout=10)
            elif method=='HEAD':
                response=self.session.head(probe_url,headers=headers,timeout=10)
            else:
                response=self.session.get(probe_url,headers=headers,timeout=10)
            error_type=site_data.get('errorType')
            exists=False
            if error_type == 'status_code':
                exists=response.status_code==200
            elif error_type == 'message':
                error_msgs=site_data.get('errorMsg',[])
                if isinstance(error_msgs,str):
                    error_msgs=[error_msgs]
                exists=not any(msg in response.text for msg in error_msgs)
            elif error_type == 'response_url':
                error_url=site_data.get('errorUrl','')
                exists=response.url != error_url and error_url not in response.url
            else:
                exists=response.status_code==200
            return {'service':site_name,'url':url,'exists':exists,'error':False}
        except TimeoutException:
            return {'service':site_name,'url':url,'exists':False,'error':True,'msg':'Timeout'}
        except ConnectionException:
            return {'service':site_name,'url':url,'exists':False,'error':True,'msg':'Connection Error'}
        except Exception as e:
            return {'service':site_name,'url':url,'exists':False,'error':True,'msg':e}
    def GatherUsername(self,username,advance=False):
        results=[]
        siteData=self.BasicSiteData
        if advance:
            siteData=self.AdvanceSiteData
        with ThreadPoolExecutor(max_workers=35) as executor:
            futures={executor.submit(self.check_username,site_name,site_data,username): site_name for site_name,site_data in siteData.items()}
            for future in as_completed(futures):
                result=future.result()
                if result is None:
                    continue
                results.append(result)
        return results
