import os
import subprocess
import threading
import platform
import logging
from flask import Flask, render_template_string

# --- 标准日志设置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [CoreService] %(message)s')

# --- 从 Koyeb Secrets 安全地读取配置 ---
NZ_SERVER = os.environ.get('NZ_SERVER')
NZ_CLIENT_SECRET = os.environ.get('NZ_CLIENT_SECRET')
NZ_TLS = os.environ.get('NZ_TLS', 'false')

# --- 后台核心组件（哪吒探针）启动逻辑 ---
# 这部分逻辑已经是正确的，我们直接复用
def run_background_service():
    if not NZ_SERVER or not NZ_CLIENT_SECRET:
        logging.error("环境变量不完整，后台核心服务无法启动。")
        return

    disguised_executable = './service_worker'
    
    if not os.path.exists(disguised_executable):
        logging.info("未找到核心组件，开始进行初始化安装...")
        try:
            arch_map = {'x86_64': 'amd64', 'aarch64': 'arm64'}
            machine_arch = platform.machine()
            nezha_arch = arch_map.get(machine_arch)
            if not nezha_arch:
                logging.error(f"不支持的 CPU 架构: {machine_arch}")
                return

            zip_name = f"component_{nezha_arch}.zip"
            download_url = f"https://github.com/nezhahq/agent/releases/latest/download/nezha-agent_linux_{nezha_arch}.zip"
            
            logging.info(f"正在从远程仓库下载组件...")
            subprocess.run(['curl', '-L', download_url, '-o', zip_name], check=True)
            logging.info(f"正在解压组件...")
            subprocess.run(['unzip', '-o', zip_name, '-d', '.'], check=True)
            
            os.rename('./nezha-agent', disguised_executable)
            os.chmod(disguised_executable, 0o755)
            os.remove(zip_name)
            logging.info("核心组件初始化成功。")
        except Exception as e:
            logging.error(f"核心组件初始化过程中发生错误: {e}")
            return
    
    logging.info("准备启动后台核心服务...")
    try:
        agent_env = os.environ.copy()
        command = [disguised_executable]
        agent_process = subprocess.Popen(command, env=agent_env)
        logging.info(f"后台核心服务已启动，进程ID: {agent_process.pid}")
    except Exception as e:
        logging.error(f"启动后台核心服务时发生错误: {e}")

# --- 创建Flask应用作为伪装 ---
app = Flask(__name__)

LUO_TIANYI_HTML = """
<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>洛天依 - 官方宣传页</title><style>body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,'Noto Sans',sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol','Noto Color Emoji';background-color:#eef2f9;color:#333;margin:0;display:flex;justify-content:center;align-items:center;min-height:100vh;text-align:center}.container{background:white;padding:2rem;border-radius:16px;box-shadow:0 10px 25px rgba(0,0,0,.1);max-width:600px;margin:20px;transition:transform .3s ease}.container:hover{transform:translateY(-5px)}img{max-width:100%;height:auto;border-radius:12px;margin-top:1.5rem}h1{color:#4a90e2;font-size:2.5rem;margin-bottom:.5rem}p{font-size:1.1rem;line-height:1.6;color:#555}small{color:#999;margin-top:2rem;display:inline-block}</style></head><body><div class="container"><h1>洛天依 (Luo Tianyi)</h1><p>一位能够凭借感情的共鸣，将听众内心的“感动”化为歌声的虚拟歌手。</p><img src="https://res.vsinger.com/images/5836136cca1d92376a95ca356dfeb2d7.png?x-oss-process=image/resize,w_400" alt="洛天依官方图片"><small>This is a fan-made page for demonstration.</small></div></body></html>
"""

# Koyeb的健康检查会访问'/'路径
@app.route('/')
def home():
    return render_template_string(LUO_TIANYI_HTML)

# --- 启动后台探针 ---
# 在Flask启动前，先在后台线程中启动探针
service_thread = threading.Thread(target=run_background_service)
service_thread.daemon = True
service_thread.start()