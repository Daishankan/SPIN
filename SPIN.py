import json
import sys
import hashlib
import os
import time
import getpass

# --- COLOR DEFINITIONS ---
# Check if the platform supports ANSI escape codes for color
if sys.platform in ["linux", "linux2"] and sys.stdout.isatty():
    W = "\033[0m"   # White (reset)
    G = '\033[32;1m' # Green
    R = '\033[31;1m' # Red
    B = '\033[34;1m' # Blue
    Y = '\033[33;1m' # Yellow
else:
    W, G, R, B, Y = '', '', '', '', ''

# --- EXCEPTION HANDLING FOR 'requests' MODULE ---
try:
    import requests
except ImportError:
    print(R + "[!] خطأ: مكتبة 'requests' غير مثبتة.")
    print(Y + "[*] يرجى تثبيتها باستخدام الأمر: pip install requests")
    sys.exit()

# --- PYTHON 2/3 COMPATIBILITY ---
try:
    input = raw_input
except NameError:
    pass

# --- GLOBAL VARS ---
user_name_cache = []
token = '' # Will be loaded from file

# --- HELPER FUNCTIONS ---
def load_token():
    """Loads access token from file."""
    global token
    try:
        with open('cookie/token.log', 'r') as token_file:
            token = token_file.read().strip()
            return token
    except IOError:
        return None

def fetch_data(url):
    """Generic function to fetch data from Facebook Graph API."""
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes
        return json.loads(response.text)
    except requests.exceptions.RequestException as e:
        print(R + f"\n[!] خطأ في الاتصال: {e}" + W)
        return None
    except json.JSONDecodeError:
        print(R + "\n[!] فشل في تحليل استجابة الخادم (JSON)." + W)
        return None

# --- CORE FEATURES ---
def unfriend(friends_list):
    """
    Unfriends users from the provided list.
    This is the decrypted and cleaned version of the marshal code.
    """
    global token
    if not token:
        print(R + "[!] رمز الوصول غير موجود. يرجى إنشائه أولاً." + W)
        return

    print(Y + '\r[*] تم استرداد قائمة الأصدقاء بنجاح.' + W)
    print(G + '[*] بدء عملية حذف الأصدقاء...' + W)
    
    try:
        total_friends = len(friends_list)
        for i, friend in enumerate(friends_list):
            friend_id = friend.get('id')
            friend_name = friend.get('name')
            
            if not friend_id or not friend_name:
                continue

            # The API endpoint for unfriend is a POST request to /me/friends with method=delete
            url = f"https://graph.facebook.com/me/friends?uid={friend_id}&access_token={token}"
            params = {'method': 'delete'}
            
            response = requests.post(url, data=params)
            result = response.json()

            # Display progress
            progress = f"[{i+1}/{total_friends}]"
            
            if response.status_code == 200 and not result.get('error'):
                print(W + f"{progress} [{G}تم الحذف{W}] {friend_name} ({friend_id})")
            else:
                error_message = result.get('error', {}).get('message', 'Unknown error')
                print(W + f"{progress} [{R}فشل{W}] لم يتم حذف {friend_name}. السبب: {error_message}")
            
            time.sleep(1) # Add a delay to avoid being rate-limited

    except KeyboardInterrupt:
        print(R + '\n[!] تم إيقاف العملية من قبل المستخدم.' + W)
    except Exception as e:
        print(R + f'\n[!] حدث خطأ غير متوقع: {e}' + W)
        
    print(G + '[*] انتهت عملية حذف الأصدقاء.' + W)
    input(G + "\n[*] اضغط على Enter للعودة..." + W)

def get_friends_list():
    """Fetches the full friend list of the user."""
    if not token:
        print(R + "[!] رمز الوصول غير موجود." + W)
        return []
        
    print(G + "[*] جارٍ استرداد قائمة الأصدقاء..." + W)
    url = f'https://graph.facebook.com/me/friends?limit=5000&access_token={token}'
    data = fetch_data(url)
    
    if data and 'data' in data:
        print(G + f"[*] تم العثور على {len(data['data'])} صديق." + W)
        return data['data']
    else:
        print(R + "[!] فشل في استرداد قائمة الأصدقاء." + W)
        if data and 'error' in data:
            print(R + f"[*] السبب: {data['error']['message']}" + W)
        return []

# --- BANNERS AND MENUS ---
def display_banner():
    """Displays the main banner of the tool."""
    # The QB ASCII art is integrated here
    print(B + r'''
                                          _     _
                                        o' \.=./ `o
                                           (o o)          
                                       ooO--(_)--Ooo
                                       
   ____  ____  ____
  / __ \/ __ \/ __ \
 / / / / /_/ / /_/ /  {W}Social Profile Intelligence Network
/ /_/ / ____/ ____/   {Y}Version 2.0 - By ABDULLATEF
\____/_/   /_/
'''.format(W=W, Y=Y))
    
    if user_name_cache:
        print(G + ('[*] مرحباً بك: ' + user_name_cache[0]).center(60) + W)
    elif load_token():
        try:
            r = requests.get('https://graph.facebook.com/me?access_token=' + token)
            user_data = r.json()
            name = user_data.get('name')
            if name:
                user_name_cache.append(name)
                print(G + ('[*] مرحباً بك: ' + name).center(60) + W)
        except Exception:
            print(Y + "[!] رمز الوصول قديم أو غير صالح.".center(60) + W)
    else:
        print(Y + "[!] لم يتم تسجيل الدخول. استخدم 'token' لإنشاء رمز وصول.".center(60) + W)
    print(R + "============================================================" + W)

def display_warning_and_terms():
    """Displays warning and terms of use upon first run."""
    print(R + "======================[ تحذير وشروط الاستخدام ]======================" + W)
    print(Y + "[!] هذه الأداة مخصصة للأغراض التعليمية والبحثية فقط.")
    print(Y + "[!] أي استخدام غير قانوني أو غير أخلاقي لهذه الأداة هو على مسؤوليتك الخاصة.")
    print(Y + "[!] المبرمج 'ABDULLATEF' يخلي مسؤوليته بالكامل عن أي سوء استخدام.")
    print(R + "====================================================================" + W)
    input(G + "\n[*] اضغط على Enter للمتابعة والموافقة على الشروط..." + W)
    os.system('clear' if os.name == 'posix' else 'cls')

def show_main_menu():
    """Displays the main command menu."""
    print(B + '''
[ MAIN MENU ]
--------------------------------------------------------------------
  {G}COMMAND{W}              {G}DESCRIPTION{W}
--------------------------------------------------------------------
  {Y}get_data{W}           | جمع كافة بيانات الأصدقاء.
  {Y}get_info{W}           | عرض معلومات عن صديق معين.
  
  {Y}dump_id{W}            | استخراج ID جميع الأصدقاء.
  {Y}dump_phone{W}         | استخراج أرقام هواتف الأصدقاء (إن وجدت).
  {Y}dump_mail{W}          | استخراج إيميلات الأصدقاء (إن وجدت).
  
  {Y}token{W}               | إنشاء رمز وصول جديد (Access Token).
  {Y}cat_token{W}          | عرض رمز الوصول الحالي.
  {Y}rm_token{W}           | حذف رمز الوصول الحالي.
  
  {Y}bot{W}                 | فتح قائمة البوت (للتحكم الآلي).
  
  {Y}help{W}                | عرض قائمة المساعدة هذه.
  {Y}about{W}               | عرض معلومات حول الأداة.
  {Y}clear{W}               | مسح الشاشة.
  {Y}exit{W}                | الخروج من البرنامج.
--------------------------------------------------------------------
'''.format(G=G, W=W, Y=Y))

def show_about_info():
    """Displays information about the tool."""
    print(B + '''
[ ABOUT SPIN ]
--------------------------------------------------------------------
  {G}Tool Name{W}      : Social Profile Intelligence Network (SPIN)
  {G}Version{W}        : 2.0
  {G}Author{W}         : ABDULLATEF
  {G}Original Idea{W}  : Based on OSIF by CiKu370
  {G}Description{W}    : أداة لجمع المعلومات من فيسبوك بشكل مفتوح المصدر
                  للأغراض التعليمية والبحثية.
--------------------------------------------------------------------
'''.format(G=G, W=W))

def show_bot_menu():
    """Displays the bot features menu."""
    print(B + '''
[ BOT MENU ]
--------------------------------------------------------------------
  {G}NUM{W}   | {G}FEATURE{W}
--------------------------------------------------------------------
  {Y}[01]{W}  | ردود فعل تلقائية (Reactions).
  {Y}[02]{W}  | تعليقات تلقائية (Comments).
  {Y}[03]{W}  | وكز تلقائي (Poke).
  {Y}[04]{W}  | قبول جميع طلبات الصداقة.
  {Y}[05]{W}  | حذف جميع منشوراتك.
  {Y}[06]{W}  | حذف جميع الأصدقاء.
  {Y}[07]{W}  | إلغاء متابعة جميع الأصدقاء.
  {Y}[08]{W}  | حذف جميع ألبومات الصور.
  
  {R}[00]{W}  | العودة إلى القائمة الرئيسية.
--------------------------------------------------------------------
'''.format(G=G, W=W, Y=Y, R=R))

def handle_bot_menu():
    """Handles the logic for the bot menu."""
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        display_banner()
        show_bot_menu()
        choice = input(B + "SPIN (Bot) > " + W).strip()
        
        if choice == '00':
            return
        elif choice == '06':
            confirm = input(R + "[!] هل أنت متأكد من أنك تريد حذف جميع أصدقائك؟ هذا الإجراء لا يمكن التراجع عنه. (اكتب 'نعم' للتأكيد): " + W)
            if confirm.lower() == 'نعم':
                friends = get_friends_list()
                if friends:
                    unfriend(friends)
                else:
                    print(R + "[!] لا يوجد أصدقاء لحذفهم أو فشل في استرداد القائمة." + W)
                    time.sleep(3)
            else:
                print(Y + "[*] تم إلغاء العملية." + W)
                time.sleep(2)
        elif choice in ['01', '02', '03', '04', '05', '07', '08']:
            print(Y + "[!] هذه الميزة قيد التطوير وسيتم تفعيلها قريباً." + W)
            time.sleep(2)
        else:
            print(R + "[!] خيار غير صالح." + W)
            time.sleep(2)

def main():
    """Main function to run the tool."""
    if not os.path.exists('cookie'):
        os.makedirs('cookie')
        display_warning_and_terms()
    
    load_token()
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        display_banner()
        show_main_menu()
        
        try:
            choice = input(B + "SPIN > " + W).lower().strip()
            
            if choice == 'exit':
                print(Y + "[*] شكراً لاستخدامك SPIN. إلى اللقاء!" + W)
                sys.exit()
            elif choice == 'help':
                continue
            elif choice == 'about':
                os.system('clear' if os.name == 'posix' else 'cls')
                display_banner()
                show_about_info()
                input(G + "\n[*] اضغط على Enter للعودة..." + W)
            elif choice == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
            elif choice == 'bot':
                handle_bot_menu()
            elif choice in ['token', 'get_data', 'get_info', 'dump_id', 'dump_phone', 'dump_mail', 'cat_token', 'rm_token']:
                 print(Y + "[!] هذه الميزة قيد التطوير وسيتم تفعيلها قريباً." + W)
                 time.sleep(2)
            else:
                print(R + "[!] أمر غير معروف: '{}'. اكتب 'help' لعرض الخيارات.".format(choice) + W)
                time.sleep(2)

        except (KeyboardInterrupt, EOFError):
            print(Y + "\n\n[*] تم إيقاف الأداة. إلى اللقاء!" + W)
            sys.exit()

if __name__ == '__main__':
    main()
