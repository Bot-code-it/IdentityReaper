from modules.reapers.email import EmailReaper
from modules.reapers.phonenumber import PhonenumberReaper
from modules.reapers.username import UsernameReaper
from concurrent.futures import ThreadPoolExecutor
class IdentityReaper:
    def __init__(self):
        self.Username=UsernameReaper()
        self.Email=EmailReaper()
        self.Phone=PhonenumberReaper()
        self.HuntingOptions={"basic":self.Basic,"intermediate":self.Intermediate,"advance":self.Advance}
    def Logo(self):
        logo="""
  @@@ @@@@@@@  @@@@@@@@ @@@  @@@ @@@@@@@ @@@ @@@@@@@ @@@ @@@   @@@@@@@  @@@@@@@@  @@@@@@  @@@@@@@  @@@@@@@@ @@@@@@@
  @@@ @@@@@@@@ @@@@@@@@ @@@@ @@@ @@@@@@@ @@@ @@@@@@@ @@@ @@@   @@@@@@@@ @@@@@@@@ @@@@@@@@ @@@@@@@@ @@@@@@@@ @@@@@@@@
  @@@ @@@  @@@ @@@      @@!@!@@@   @@@   @@@   @@@   @@! !@@   @@!  @@@ @@@      @@!  @@@ @@!  @@@ @@@      @@!  @@@
  !@@ @@@  @@@ @@@      !@!!@!@@   !@@   !@@   !@@   !@! @!!   !@!  @!@ @@!      !@!  @!@ @@!  @!@ @@!      !@!  @!@
  !!@ @!@  !@@ @@!!!!   @!@ !!@@   !!@   !!@   !!@    !@!@!    @!@!!@!  @!!!:!   @!@!@!@! @!@@!@!  @!!!:!   @!@!!@!
  !!! !@!  !!@ @!!!!:   !!@  !!@   !!!   !!!   !!!     @@!!    !!@!@!   !!!!!:   !!!@!!!! @!@!!!   @!!!!:   !!@!@!
  !!: !!:  !!! !!:      !!:  !!!   !!:   !!:   !!:     !!:     !!: :!!  !!:      !!:  !!! !!:      !!:      !!: :!!
  :!: :!:  !:! !::      :!:  !:!   :!:   :!:   :!:     :!:     :!:  !:! :!:      :!:  !:! :!:      :!:      :!:  !:!
  ::  :::: ::  :: ::::  ::   ::    ::    ::    ::      ::      ::   ::: :: ::::  ::   :::  ::      :: ::::  ::   :::
  :   :: :  :  : :: ::  ::    :     :    :      :       :       :   : : : :: ::   :   : :   :      : :: ::   :   : :"""
        return logo
    def Basic(self,username=None,email=None,phonenumber=None,country_code=None):
        with ThreadPoolExecutor() as executor:
            futures={'Username':executor.submit(self.Username.GatherUsername,username,False) if username else None,
                'Email':executor.submit(self.Email.GatherEmail,email) if email else None,
                'Phonenumber':executor.submit(self.Phone.GatherPhonenumber,country_code,phonenumber) if phonenumber else None}
        return {key: future.result() for key,future in futures.items() if future}
    def Intermediate(self,username=None,email=None,phonenumber=None,country_code=None):
        with ThreadPoolExecutor() as executor:
            futures={'Username':executor.submit(self.Username.GatherUsername,username,True) if username else None,
                'Email':executor.submit(self.Email.GatherEmail,email) if email else None,
                'Phonenumber':executor.submit(self.Phone.GatherPhonenumber,country_code,phonenumber) if phonenumber else None}
        return {key: future.result() for key,future in futures.items() if future}
    def Advance(self,username=None,email=None,phonenumber=None,country_code=None):
        with ThreadPoolExecutor() as executor:
            futures={'Username':executor.submit(self.Username.GatherUsername,username,True) if username else None,
                'Email':executor.submit(self.Email.GatherEmail,email) if email else None,
                'Phonenumber':executor.submit(self.Phone.GatherPhonenumber,country_code,phonenumber) if phonenumber else None}
        return {key: future.result() for key,future in futures.items() if future}
    def Gather(self,option,username=None,email=None,phonenumber=None,country_code=None):
        Function=self.HuntingOptions.get(option.lower(),self.Basic)
        results=Function(username,email,phonenumber,country_code)
        return results
if __name__=="__main__":
    s=IdentityReaper()
