## camera启动速度分析调试

相机启动速度是ROM开发中性能优化的重要一环，与对比机(DL35)对比各个场景下的启动速度 ，通过用systrace工具抓取具体线程服务的工作状态，进行对比。

`liziluo@liziluo-mdsw:~/Android/Sdk/platform-tools/systrace$ python systrace.py -a com.mediatek.camera -o test1.html`

systrace通过-a指定包名来抓取对应的应用，-o指定生成的文件



查阅资料了解了相机启动的步骤：

- 从Touch屏幕到CameraManager中准备open camera
- 创建CaptureSession
- 启动预览



**从Touch屏幕到CameraManager中准备open camera**

App调用CameraManager.openCamera打开具体的cameraId，此步骤主要检查cameraId是否可以使用、没有冲突

从图片中可以看出，在准备open camera这个环节相较于对比机，在connectDevice中耗时多129ms 

本机：

![](a1.png)

对比机：

![](a2.png)

**创建CaptureSession**

会话主要创建CameraCaptureSessionImpl 

通过对比，两台机器在此环节耗时基本没有差距

位置：frameworks\base\core\java\android\hardware\camera2\impl\CameraDeviceImpl.java

![](c1.png)



**启动预览**

这一环节，threadloop中两台机器有较大的差距。在创建完session后，启动RequestThread，这个是在创建Camera3Device的时候初始化并运行的，

主要给halRequest赋值，让我们对比一下两台机器的执行时间

可以看到在其中两次的threadloop中，耗时相较于a10有170ms的差距，加上之前connectDevice的129ms，整体相较于a10有0.5s的差距，与redmine上对比视频相近，所以接下来将从这两个方面进行优化

本机：

![](b1.png)

对比机：

![](b2.png)

**优化**

从connectDevice以及threadloop中查看具体操作，可以得知主要的耗时是在binder transaction中

查阅发现在binder transaction这个链接过程会受到机器性能的影响，可能是由于打开camera时后台运行的进程不同，导致链接camera有不同的负载，让两台机器重新开机后，静止5分钟，因为a10和a11的开机服务不相同，在机器启动后需要的时间也不一样。所以待所有进程服务全部启动完毕，尽可能的不会影响camera的启动速度，再对比打开camera

最后测试两台机器打开速度几乎相同

