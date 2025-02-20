

要在Ubuntu上安装AppImage文件，你可以遵循以下步骤：

1：使AppImage文件可执行：

```
chmod u+x YourApp.AppImage
```

2：运行AppImage文件：

```
./YourApp.AppImage
```



### 如何创建快捷方式

1.创建快捷方式文件

```
touch wechat.desktop
```



2.编辑文件 修改以下内容

```
[Desktop Entry]
Name=IntelliJ IDEA
Comment=IntelliJ IDEA
Exec=/home/liziluo/LUZaLID/quickStart/sh/wechat.sh
Icon=/home/liziluo/LUZaLID/quickStart/png/wechat.png
Terminal=false
Type=Application
Categories=Developer;
```

"Exec"是执⾏脚本的路径，“Icon”是图标路径。 

给此⽂件添加执⾏权限，双击就能够启动idea了

```
chmod u+x wechat.desktop 
```



3.如果要在应⽤列表中显⽰,执行以下操作

```
cd /usr/share/applications 
sudo cp wechat.desktop ./
```



4.在终端想要直接执行，可以进行以下操作

```
sudo cp wechat.AppImage /usr/bin/wechat
```

执行完后，在终端输入wechat即可调出

