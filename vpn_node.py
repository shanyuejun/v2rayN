import requests
import re
from datetime import datetime
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import os

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_latest_vpn_subscribe():
    """获取最新的VPN订阅链接并保存到文件"""
    
    # 固定输出文件名
    output_file = "vpn_subscribe.txt"
    
    print("="*60)
    print("VPN订阅链接获取器")
    print("="*60)
    
    # 直接访问最新的.md文件
    # 根据图片，最新的是2026-01文件夹下的文件
    
    # 尝试当前年份和月份
    today = datetime.now()
    
    # 可能的年份-月份组合（从最新到最旧尝试）
    year_months = [
        today.strftime("%Y-%m"),  # 当前年月
        f"{today.year}-{today.month-1:02d}" if today.month > 1 else f"{today.year-1}-12",  # 上个月
        "2026-01",  # 根据图片显示的最新月份
        "2025-12",
        "2025-11",
        "2025-10"
    ]
    
    # 尝试不同时间点的文件
    time_points = []
    for hour in range(15, -1, -1):
        for minute in [30, 0]:
            time_points.append((hour, minute))
    
    found_content = None
    source_info = ""
    
    # 尝试不同的年月和时间点
    for year_month in year_months:
        print(f"\n尝试年份-月份: {year_month}")
        
        # 尝试今天
        for hour, minute in time_points:
            filename = f"{today.day:02d}日{hour:02d}时{minute:02d}分.md"
            url = f"https://raw.githubusercontent.com/sharkDoor/vpn-free-nodes/master/node-list/{year_month}/{filename}"
            
            try:
                print(f"  尝试: {filename}", end="\r")
                response = requests.get(url, verify=False, timeout=5)
                if response.status_code == 200:
                    found_content = response.text
                    source_info = f"{year_month}/{filename}"
                    print(f"  ✓ 找到文件: {filename}")
                    break
            except:
                continue
        
        if found_content:
            break
        
        # 尝试昨天
        yesterday = today.replace(day=today.day-1) if today.day > 1 else today.replace(month=today.month-1, day=28)
        for hour, minute in time_points:
            filename = f"{yesterday.day:02d}日{hour:02d}时{minute:02d}分.md"
            url = f"https://raw.githubusercontent.com/sharkDoor/vpn-free-nodes/master/node-list/{year_month}/{filename}"
            
            try:
                print(f"  尝试: {filename}", end="\r")
                response = requests.get(url, verify=False, timeout=5)
                if response.status_code == 200:
                    found_content = response.text
                    source_info = f"{year_month}/{filename}"
                    print(f"  ✓ 找到文件: {filename}")
                    break
            except:
                continue
        
        if found_content:
            break
    
    if not found_content:
        print("\n✗ 未找到任何.md文件")
        return False
    
    print(f"\n✓ 成功获取文件: {source_info}")
    print(f"文件大小: {len(found_content)} 字符")
    
    # 提取所有VPN链接
    print("\n正在提取VPN链接...")
    links = []
    
    # 提取trojan链接
    trojan_links = re.findall(r'trojan://[^\s\n\r]+', found_content)
    links.extend(trojan_links)
    print(f"  Trojan链接: {len(trojan_links)} 个")
    
    # 提取ss链接
    ss_links = re.findall(r'ss://[^\s\n\r]+', found_content)
    links.extend(ss_links)
    print(f"  SS链接: {len(ss_links)} 个")
    
    # 提取vmess链接
    vmess_links = re.findall(r'vmess://[^\s\n\r]+', found_content)
    links.extend(vmess_links)
    print(f"  Vmess链接: {len(vmess_links)} 个")
    
    # 去重
    unique_links = []
    seen = set()
    for link in links:
        if link not in seen:
            seen.add(link)
            unique_links.append(link)
    
    print(f"\n✓ 共提取到 {len(unique_links)} 个唯一链接")
    
    if not unique_links:
        print("✗ 未找到任何VPN链接")
        return False
    
    # 保存到文件（覆盖写入）
    print(f"\n正在保存到 {output_file}...")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入文件头
            f.write("# VPN订阅链接\n")
            f.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 来源: {source_info}\n")
            f.write(f"# 链接数量: {len(unique_links)}\n")
            f.write("# 提示: 每行一个链接，可直接导入到支持订阅的客户端\n")
            f.write("="*60 + "\n\n")
            
            # 写入链接
            for link in unique_links:
                f.write(link + "\n")
        
        # 获取文件路径
        file_path = os.path.abspath(output_file)
        
        print(f"✓ 已保存 {len(unique_links)} 个链接到 {output_file}")
        print(f"文件路径: {file_path}")
        
        # 显示前5个链接
        print(f"\n前5个链接:")
        for i, link in enumerate(unique_links[:5], 1):
            print(f"{i}. {link}")
        
        return True
        
    except Exception as e:
        print(f"✗ 保存文件失败: {e}")
        return False

if __name__ == "__main__":
    # 只需要requests库
    # pip install requests
    
    success = get_latest_vpn_subscribe()
    
    if success:
        print("\n" + "="*60)
        print("完成！订阅链接已保存到 vpn_subscribe.txt")
        print("可以直接将该文件导入到支持订阅的VPN客户端")
    else:
        print("\n" + "="*60)
        print("获取失败，请检查网络连接")