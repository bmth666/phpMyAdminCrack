# phpMyAdmin 弱口令爆破工具

在网上找了一圈，发现phpMyAdmin的弱口令爆破工具已经是好几年前的了，比较新的phpmyadmin版本根本无法使用，网上也没有找到好用的脚本

这里重新编写了面向对象的重构版本，支持全版本phpMyAdmin爆破和未授权检测，具备完善的进度显示和日志功能，**90%代码由Cursor实现(AI太好用了)**



## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 单目标测试
python main.py -u http://example.com/

# 批量测试（10线程）
python main.py -f url.txt -t 10

# 详细模式
python main.py -f url.txt -t 10 -v
```

## 项目结构

```
phpmyadmin_crack/
├── src/                   源代码（11个模块）
│   ├── cli.py             命令行接口
│   ├── config.py          配置管理
│   ├── dict_loader.py     字典加载
│   ├── url_validator.py   URL验证
│   ├── proxy_manager.py   代理管理
│   ├── pma_detector.py    检测器（版本、未授权访问）
│   ├── pma_cracker.py     爆破核心
│   ├── result_manager.py  结果管理
│   ├── task_executor.py   任务执行
│   ├── progress_bar.py    实时进度条
│   ├── color_helper.py    颜色输出
│   └── logger.py          日志记录
├── wordlists/             字典目录
│   ├── username.txt       用户名字典
│   ├── password.txt       密码字典
│   └── dicts.txt          路径字典
├── results/               结果文件目录（自动生成）
├── logs/                  日志文件目录（自动生成）
├── main.py                主入口
├── url.txt                目标URL列表
└── requirements.txt       依赖包
```

## 核心功能

### 🎯 智能识别

- **Title标签识别** - 通过`<title>`标签精准判断phpMyAdmin
- **三层版本获取**
  1. `?v=版本号` 参数
  2. `/doc/html/index.html` 文档页面
  3. `set_session` 字段判断
- **版本自动适配** - 4.8.0前后自动切换登录方式
- **未授权访问检测** - 自动发现高危漏洞（无需登录即可访问）

## 命令行参数

```bash
python main.py [-h] (-u URL | -f FILE) [--proxy PROXY] [-t N] 
               [-o FILE] [--timeout SEC] [-v]
```

![image-20251014150926587](assets/image-20251014150926587.png)

### 必需参数（二选一）

- `-u URL` - 单个目标URL
- `-f FILE` - URL文件路径

### 可选参数
- `--proxy PROXY` - SOCKS5/HTTP代理地址
- `-t N` - 线程数量（1-50，默认1）
- `-o FILE` - 结果文件名（自动保存到results目录）
- `--timeout SEC` - 超时时间（1-60秒，默认5）
- `-v` - 详细模式

## 使用示例

### 基础用法
```bash
# 单目标
python main.py -u http://192.168.1.100/

# 批量（单线程）
python main.py -f url.txt

# 批量（多线程）
python main.py -f url.txt -t 10
```

### 使用代理

```bash
# SOCKS5
python main.py -f url.txt --proxy socks5://127.0.0.1:1080

# HTTP
python main.py -f url.txt --proxy http://127.0.0.1:8080

# 带认证
python main.py -f url.txt --proxy socks5://user:pass@127.0.0.1:1080
```

![image-20251015101954683](assets/image-20251015101954683.png)

### 高级用法

```bash
# 自定义配置
python main.py -f url.txt -t 10 --timeout 8 -o myresult.txt

# 详细模式
python main.py -f url.txt -t 10 -v

# 完整配置
python main.py -f url.txt -t 10 --timeout 8 -o myresult.txt -v
```

结果如下：

![image-20251014141736760](assets/image-20251014141736760.png)

![image-20251014141943758](assets/image-20251014141943758.png)

## 文件说明

### 字典文件

可以自定义字典，想要爆破成功，字典也是很重要滴。~~纯看运气~~

**wordlists/username.txt** - 用户名字典

```
root
mysql
admin
test
```

**wordlists/password.txt** - 密码字典

```
123456
admin
root
password
```

**wordlists/dicts.txt** - 路径字典

```
/pma/
/phpMyAdmin/
/phpmyadmin/
/mysqladmin/
```

### 结果文件

保存在`results/`目录，包含所有成功的爆破结果和未授权访问发现。

### 日志文件

保存在`logs/`目录，记录所有详细操作过程。

## 版本支持

### 支持范围
- phpMyAdmin 4.0.0 - 4.7.x
- phpMyAdmin 4.8.0 - 最新版本
- 未知版本（智能判断）

### 登录方式

| 版本 | 参数 | Cookie | 验证 |
|------|------|--------|------|
| < 4.8.0 | token, username, password | 无 | 302直接成功 |
| ≥ 4.8.0 | token, username, password, set_session | phpMyAdmin | 302直接成功 |
| 未知版本 | 智能判断 | 完整提取（4个） | 302后验证 |

## 注意事项

1. ⚠️ **仅用于授权测试** - 未经授权的测试违法
2. 📊 **线程控制** - 建议5-20线程
3. 🔒 **代理使用** - 使用SOCKS需安装pysocks
4. 📁 **目录创建** - results和logs目录会自动创建
5. 💾 **定期清理** - 注意清理历史日志和结果文件

## 许可证

本工具仅用于授权的安全测试，使用者应遵守当地法律法规。

