#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API网关

统一管理所有模块的API接口，提供：
- 请求路由和转发
- 身份验证和授权
- 请求限流和缓存
- API监控和日志
- 负载均衡
- 错误处理
"""

import json
import time
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from functools import wraps
import requests
import redis
from collections import defaultdict, deque


class RateLimiter:
    """请求限流器"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.local_cache = defaultdict(deque)
        self.window_size = 60  # 1分钟窗口
    
    def is_allowed(self, key: str, limit: int, window: int = None) -> bool:
        """检查是否允许请求"""
        window = window or self.window_size
        now = time.time()
        
        if self.redis_client:
            return self._redis_rate_limit(key, limit, window, now)
        else:
            return self._local_rate_limit(key, limit, window, now)
    
    def _redis_rate_limit(self, key: str, limit: int, window: int, now: float) -> bool:
        """Redis实现的限流"""
        try:
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, now - window)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, window)
            results = pipe.execute()
            
            current_requests = results[1]
            return current_requests < limit
        except:
            return True  # Redis失败时允许请求
    
    def _local_rate_limit(self, key: str, limit: int, window: int, now: float) -> bool:
        """本地内存实现的限流"""
        requests_queue = self.local_cache[key]
        
        # 清理过期请求
        while requests_queue and requests_queue[0] < now - window:
            requests_queue.popleft()
        
        # 检查是否超限
        if len(requests_queue) >= limit:
            return False
        
        # 添加当前请求
        requests_queue.append(now)
        return True


class APIGateway:
    """API网关"""
    
    def __init__(self, config_path: str = "config/gateway.json"):
        self.app = Flask(__name__)
        CORS(self.app)
        
        self.config_path = Path(config_path)
        self.setup_logging()
        self.load_config()
        
        # 初始化组件
        self.rate_limiter = RateLimiter()
        self.cache = {}
        self.service_registry = {}
        self.api_stats = defaultdict(int)
        
        # 设置路由
        self.setup_routes()
    
    def setup_logging(self):
        """设置日志"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "gateway.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self):
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.error(f"加载配置失败: {e}")
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "gateway": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": False
            },
            "services": {
                "question_bank": {
                    "url": "http://localhost:5000",
                    "prefix": "/api/questions",
                    "timeout": 30,
                    "rate_limit": 100
                },
                "exam_management": {
                    "url": "http://localhost:5001",
                    "prefix": "/api/exams",
                    "timeout": 30,
                    "rate_limit": 100
                },
                "grading_center": {
                    "url": "http://localhost:3000",
                    "prefix": "/api/grading",
                    "timeout": 60,
                    "rate_limit": 50
                },
                "user_management": {
                    "url": "http://localhost:5002",
                    "prefix": "/api/users",
                    "timeout": 30,
                    "rate_limit": 200
                },
                "score_statistics": {
                    "url": "http://localhost:5003",
                    "prefix": "/api/stats",
                    "timeout": 30,
                    "rate_limit": 100
                }
            },
            "auth": {
                "enabled": True,
                "jwt_secret": "your-secret-key",
                "token_expiry": 3600
            },
            "rate_limiting": {
                "enabled": True,
                "default_limit": 100,
                "window_size": 60
            },
            "caching": {
                "enabled": True,
                "default_ttl": 300,
                "max_size": 1000
            }
        }
    
    def save_config(self):
        """保存配置"""
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def setup_routes(self):
        """设置路由"""
        
        @self.app.before_request
        def before_request():
            """请求前处理"""
            g.start_time = time.time()
            g.request_id = hashlib.md5(f"{time.time()}{request.remote_addr}".encode()).hexdigest()[:8]
            
            # 记录请求
            self.logger.info(f"[{g.request_id}] {request.method} {request.path} from {request.remote_addr}")
        
        @self.app.after_request
        def after_request(response):
            """请求后处理"""
            duration = time.time() - g.start_time
            self.logger.info(f"[{g.request_id}] Response {response.status_code} in {duration:.3f}s")
            
            # 更新统计
            self.api_stats[f"{request.method}:{request.path}"] += 1
            self.api_stats["total_requests"] += 1
            
            return response
        
        @self.app.route('/health')
        def health_check():
            """健康检查"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": self.check_services_health()
            })
        
        @self.app.route('/stats')
        def get_stats():
            """获取统计信息"""
            return jsonify({
                "api_stats": dict(self.api_stats),
                "services": list(self.config["services"].keys()),
                "uptime": time.time() - self.start_time if hasattr(self, 'start_time') else 0
            })
        
        # 动态路由处理
        @self.app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
        def proxy_request(path):
            """代理请求到后端服务"""
            return self.handle_request(path)
    
    def handle_request(self, path: str):
        """处理请求"""
        try:
            # 1. 身份验证
            if self.config["auth"]["enabled"]:
                auth_result = self.authenticate_request()
                if not auth_result["success"]:
                    return jsonify({"error": auth_result["message"]}), 401
            
            # 2. 路由解析
            service_name, service_path = self.resolve_route(path)
            if not service_name:
                return jsonify({"error": "Service not found"}), 404
            
            # 3. 请求限流
            if self.config["rate_limiting"]["enabled"]:
                if not self.check_rate_limit(service_name):
                    return jsonify({"error": "Rate limit exceeded"}), 429
            
            # 4. 缓存检查
            cache_key = self.get_cache_key(service_name, service_path, request.args)
            if request.method == "GET" and self.config["caching"]["enabled"]:
                cached_response = self.get_cached_response(cache_key)
                if cached_response:
                    return cached_response
            
            # 5. 转发请求
            response = self.forward_request(service_name, service_path)
            
            # 6. 缓存响应
            if request.method == "GET" and response.status_code == 200:
                self.cache_response(cache_key, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"处理请求失败: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    def authenticate_request(self) -> Dict:
        """身份验证"""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return {"success": False, "message": "Missing authorization header"}
        
        try:
            # 简化的JWT验证（实际应该使用专业的JWT库）
            token = auth_header.replace('Bearer ', '')
            # 这里应该验证JWT token
            return {"success": True, "user_id": "user123"}
        except Exception as e:
            return {"success": False, "message": f"Invalid token: {e}"}
    
    def resolve_route(self, path: str) -> tuple:
        """解析路由"""
        for service_name, service_config in self.config["services"].items():
            prefix = service_config["prefix"].lstrip('/')
            if path.startswith(prefix):
                service_path = path[len(prefix):].lstrip('/')
                return service_name, service_path
        
        return None, None
    
    def check_rate_limit(self, service_name: str) -> bool:
        """检查请求限流"""
        service_config = self.config["services"].get(service_name, {})
        limit = service_config.get("rate_limit", self.config["rate_limiting"]["default_limit"])
        
        client_id = request.remote_addr
        key = f"rate_limit:{service_name}:{client_id}"
        
        return self.rate_limiter.is_allowed(key, limit)
    
    def get_cache_key(self, service_name: str, path: str, params: Dict) -> str:
        """生成缓存键"""
        params_str = json.dumps(sorted(params.items())) if params else ""
        return hashlib.md5(f"{service_name}:{path}:{params_str}".encode()).hexdigest()
    
    def get_cached_response(self, cache_key: str):
        """获取缓存响应"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            ttl = self.config["caching"]["default_ttl"]
            
            if time.time() - timestamp < ttl:
                self.logger.info(f"Cache hit: {cache_key}")
                return jsonify(cached_data)
            else:
                # 缓存过期
                del self.cache[cache_key]
        
        return None
    
    def cache_response(self, cache_key: str, response):
        """缓存响应"""
        try:
            if len(self.cache) >= self.config["caching"]["max_size"]:
                # 简单的LRU：删除最旧的缓存
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
            
            self.cache[cache_key] = (response.get_json(), time.time())
            self.logger.info(f"Cached response: {cache_key}")
        except Exception as e:
            self.logger.warning(f"缓存响应失败: {e}")
    
    def forward_request(self, service_name: str, service_path: str):
        """转发请求到后端服务"""
        service_config = self.config["services"][service_name]
        base_url = service_config["url"]
        timeout = service_config.get("timeout", 30)
        
        # 构建完整URL
        url = f"{base_url}/{service_path}".rstrip('/')
        if request.query_string:
            url += f"?{request.query_string.decode()}"
        
        # 准备请求数据
        headers = dict(request.headers)
        headers.pop('Host', None)  # 移除Host头
        
        data = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.get_data()
        
        try:
            # 发送请求
            response = requests.request(
                method=request.method,
                url=url,
                headers=headers,
                json=data if request.is_json else None,
                data=data if not request.is_json else None,
                timeout=timeout
            )
            
            # 构建响应
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            headers = [(name, value) for (name, value) in response.raw.headers.items()
                      if name.lower() not in excluded_headers]
            
            return response.content, response.status_code, headers
            
        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {service_name} {url}")
            return jsonify({"error": "Service timeout"}), 504
        except requests.exceptions.ConnectionError:
            self.logger.error(f"连接失败: {service_name} {url}")
            return jsonify({"error": "Service unavailable"}), 503
        except Exception as e:
            self.logger.error(f"转发请求失败: {e}")
            return jsonify({"error": "Service error"}), 502
    
    def check_services_health(self) -> Dict:
        """检查服务健康状态"""
        health_status = {}
        
        for service_name, service_config in self.config["services"].items():
            try:
                url = f"{service_config['url']}/health"
                response = requests.get(url, timeout=5)
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds()
                }
            except Exception as e:
                health_status[service_name] = {
                    "status": "unreachable",
                    "error": str(e)
                }
        
        return health_status
    
    def run(self):
        """启动网关"""
        self.start_time = time.time()
        
        gateway_config = self.config["gateway"]
        host = gateway_config.get("host", "0.0.0.0")
        port = gateway_config.get("port", 8000)
        debug = gateway_config.get("debug", False)
        
        self.logger.info(f"启动API网关: {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def main():
    """主函数"""
    gateway = APIGateway()
    
    print("🌐 API网关启动中...")
    print(f"配置文件: {gateway.config_path}")
    print(f"服务数量: {len(gateway.config['services'])}")
    
    try:
        gateway.run()
    except KeyboardInterrupt:
        print("\n🛑 API网关已停止")


if __name__ == "__main__":
    main()
