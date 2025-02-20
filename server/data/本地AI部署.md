**[ollama](https://github.com/ollama/ollama)**：Get up and running with large language models.（运行和管理大语言模型）
打开终端直接下载安装
```
curl -fsSL https://ollama.com/install.sh | sh
```

下载完成之后安装需要的模型，这边以llama3.1:8b为安装模型
如果想要其他模型，可以到https://ollama.com/library里查找，目前国内很多厂商都开放了自己的模型，如文新一言等..
执行以下指令，启动ollama服务模式

```
ollama serve
```

然后可以安装需要的模型，例如llama3.1:8b，首次安装输入run即可自动帮忙下载安装，下载完成后后续可以直接启动

```
ollama run llama3.1:8b
```

执行ollama run之后，通过http://127.0.0.1:11434查看当前ollama是否在运行
ollama模型默认存储位置:
```
macOS: ~/.ollama/models 
Linux: **/usr/share/ollama/.ollama/models**
Windows: C:Users<username>.ollamamodels
```
更改存储路径(/path/to/ollama/models):
```
sudo mkdir /path/to/ollama/models
sudo chown -R root:root /path/to/ollama/models
sudo chmod -R 777 /path/to/ollama/models
sudo vim /etc/systemd/system/ollama.service
在ollama.service中加入Environment="OLLAMA_MODELS=/path/to/ollama/models" # 记得替换路径！！！
sudo systemctl daemon-reload
sudo systemctl restart ollama.service
sudo systemctl status ollama
```


**ChatBox** :https://chatboxai.app/zh/install?download=linux
启动
```
./tool/Chatbox/Chatbox-1.6.1-x86_64.AppImage
```


**[MaxKB](https://github.com/1Panel-dev/MaxKB)** ：国产前端展示界面，还包含本地知识库能功能
> 貌似后续使用要付费
```
docker run -d --name=maxkb --restart=always -p 8080:8080 -v ~/.maxkb:/var/lib/postgresql/data -v ~/.python-packages:/opt/maxkb/app/sandbox/python-packages cr2.fit2cloud.com/1panel/maxkb

# 用户名: admin
# 密码: MaxKB@123..
```

```
访问后台页面：docker ip:8080

eg:http://172.17.0.1:8080
```

**[open-webui](https://github.com/open-webui/open-webui)**  : 前端展示界面，类GPT画面，自带一个模型Alena
安装了docker的话可以直接通过以下命令下载open-webui
```
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

目前下载完成后发现无法获取到ollama本地的模型，更换docker的启动方式
更换之后open-webui的链接替换为http://localhost:8080/
```
docker run -d --network=host -v open-webui:/app/backend/data -e OLLAMA_BASE_URL=http://127.0.0.1:11434 --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```


**[Anythingllm](https://anythingllm.com/)**：本地知识库工具:支持上传txt、doc、pdf等文件格式
优点：
- 支持上传多类型文件，进行本地数据配置，可以形成小型数据库
- 图形化界面，三端应用支持
缺点：
- 不能自动上网读取内容，后续有新数据都要持续导入
```
启动方式:
cd ~/AnythingLLMDesktop
./start
```

注意：上传文件时不要用中文命名，会导致应用崩溃

