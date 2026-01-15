import requests
import re
from datetime import datetime, timedelta
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import os

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def find_latest_file_url():
    """根据当前时间动态搜索最新的VPN节点文件"""
    now = datetime.now()
    print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 构建可能的时间点（从当前时间往前推，每半小时一个文件）
    time_points = []
    
    # 获取当前小时和分钟
    current_hour = now.hour
    current_minute = now.minute
    
    # 计算最近的半小时时间点
    if current_minute >= 30:
        latest_minute = 30
    else:
        latest_minute = 0
    
    # 从最近的时间点开始往前搜索
    # 搜索过去24小时内的文件
    for hour_offset in range(0, 24):  # 搜索过去24小时
        # 计算目标时间
        target_time = now - timedelta(hours=hour_offset)
        
        # 尝试半小时时间点
        for minute in [30, 0]:
            # 构建文件名
            filename = f"{target_time.day:02d}日{target_time.hour:02d}时{minute:02d}分.md"
            
            # 构建可能的年月文件夹
            year_month = target_time.strftime("%Y-%m")
            
            # 构建URL
            url = f"https://raw.githubusercontent.com/sharkDoor/vpn-free-nodes/master/node-list/{year_month}/{filename}"
            
            time_points.append({
                'url': url,
                'filename': filename,
                'year_month': year_month,
                'time': target_time.replace(minute=minute)
            })
    
    # 按时间从新到旧排序
    time_points.sort(key=lambda x: x['time'], reverse=True)
    
    # 尝试获取文件
    print(f"\n开始搜索最新文件...")
    
    for i, time_point in enumerate(time_points[:20]):  # 只尝试前20个
        try:
            print(f"尝试: {time_point['year_month']}/{time_point['filename']}", end="\r")
            response = requests.get(time_point['url'], verify=False, timeout=3)
            if response.status_code == 200:
                file_size = len(response.text)
                if file_size > 100:  # 文件大小至少100字节
                    print(f"✓ 找到最新文件: {time_point['year_month']}/{time_point['filename']}")
                    print(f"  文件大小: {file_size} 字符")
                    return time_point['url'], response.text, time_point
        except:
            continue
    
    print("\n✗ 未找到任何有效文件")
    return None, None, None

def extract_vpn_links(content):
    """从文件内容中提取VPN链接"""
    print("\n正在提取VPN链接...")
    
    # 定义各种VPN协议的正则表达式
    vpn_patterns = {
        'Trojan': r'trojan://[^\s\n\r<>{}|\\^`]+',
        'SS': r'ss://[^\s\n\r<>{}|\\^`]+',
        'Vmess': r'vmess://[^\s\n\r<>{}|\\^`]+',
        'VLESS': r'vless://[^\s\n\r<>{}|\\^`]+',
        'Hysteria': r'hysteria://[^\s\n\r<>{}|\\^`]+',
        'Hysteria2': r'hysteria2://[^\s\n\r<>{}|\\^`]+',
        'Tuic': r'tuic://[^\s\n\r<>{}|\\^`]+',
        'WireGuard': r'wg://[^\s\n\r<>{}|\\^`]+',
        'HTTP/HTTPS': r'https?://[^\s\n\r<>{}|\\^`]+',
        'SSH': r'ssh://[^\s\n\r<>{}|\\^`]+'
    }
    
    # 提取所有链接
    all_links = []
    categorized_links = {}
    
    for vpn_type, pattern in vpn_patterns.items():
        links = re.findall(pattern, content, re.IGNORECASE)
        if links:
            categorized_links[vpn_type] = links
            all_links.extend(links)
            print(f"  {vpn_type}: {len(links)} 个")
    
    # 去重
    unique_links = []
    seen = set()
    
    for link in all_links:
        # 清理链接（移除多余空格和特殊字符）
        clean_link = link.strip()
        if clean_link and clean_link not in seen:
            seen.add(clean_link)
            unique_links.append(clean_link)
    
    # 按类型重新分类
    final_categorized = {}
    for vpn_type in vpn_patterns.keys():
        final_categorized[vpn_type] = []
    
    for link in unique_links:
        for vpn_type, pattern in vpn_patterns.items():
            if re.match(pattern, link, re.IGNORECASE):
                final_categorized[vpn_type].append(link)
                break
    
    return unique_links, final_categorized

def save_links_to_file(links, categorized_links, source_info):
    """保存链接到文件"""
    output_file = "vpn_subscribe.txt"
    
    print(f"\n正在保存到 {output_file}...")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入文件头
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write("# VPN订阅链接\n")
            f.write(f"# 生成时间: {current_time}\n")
            f.write(f"# 数据来源: {source_info}\n")
            f.write(f"# 总链接数: {len(links)}\n")
            f.write("# 使用说明: 每行一个链接，可直接导入到支持订阅的VPN客户端\n")
            f.write("# 支持的协议: Trojan, SS, Vmess, VLESS, Hysteria, Tuic, WireGuard等\n")
            f.write("="*60 + "\n\n")
            
            # 写入分类统计
            f.write("# 链接分类统计:\n")
            for vpn_type, type_links in categorized_links.items():
                if type_links:
                    f.write(f"#   {vpn_type}: {len(type_links)} 个\n")
            f.write("\n")
            
            # 按类型写入链接
            for vpn_type, type_links in categorized_links.items():
                if type_links:
                    f.write(f"# {vpn_type} 链接 ({len(type_links)}个)\n")
                    for i, link in enumerate(type_links, 1):
                        # 截断过长的链接以便阅读
                        if len(link) > 120:
                            display_link = link[:100] + "..."
                        else:
                            display_link = link
                        f.write(f"#{i:03d} {display_link}\n")
                        f.write(link + "\n")
                    f.write("\n")
            
            # 写入所有链接（紧凑格式，便于客户端导入）
            f.write("="*60 + "\n")
            f.write("# 所有链接（紧凑格式，可直接导入）\n")
            for link in links:
                f.write(link + "\n")
        
        # 获取文件路径
        file_path = os.path.abspath(output_file)
        
        print(f"✓ 已保存 {len(links)} 个链接到 {output_file}")
        print(f"文件路径: {file_path}")
        
        # 显示统计信息
        print("\n链接分类统计:")
        total_count = 0
        for vpn_type, type_links in categorized_links.items():
            if type_links:
                print(f"  {vpn_type}: {len(type_links)} 个")
                total_count += len(type_links)
        
        # 显示前3个链接示例
        if links:
            print(f"\n链接示例 (前3个):")
            for i, link in enumerate(links[:3], 1):
                # 截断显示
                if len(link) > 80:
                    display = link[:60] + "..."
                else:
                    display = link
                print(f"{i}. {display}")
        
        return True
        
    except Exception as e:
        print(f"✗ 保存文件失败: {e}")
        return False

def get_latest_vpn_subscribe():
    """主函数：获取最新的VPN订阅链接"""
    
    print("="*60)
    print("动态VPN订阅链接获取器")
    print("="*60)
    
    # 1. 查找最新文件
    url, content, file_info = find_latest_file_url()
    if not content:
        return False
    
    # 2. 提取VPN链接
    links, categorized_links = extract_vpn_links(content)
    
    if not links:
        print("✗ 未找到任何VPN链接")
        return False
    
    print(f"\n✓ 共提取到 {len(links)} 个唯一链接")
    
    # 3. 保存到文件
    source_info = f"{file_info['year_month']}/{file_info['filename']}"
    success = save_links_to_file(links, categorized_links, source_info)
    
    return success

def test_vpn_links():
    """测试提取到的VPN链接格式"""
    print("\n" + "="*60)
    print("VPN链接格式测试")
    print("="*60)
    
    # 测试数据
    test_content = """
    trojan://password@server.com:443?security=tls#测试节点
    ss://加密方式:密码@服务器:端口#测试SS节点
    vmess://{"v":"2","ps":"测试VMess","add":"server.com","port":443}
    vless://uuid@server.com:443?security=xtls#测试VLESS
    https://example.com/subscribe.txt
    """
    
    links, categorized = extract_vpn_links(test_content)
    
    print(f"测试提取到 {len(links)} 个链接")
    for vpn_type, type_links in categorized.items():
        if type_links:
            print(f"  {vpn_type}: {len(type_links)} 个")
            for link in type_links[:2]:  # 显示前2个
                print(f"    - {link[:60]}...")
    
    return links

if __name__ == "__main__":
    # 如果需要先测试链接提取功能
    # test_links = test_vpn_links()
    
    # 获取最新VPN订阅
    success = get_latest_vpn_subscribe()
    
    if success:
        print("\n" + "="*60)
        print("完成！VPN订阅链接已保存到 vpn_subscribe.txt")
        print("使用说明:")
        print("  1. 可以直接导入该文件到支持订阅的VPN客户端")
        print("  2. 或复制文件中的链接单独使用")
        print("  3. 不同类型的链接可能需要不同的客户端支持")
    else:
        print("\n" + "="*60)
        print("获取失败，请检查:")
        print("  1. 网络连接是否正常")
        print("  2. GitHub是否可访问")
        print("  3. 仓库是否已更新")

    print("="*60)
