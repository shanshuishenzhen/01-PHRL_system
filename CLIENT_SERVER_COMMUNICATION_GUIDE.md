# 📡 PH&RL 客户端与服务器通信指南

## 🎯 概述

PH&RL考试系统采用**C/S架构**，客户端通过HTTP/HTTPS协议与服务器进行通信。本文档详细说明通信实现方式、配置要求和操作步骤。

## 🏗️ 通信架构

### 架构图
```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐
│   客户端        │ ◄──────────────► │   服务器端      │
│ (Exam Client)   │                  │ (Exam Server)   │
├─────────────────┤                  ├─────────────────┤
│ • 考试界面      │                  │ • 考试管理      │
│ • 答题功能      │                  │ • 题库管理      │
│ • 防作弊       │                  │ • 阅卷中心      │
│ • 本地存储      │                  │ • 用户管理      │
└─────────────────┘                  └─────────────────┘
```

### 通信特点
- **协议**：HTTP/HTTPS RESTful API
- **数据格式**：JSON
- **认证方式**：Bearer Token + 隐藏管理员
- **连接模式**：长连接 + 心跳检测
- **容错机制**：自动重试 + 离线缓存

## ⚙️ 配置要求

### 1. 网络环境要求

#### **基本要求**
- **网络类型**：局域网（LAN）
- **协议支持**：TCP/IP
- **端口要求**：默认5000端口（可配置）
- **带宽要求**：最低10Mbps（推荐100Mbps）

#### **防火墙配置**
```bash
# Windows防火墙规则（管理员权限执行）
netsh advfirewall firewall add rule name="PH&RL Exam Server" dir=in action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name="PH&RL Exam Client" dir=out action=allow protocol=TCP remoteport=5000
```

#### **网络拓扑要求**
```
服务器 (192.168.1.100:5000)
    │
    ├── 交换机/路由器
    │
    ├── 客户机1 (192.168.1.101)
    ├── 客户机2 (192.168.1.102)
    ├── ...
    └── 客户机N (192.168.1.1xx)
```

### 2. 服务器端配置

#### **硬件要求**
- **CPU**：4核心以上
- **内存**：8GB以上
- **存储**：100GB以上SSD
- **网络**：千兆网卡

#### **软件要求**
- **操作系统**：Windows 10/11 或 Windows Server 2019+
- **Python**：3.8+
- **数据库**：SQLite/MySQL
- **Web服务器**：内置Flask服务器

#### **服务器启动**
```bash
# 进入服务器目录
cd D:\01-PHRH_system

# 启动考试管理服务
python exam_management/app.py

# 启动题库管理服务
python question_bank_web/app.py

# 启动阅卷中心服务
cd grading_center/server
npm start
```

### 3. 客户端配置

#### **硬件要求**
- **CPU**：双核心以上
- **内存**：4GB以上
- **存储**：2GB以上
- **网络**：百兆网卡

#### **软件要求**
- **操作系统**：Windows 10/11
- **Python**：3.8+（打包后不需要）
- **显示器**：1024x768以上分辨率

## 🔧 配置操作

### 1. 服务器地址配置

#### **方法一：配置文件修改**
编辑 `standalone_client/config/client_config.json`：
```json
{
    "server": {
        "host": "192.168.1.100",
        "port": 5000,
        "protocol": "http",
        "timeout": 30,
        "retry_count": 3,
        "retry_delay": 5
    }
}
```

#### **方法二：界面配置**
1. 启动客户端
2. 在登录界面点击"服务器配置"
3. 填写服务器信息：
   - **服务器地址**：192.168.1.100
   - **端口**：5000
   - **协议**：http
   - **超时时间**：30秒
4. 点击"测试连接"验证
5. 点击"保存"应用配置

#### **方法三：命令行配置**
```python
# 使用Python脚本配置
from standalone_client.core.config import client_config

client_config.set('server.host', '192.168.1.100')
client_config.set('server.port', 5000)
client_config.set('server.protocol', 'http')
client_config.save()
```

### 2. 网络连接测试

#### **连接测试脚本**
创建 `test_connection.py`：
```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "standalone_client"))

from utils.network import NetworkUtils
from core.config import client_config

def test_connection():
    # 获取服务器配置
    host = client_config.get('server.host')
    port = client_config.get('server.port')
    server_url = client_config.get_server_url()
    
    print(f"🔍 测试服务器连接: {server_url}")
    
    # 测试网络连接
    print("1. 测试互联网连接...")
    internet_ok = NetworkUtils.check_internet_connection()
    print(f"   结果: {'✅ 正常' if internet_ok else '❌ 异常'}")
    
    # 测试服务器端口
    print(f"2. 测试服务器端口 {host}:{port}...")
    port_ok = NetworkUtils.test_port_open(host, port)
    print(f"   结果: {'✅ 开放' if port_ok else '❌ 关闭'}")
    
    # 测试服务器响应
    print(f"3. 测试服务器响应 {server_url}...")
    ping_time = NetworkUtils.ping_server(f"{server_url}/api/ping")
    if ping_time:
        print(f"   结果: ✅ 响应时间 {ping_time:.2f}ms")
    else:
        print(f"   结果: ❌ 无响应")
    
    return port_ok and ping_time is not None

if __name__ == "__main__":
    success = test_connection()
    print(f"\n📊 连接测试: {'✅ 成功' if success else '❌ 失败'}")
```

运行测试：
```bash
python test_connection.py
```

### 3. 批量客户端配置

#### **配置模板**
创建 `client_config_template.json`：
```json
{
    "server": {
        "host": "{{SERVER_IP}}",
        "port": 5000,
        "protocol": "http",
        "timeout": 30,
        "retry_count": 3,
        "retry_delay": 5
    },
    "app": {
        "name": "PH&RL 考试客户端",
        "version": "1.0.0",
        "debug": false
    },
    "ui": {
        "window_size": "1024x768",
        "fullscreen_exam": true,
        "theme_color": "#2196F3"
    },
    "security": {
        "enable_anti_cheat": true,
        "enable_encryption": true
    }
}
```

#### **批量配置脚本**
创建 `deploy_config.py`：
```python
#!/usr/bin/env python3
import json
import shutil
from pathlib import Path

def deploy_config(server_ip, target_dirs):
    """批量部署客户端配置"""
    
    # 读取模板
    template_path = Path("client_config_template.json")
    with open(template_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 替换服务器IP
    config['server']['host'] = server_ip
    
    # 部署到各个客户端目录
    for target_dir in target_dirs:
        target_path = Path(target_dir) / "config" / "client_config.json"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 配置已部署到: {target_path}")

# 使用示例
if __name__ == "__main__":
    server_ip = "192.168.1.100"
    client_dirs = [
        "D:/ExamClient_PC01",
        "D:/ExamClient_PC02", 
        "D:/ExamClient_PC03"
    ]
    
    deploy_config(server_ip, client_dirs)
```

## 🔌 API接口说明

### 1. 认证接口

#### **登录**
```http
POST /api/login
Content-Type: application/json

{
    "username": "student001",
    "password": "password123"
}

Response:
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user_info": {
        "id": "user_123",
        "username": "student001",
        "role": "student"
    }
}
```

#### **登出**
```http
POST /api/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response:
{
    "success": true,
    "message": "登出成功"
}
```

### 2. 考试接口

#### **获取考试列表**
```http
GET /api/exams?student_id=user_123
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response:
{
    "success": true,
    "exams": [
        {
            "id": "exam_001",
            "name": "Python基础测试",
            "duration": 60,
            "total_score": 100,
            "status": "available"
        }
    ]
}
```

#### **获取考试详情**
```http
GET /api/exams/exam_001
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response:
{
    "success": true,
    "exam": {
        "id": "exam_001",
        "name": "Python基础测试",
        "duration": 60,
        "questions": [
            {
                "id": "q1",
                "type": "single_choice",
                "content": "Python是什么类型的语言？",
                "options": ["编译型", "解释型", "汇编型"],
                "score": 10
            }
        ]
    }
}
```

### 3. 答题接口

#### **提交答案**
```http
POST /api/exams/answer
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
    "exam_id": "exam_001",
    "question_id": "q1",
    "answer": "B",
    "timestamp": 1641234567.89
}

Response:
{
    "success": true,
    "message": "答案已保存"
}
```

#### **提交考试**
```http
POST /api/exams/submit
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
    "exam_id": "exam_001",
    "answers": {
        "q1": "B",
        "q2": ["A", "C"],
        "q3": "这是简答题答案"
    },
    "submit_time": 1641234567.89
}

Response:
{
    "success": true,
    "message": "考试提交成功",
    "score": 85
}
```

## 🛠️ 故障排除

### 1. 常见问题

#### **连接超时**
```
错误：Connection timeout
原因：网络延迟或服务器无响应
解决：
1. 检查网络连接
2. 增加超时时间
3. 检查服务器状态
```

#### **端口被占用**
```
错误：Port 5000 already in use
原因：端口被其他程序占用
解决：
1. 更换端口号
2. 关闭占用程序
3. 重启服务器
```

#### **认证失败**
```
错误：Authentication failed
原因：用户名密码错误或token过期
解决：
1. 检查登录凭据
2. 重新登录获取token
3. 检查用户权限
```

### 2. 诊断工具

#### **网络诊断脚本**
```python
# network_diagnosis.py
import subprocess
import socket
from utils.network import NetworkUtils

def diagnose_network():
    print("🔍 网络诊断开始...")
    
    # 1. 检查本地网络
    local_ip = NetworkUtils.get_local_ip()
    print(f"本地IP: {local_ip}")
    
    # 2. Ping服务器
    server_ip = "192.168.1.100"
    result = subprocess.run(['ping', '-n', '4', server_ip], 
                          capture_output=True, text=True)
    print(f"Ping结果: {'成功' if result.returncode == 0 else '失败'}")
    
    # 3. 检查端口
    port_open = NetworkUtils.test_port_open(server_ip, 5000)
    print(f"端口5000: {'开放' if port_open else '关闭'}")
    
    # 4. DNS解析
    try:
        socket.gethostbyname(server_ip)
        print("DNS解析: 正常")
    except:
        print("DNS解析: 异常")

if __name__ == "__main__":
    diagnose_network()
```

### 3. 日志分析

#### **客户端日志位置**
```
standalone_client/logs/
├── client.log          # 主日志
├── network.log         # 网络日志
├── api.log            # API调用日志
└── error.log          # 错误日志
```

#### **关键日志信息**
```bash
# 查看连接日志
grep "连接" standalone_client/logs/network.log

# 查看API调用
grep "API" standalone_client/logs/api.log

# 查看错误信息
tail -f standalone_client/logs/error.log
```

## 📋 部署检查清单

### 服务器端检查
- [ ] 服务器硬件配置满足要求
- [ ] 操作系统和软件环境就绪
- [ ] 防火墙端口已开放
- [ ] 服务进程正常运行
- [ ] 数据库连接正常
- [ ] API接口响应正常

### 客户端检查
- [ ] 网络连接正常
- [ ] 服务器地址配置正确
- [ ] 客户端软件安装完成
- [ ] 配置文件部署到位
- [ ] 连接测试通过
- [ ] 登录认证正常

### 网络环境检查
- [ ] 局域网连通性正常
- [ ] 带宽满足要求
- [ ] 延迟在可接受范围
- [ ] 防火墙规则配置正确
- [ ] 路由器/交换机配置正常

## 🚀 最佳实践

### 1. 性能优化
- 使用有线网络连接
- 配置合适的超时时间
- 启用请求缓存
- 优化数据传输格式

### 2. 安全建议
- 使用HTTPS协议（生产环境）
- 定期更新认证token
- 启用请求加密
- 监控异常连接

### 3. 运维建议
- 定期检查网络状态
- 监控服务器性能
- 备份重要配置
- 建立故障恢复机制

---

**📞 技术支持**：如遇问题请联系系统管理员或查看详细日志进行排查。
