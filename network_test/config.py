import json
import os
from pathlib import Path

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent / 'data' / 'network_test_config.json'

# 初始化配置数据
config_data = {
    'ADMIN_USERS': [],
    'AUTHORIZED_USERS': [],
    'SERVERS': []
}

# 从主配置获取管理员列表（如果可用）
try:
    from config import config as main_config
    if main_config.ADMIN_IDS:
        config_data['ADMIN_USERS'] = main_config.ADMIN_IDS.copy()
except ImportError:
    pass

# 如果配置文件存在，加载它
if CONFIG_FILE.exists():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            config_data.update(loaded_data)
    except Exception as e:
        print(f"加载网络测试配置失败: {e}")

ADMIN_USERS = config_data.get('ADMIN_USERS', [])
AUTHORIZED_USERS = config_data.get('AUTHORIZED_USERS', [])
SERVERS = config_data.get('SERVERS', [])

def save_config():
    """保存配置到文件"""
    # 确保目录存在
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    config_data['AUTHORIZED_USERS'] = AUTHORIZED_USERS
    config_data['SERVERS'] = SERVERS
    config_data['ADMIN_USERS'] = ADMIN_USERS
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
