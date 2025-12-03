from modules import IdentityReaper
def Color(text,color):
    code="\033[38;2;{};{};{}m"
    color_codes=dict(light=(145,255,0),red=(255,50,50),blue=(0,120,255),cyan=(0,200,255),purple=(197,70,255),yellow=(255,235,122),grey=(140,140,140),orange=(255,162,0),green=(0,222,152))
    return f"{code.format(*color_codes.get(color,(255,255,255)))}{text}\033[38;2;250;250;250m"
def CLS():
    print("\033c\033[38;2;250;250;250m",end='')
class CLI:
    def __init__(self):
        self.Reaper=IdentityReaper()
        self.Options=[i.capitalize() for i in self.Reaper.HuntingOptions.keys()]
    def Logo(self):
        print(Color(self.Reaper.Logo(),"red"),end='\n\n\n')
    def PrintTargetBox(self,information,scanner):
        self.Logo()
        username=information.get("username","")
        email=information.get("email","")
        phone=f'{information.get("country_code","")}{information.get("phonenumber","")}'
        length=max(list(map(len,[username,email,phone])))+2
        init1=Color("║  ","cyan")
        init2=Color("  ║","cyan")
        print(Color("╔"+"═"*(length+19)+"╗",'cyan'))
        print(init1+(scanner.upper()+" SCAN").center(length+15)+init2)
        print(Color("╠"+"═"*(length+19)+"╣",'cyan'))
        if username:
            print(init1+Color("Username      :","purple")+Color(username.rjust(length),"light")+init2)
        if email:
            print(init1+Color("Email         :","purple")+Color(email.rjust(length),"light")+init2)
        if phone:
            print(init1+Color("Phonenumber   :","purple")+Color(phone.rjust(length),"light")+init2)
        print(Color("╚"+"═"*(length+19)+"╝",'cyan'))
        return length+21
    def Menu(self):
        scanner=None
        while not scanner:
            self.Logo()
            for index,opt in enumerate(self.Options,start=1):
                print(Color(f"[{index}]",'purple'),opt)
            try:
                user=int(input(Color("\nSelect a scan level: ",'blue')))
                if user<1 or user>len(self.Options):
                    raise
                scanner=self.Options[user-1]
            except:
                pass
            CLS()
        return scanner
    def TargetInfo(self):
        info=dict()
        while True:
            self.Logo()
            print(Color(" Target's Information ".center(40,'='),"cyan")+"\n")
            print(Color("#Leave empty for 'None' . . .","yellow")+"\n")
            username=input(Color("Username      : ","purple")).strip(" ")
            email=input(Color("Email         : ","purple")).strip(" ")
            country_code=input(Color("Country Code  : ","purple")).strip(" +")
            if country_code and country_code.isnumeric():
                phone=input(Color("Phonenumber   : ","purple")+f"+{country_code} ").strip(" ")
            else: phone=""
            CLS()
            self.Logo()
            if not username and (not country_code or not phone) and not email:
                input(Color("No information provided . . .","orange"))
                CLS()
                continue
            if username:
                print(Color("Username      : ","purple")+Color(username,'light'))
            if email:
                print(Color("Email         : ","purple")+Color(email,'light'))
            if country_code and phone and phone.isnumeric() and country_code.isnumeric():
                print(Color("Phonenumber   : ","purple")+Color(f"+{country_code}{phone}",'light'))
            if input(Color("\nContinue with this information? (y/n): ","blue")).lower()=="y":
                CLS()
                break
            CLS()
        if username:
            info['username']=username
        if email:
            info['email']=email
        if country_code and phone and phone.isnumeric() and country_code.isnumeric():
            info['country_code']=country_code
            info['phonenumber']=phone
        return info
    def Scan(self,scanner,information):
        results=self.Reaper.Gather(scanner,**information)
        return results
    def PrintResults(self,results,information):
        def box(word,length):
            print(Color("╔"+("═"*length)+"╗","purple"))
            print(Color("║","purple")+Color(word.center(length),"light")+Color("║","purple"))
            print(Color("╚"+("═"*length)+"╝","purple"))
        CLS()
        self.Logo()
        lengthBox=max(list(map(lambda x: len(x)+len(information[x.lower()]),results.keys())))+7
        for key,val in results.items():
            box(f"{key.capitalize()} - {information[key.lower()]}",lengthBox)
            for item in val:
                symbol,color=("+","green") if item['exists'] else ("-","orange")
                symbol,color=("!","yellow") if item['error'] else (symbol,color)
                error=f"[ {item['msg']} ]" if item['error'] else f"[ {item['url']} ]"
                print(Color(f"[{symbol}] {item['service']} {error}",color))
            print()
    def Run(self):
        information=self.TargetInfo()
        scanner=self.Menu()
        self.PrintTargetBox(information,scanner)
        results=self.Scan(scanner,information)
        self.PrintResults(results,information)
        input()
c=CLI()
c.Run()
