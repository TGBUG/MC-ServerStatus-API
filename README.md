# MC-ServerStaus-API
基于python fastapi开发的我的世界服务器监控API

### 使用方法
- 直接使用 python
  下载源码
  到app目录，执行
  ```shell
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  ```
- 使用 Docker
  执行
  ```shell
  docker pull tgbug/mc-server-status-api:latest
  //Docker默认没有图像与配置文件，记得挂载
  docker run -d -p 8000:8000 tgbug/mc-server-status-api -v $(pwd)/到你的配置文件:/app/conf.yaml -v $(pwd)/到你的图片目录:/app/imgs
  ```
  
### 请求方法
- Json接口：
  
  http://127.0.0.1:8000/json/你的服务器地址
  
  返回示例：
  
  ```json
    {
    
      "host": "127.0.0.1",
    
      "port": 25565,
    
      "players_online": 0,
    
      "players_max": 2025,
    
      "version_name": "BungeeCord 1.8.x-1.21.x",
     
      "version_protocol": 47,
  
      "motd": "This is MOTD",
    
      "online": true,
    
      "latency": 87.7833999984432
      
    }
  ```
  
- 图片接口：
  
  http://127.0.0.1:8000/img/你的服务器地址?server_name=我的服务器
  
  或
  
  http://127.0.0.1:8000/img/你的服务器地址/你需要的背景图编号?server_name=我的服务器
  
  (不指定要哪张背景图时是从所有背景图中随机一张；server_name缺省时默认值为Minecraft服务器)

### 配置文件
conf.yaml
```yaml
  rate_limit:
  
    max_requests_per_minute: 60  # 每分钟最大请求量
    

  cache:
  
    ttl_seconds: 600  # 缓存存活时间
    
    max_memory_mb: 128  # 最大内存占用
    
    min_memory_margin_mb: 6  # 当剩余值小于多少时触发清理
    
    max_disk_cache_mb: 512  # 最大磁盘占用
    
    min_disk_free_mb: 6  # 当剩余值小于多少时触发清理

  paths:
  
    img_dir: imgs  # 背景图目录，不建议修改
    
    img_cache_dir: img_cache  # img接口缓存目录，不建议修改
```
