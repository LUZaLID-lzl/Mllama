**Ubuntu连上usb之后，调用adb devices出现如下的错误**

![image-20240514111432597](image-20240514111432597.png)



**lsusb查看设备的device ID**

![image-20240514111519244](image-20240514111519244.png)

比如这个标红的就是插入的设备

添加udev规则,通过添加udev规则让普通用户也能访问。

```
sudo vi /etc/udev/rules.d/51-android.rules
```

在其中添加SUBSYSTEM=="usb", ATTR{idVendor}=="0e8d", MODE="0666", GROUP="plugdev"

只需要改动idVendor为ID前半部分即可



**重启udev服务**
sudo udevadm control --reload-rules
sudo service udev restart