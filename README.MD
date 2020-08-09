# **_Tornado Demo_**

---

> 基于Python3.6.x, Tornado6.0 系列搭建，采用pipenv管理

### 项目安装
```shell script
pipenv install --dev
```

### 项目运行

```python3
python server.py --models=service --host=0.0.0.0 --port=8000
``` 

### 路由管理
```text
可以采用路由映射或路由装饰器实现
推荐使用路由装饰器
1. 路由映射：在modules目录下urls文件实现路由映射
2. 路由装饰器：在类上用Route装饰器即可
```

### 业务管理
```text
具体业务代码请写在: modules>dir 目录下
deme已写，参考。
```

### 配置文件
```text
配置文件放在conf目录下，可以采用py配置文件或yml配置文件
```

### 通用方法
```text
通用方法写在common下
```

### Api配置(微服务架构可用)
```text
可用py配置活yml配置
```

### 国际化配置
```text
locales目录实现
```

### 加密打包
```text
python代码可以通过build.py进行加密打包操作
```