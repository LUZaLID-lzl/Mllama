# Fingerprint指纹识别学习

最新推荐文章于 2024-11-11 09:56:09 发布

![](https://csdnimg.cn/release/blogv2/dist/pc/img/reprint.png)

[W歹匕示申W](https://blog.csdn.net/csh86277516 "W歹匕示申W") ![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCurrentTime2.png)于 2017-03-31 16:47:29 发布

![](https://csdnimg.cn/release/blogv2/dist/pc/img/articleReadEyes2.png)阅读量4w ![](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarCollect2.png)![](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarCollectionActive2.png)收藏 57

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newHeart2023Active.png) ![](https://csdnimg.cn/release/blogv2/dist/pc/img/newHeart2023Black.png)点赞数 11

分类专栏： [Android](https://blog.csdn.net/csh86277516/category_6253880.html)

[![](https://i-blog.csdnimg.cn/columns/default/20201014180756919.png?x-oss-process=image/resize,m_fixed,h_224,w_224)Android 专栏收录该内容](https://blog.csdn.net/csh86277516/category_6253880.html "Android")

90 篇文章 5 订阅

订阅专栏

> Fingerprint模块[架构](http://lib.csdn.net/base/architecture "大型网站架构知识库")图如下，这里分为application，framework，fingerprintd和FingerprintHal这几个部分,不涉及指纹的IC库和驱动这部分,这部分逻辑由指纹厂商来实现，目前了解的并不多。   
> ![image](https://i-blog.csdnimg.cn/blog_migrate/6b7a40846ead09a0dc5b90a96e9d190d.png)
> 
> ##### 二、Fingerprint framework初始化流程
> 
> 在系统开机的时候，会启动各种Service，包括FingerprintService。从下图的开机log（sys_log.boot）中可以看出：   
> ![image](http://ohazfcl3s.bkt.clouddn.com/fp_init_log.png)  
> FingerprintService的启动在SystemServer.[Java](http://lib.csdn.net/base/javase "Java SE知识库")的startOtherService方法中：

```
/**
     * Starts a miscellaneous grab bag of stuff that has yet to be refactored
     * and organized.
     */
    private void startOtherServices() {
        final Context context = mSystemContext;
        VibratorService vibrator = null;
        IMountService mountService = null;
        .......
        //启动FingerprintService
        if (mPackageManager.hasSystemFeature(PackageManager.FEATURE_FINGERPRINT)) {
            mSystemServiceManager.startService(FingerprintService.class);
        }
        ......



   
   
   
   



代码解释
```

这里会通过PackageManager来判断是否支持指纹功能，这个判断是N新加的，如果支持的话，需要在framework/native/data/ect/目录下添加[Android](http://lib.csdn.net/base/android "Android知识库").hardware.fingerprint.xml来支持该功能，这样才能启动FingerprintService。   
![image](http://ohazfcl3s.bkt.clouddn.com/fp_hardware.png)

这里启动的时候，会将FingerprintService添加到ServiceManager中去，如下图：   
![image](http://ohazfcl3s.bkt.clouddn.com/fp_service2.png)  
将FingerprintService添加到ServiceManager中后，在SystemServiceRegistry.java中静态代码块中注册服务的时候，可以从ServiceManager中获取FingerprintService的Binder对象，从而可以构造出FingerprintManager对象，这样app端就可以通过Context来获取FingerprintManager对象。   
![image](http://ohazfcl3s.bkt.clouddn.com/fp_service1.png)

这样，app端通过Context获取FingerprintManager，通过调用FingerprintManager的接口来实现相应的功能，FingerprintManager转调FingerprintService中方法，FingerprintService负责管理整个注册，识别、删除指纹、检查权限等流程的逻辑，FingerprintService调用fingerprintd的接口，通过fingerprintd和FingerprintHal层进行通信。

在FingerprintService的getFingerprintDaemon方法中有如下步骤：

//①获取fingerprintd

//②向fingerprintd注册回调函数mDaemonCallback

//③调用获取fingerprintd的openhal函数

//④建立fingerprint文件系统节点，设置节点访问权限，调用fingerprintd的setActiveGroup，将路径传下去。此路径一半用来存储指纹模板的图片等

```
public IFingerprintDaemon getFingerprintDaemon() {
        if (mDaemon == null) {
             //①获取fingerprintd
            mDaemon = IFingerprintDaemon.Stub.asInterface(ServiceManager.getService(FINGERPRINTD));
            if (mDaemon != null) {
                try {
                    mDaemon.asBinder().linkToDeath(this, 0);
                    //②向fingerprintd注册回调函数mDaemonCallback
                    mDaemon.init(mDaemonCallback);
                    //③调用获取fingerprintd的openhal函数
                    mHalDeviceId = mDaemon.openHal();
                    /*④建立fingerprint文件系统节点，设置节点访问权限，
                    调用fingerprintd的setActiveGroup，
                    将路径传下去。此路径一半用来存储指纹模板的图片等*/
                    if (mHalDeviceId != 0) {
                        updateActiveGroup(ActivityManager.getCurrentUser());
                    } else {
                        Slog.w(TAG, "Failed to open Fingerprint HAL!");
                        mDaemon = null;
                    }
                } catch (RemoteException e) {
                    Slog.e(TAG, "Failed to open fingeprintd HAL", e);
                    mDaemon = null; // try again later!
                }
            } else {
                Slog.w(TAG, "fingerprint service not available");
            }
        }
        return mDaemon;
    }



   
   
   
   

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

###### 1 FingerprintService在framework模块负责指纹的大部分逻辑，FingerprintService会在开机的时候初始化；

###### 2 application调用framework通过FingerprintManager接口即可实现；

###### 3 framework中FingerManager和FingerprintService的通信使用Binder机制实现，表现即使用aidl这个接口定义语言实现

###### 4 framework调往fingerprintd的同样属于Binder通信，两者分属于不同的进程。不过这部分跟java层Binder处理有点不一样，是java层往native层的调用。

> ##### 三、fingerprintd 部分的初始化

在system/core/fingerprintd目录下,有如下文件：   
![image](http://ohazfcl3s.bkt.clouddn.com/fingerprintd_1.png)

```
fingerprintd如果划分的比较细的话，可以分为四个部分：
1.fingerprintd.cpp   "负责将fingerprintd加入到ServiceManager中，以便FingerprintService能够获取"
2.IFingerprintDaemon.h/IFingerprintDaemon.cpp  "负责java层到fingerprintd的Binder通信"
3.FingerprintDaemonProxy.h/FingerprintDaemonProxy.cpp  "负责fingerprintd和Fignerprint hal层的通信"
4.IFingerprintDaemonCallback.h/IFingerprintDaemonCallback.cpp "负责将指纹的回调结果传给java层"



   
   
   
   



代码解释
```

###### fingerprintd在init.rc有相应的开机启动脚本，所以一开机就会跑它的main函数。fingerprintd作为一个独立的进程运行，负责将Framework和Hal层的通信连接起来。

![image](http://ohazfcl3s.bkt.clouddn.com/fpd_main.png)

fingerprintd 的main函数就是将fingerprintd添加到servicemanager中管理。然后开了一个线程，等待binder消息。

> ##### 四、接下来简单介绍下IFingerprintDaemon是如何跟framework通信的。

来看下IFingerprintDaemon.h文件：

```
17#ifndef IFINGERPRINT_DAEMON_H_
18#define IFINGERPRINT_DAEMON_H_
19
20#include <binder/IInterface.h>
21#include <binder/Parcel.h>
22
23namespace android {
24
25class IFingerprintDaemonCallback;
26
27/*
28* Abstract base class for native implementation of FingerprintService.
29*
30* Note: This must be kept manually in sync with IFingerprintDaemon.aidl
31*/
32class IFingerprintDaemon : public IInterface, public IBinder::DeathRecipient {
33    public:
34        enum {
35           AUTHENTICATE = IBinder::FIRST_CALL_TRANSACTION + 0,
36           CANCEL_AUTHENTICATION = IBinder::FIRST_CALL_TRANSACTION + 1,
37           ENROLL = IBinder::FIRST_CALL_TRANSACTION + 2,
38           CANCEL_ENROLLMENT = IBinder::FIRST_CALL_TRANSACTION + 3,
39           PRE_ENROLL = IBinder::FIRST_CALL_TRANSACTION + 4,
40           REMOVE = IBinder::FIRST_CALL_TRANSACTION + 5,
41           GET_AUTHENTICATOR_ID = IBinder::FIRST_CALL_TRANSACTION + 6,
42           SET_ACTIVE_GROUP = IBinder::FIRST_CALL_TRANSACTION + 7,
43           OPEN_HAL = IBinder::FIRST_CALL_TRANSACTION + 8,
44           CLOSE_HAL = IBinder::FIRST_CALL_TRANSACTION + 9,
45           INIT = IBinder::FIRST_CALL_TRANSACTION + 10,
46           POST_ENROLL = IBinder::FIRST_CALL_TRANSACTION + 11,
47           ENUMERATE = IBinder::FIRST_CALL_TRANSACTION + 12,
48        };
49
50        IFingerprintDaemon() { }
51        virtual ~IFingerprintDaemon() { }
52        virtual const android::String16& getInterfaceDescriptor() const;
53
54        // Binder interface methods
55        virtual void init(const sp<IFingerprintDaemonCallback>& callback) = 0;
56        virtual int32_t enroll(const uint8_t* token, ssize_t tokenLength, int32_t groupId,
57                int32_t timeout) = 0;
58        virtual uint64_t preEnroll() = 0;
59        virtual int32_t postEnroll() = 0;
60        virtual int32_t stopEnrollment() = 0;
61        virtual int32_t authenticate(uint64_t sessionId, uint32_t groupId) = 0;
62        virtual int32_t stopAuthentication() = 0;
63        virtual int32_t remove(int32_t fingerId, int32_t groupId) = 0;
64        virtual int32_t enumerate() = 0;
65        virtual uint64_t getAuthenticatorId() = 0;
66        virtual int32_t setActiveGroup(int32_t groupId, const uint8_t* path, ssize_t pathLen) = 0;
67        virtual int64_t openHal() = 0;
68        virtual int32_t closeHal() = 0;
69
70        // DECLARE_META_INTERFACE - C++ client interface not needed
71        static const android::String16 descriptor;
72        static void hal_notify_callback(const fingerprint_msg_t *msg);
73};
74
75// ----------------------------------------------------------------------------
76
77class BnFingerprintDaemon: public BnInterface<IFingerprintDaemon> {
78    public:
79       virtual status_t onTransact(uint32_t code, const Parcel& data, Parcel* reply,
80               uint32_t flags = 0);
81    private:
82       bool checkPermission(const String16& permission);
83};
84
85} // namespace android
86
87#endif // IFINGERPRINT_DAEMON_H_



   
   
   
   

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

java层到fingerprintd的通信这里同样是采用binder方式，注意到上面IFingerprintDaemon.h第30行的NOTE，需要手动保证IFingerprintDaemon.h文件与IFingerprintDaemon.aidl文件一致，由于java层aidl文件编译时会自动编译成IFingerprintDaemon.java文件。

> ##### 当添加接口来调用指纹底层暴露的接口，在IFingerprintDaemon.h文件中添加类似上面35行到68行的枚举，枚举的值需要与java层aidl自动生成的java文件中的枚举保持一致。另外还需要在上面68行处加上描述这些接口的纯虚函数（c++中的纯虚函数类似java的抽象方法，用于定义接口的规范，在C++中，一个具有纯虚函数的基类被称为抽象类）。

如下面截图对比，我们发现IFingerprintDaemon.cpp和java层aidl生成的IFingerprintDaemon.java在onTransact是基本一致的。这样我们也就明白了为什么上面说需要手动和IFingerprintDaemon.aidl保持同步了，这样方式类似我们平时在三方应用使用aidl文件，需要保持client端和server端aidl文件一致。

```
可以看到onTransact有四个参数
code ， data ，replay ， flags
code 是一个整形的唯一标识，用于区分执行哪个方法，客户端会传递此参数，告诉服务端执行哪个方法
data客户端传递过来的参数
replay服务器返回回去的值
flags标明是否有返回值，0为有（双向），1为没有（单向）



   
   
   
   



代码解释
```

![image](http://ohazfcl3s.bkt.clouddn.com/IFp_Daemon.png)

IFingerprintDaemon.aidl文件生成的IFingerprintDaemon.java文件   
![image](http://ohazfcl3s.bkt.clouddn.com/IFp_java.png)

> ##### 接着介绍下fingerprintd进程是如何和Fingerprint Hal层是如何传递数据的。

说到Hal层，即硬件抽象层，Android系统为HAL层中的模块接口定义了规范，所有工作于HAL的模块必须按照这个规范来编写模块接口，否则将无法正常访问硬件。   
![image](http://ohazfcl3s.bkt.clouddn.com/hal.png)

指纹的HAL层规范fingerprint.h在/hardware/libhardware/include/hardware/下可以看到。

我们注意到在fingerprint.h中定义了两个结构体，分别是fingerprint_device_t和fingerprint_module_t,如下图。   
![image](http://ohazfcl3s.bkt.clouddn.com/fp_h.png)

fingerprint_device_t结构体，用于描述指纹硬件设备；fingerprint_module_t结构体，用于描述指纹硬件模块。在FingerprintDaemonProxy.cpp就是通过拿到fingerprint_device_t这个结构体来和Fingerprint HAL层通信的。

当需要添加接口调用指纹底层时，在这个fingerprint.h中同样需要添加函数指针，然后通过FingerprintDaemonProxy.cpp中拿到这个fingerprint_device_t来调用fingerprint.h中定义的函数指针，也就相当于调用指纹HAL层。

我们重点看一下它的openHal（）函数。

![image](http://ohazfcl3s.bkt.clouddn.com/fp_openHalNew.png)

openHal的方法这里主要看上面三个部分：   
\- ①根据名称获取指纹hal层模块。hw_module这个一般由指纹芯片厂商根据 fingerprint.h实现，hw_get_module是由HAL框架提供的一个公用的函数，这个函数的主要功能是根据模块ID(module_id)去查找注册在当前系统中与id对应的硬件对象，然后载入(load)其相应的HAL层驱动模块的\*so文件。   
\- ②调用fingerprint_module_t的open函数   
\- ③向hal层注册消息回调函数，主要回调 注册指纹进度，识别结果，错误信息等等   
\- ④判断向hal层注册消息回调是否注册成功

 

## [Android Fingerprint -- HAL层的初始化工作](http://blog.csdn.net/sky1203850702/article/details/53694371)

  

**序文：如何调用Hal层库文件**

每个Hal层库文件有一个入口，即HAL_MODULE_INFO_SYM，上层在调用hal层库文件时会在/system/lib/hw/下面寻找对应库文件，找到对应库文件后便从入口HAL_MODULE_INFO_SYM调用Hal层里面的open, init, write, read等接口，Hal层再通过这个接口去读写设备节点。

#### 一、 fingerprint.default.so

* * *

1、上一篇讲 Frameworks层初始化指纹模块的时候，Fingerprintd 调用hw_get_module函数获取了一个fingerprint_module_t类型的[数据结构](http://lib.csdn.net/base/datastructure "算法与数据结构知识库")。 这个就是在fingerprint.default.so中，由指纹芯片厂商填充实现的。

```cpp
//根据名称获取指纹hal层模块。hw_module这个一般由指纹芯片厂商根据 fingerprint.h实现
if (0 != (err = hw_get_module(FINGERPRINT_HARDWARE_MODULE_ID, &hw_module))) {
    ALOGE("Can't open fingerprint HW Module, error: %d", err);
    return 0;
}






代码解释
```

我们继续往下看fingerprint.default.so。

```cpp
static struct hw_module_methods_t fingerprint_module_methods = {
.open = fingerprint_open,
};
 
fingerprint_module_t HAL_MODULE_INFO_SYM = {
    .common = {
        .tag                = HARDWARE_MODULE_TAG,
        .module_api_version = FINGERPRINT_MODULE_API_VERSION_2_0,
        .hal_api_version    = HARDWARE_HAL_API_VERSION,
        .id                 = FINGERPRINT_HARDWARE_MODULE_ID,
        .name               = "Fingerprint HAL",
        .author             = "xxx",
        .methods            = &fingerprint_module_methods,
        .dso                = NULL
    },
};






代码解释
```

hw_get_module就是根据.id = FINGERPRINT_HARDWARE_MODULE_ID这个id来找到对应的fingerprint_module_t。hal层可能有多个指纹芯片厂商的模块，可以根据这个id来做兼容，选择性的加载不同的指纹模组。

2、fingerprintd得到了相应的fingerprint_module_t，之后就会去调用它的open函数。我们来看一下初始化指纹最核心的fingerprint_open。

```cpp
static int fingerprint_open(const hw_module_t* module, const char __unused *id,
                        hw_device_t** device)
{
    ALOGV("fingerprint_open");
 
    if (device == NULL) {
        ALOGE("NULL device on open");
        return -EINVAL;
    }
 
    fingerprint_device_t *dev = (fingerprint_device_t *)
        malloc(sizeof(fingerprint_device_t));
    memset(dev, 0, sizeof(fingerprint_device_t));
 
    dev->common.tag = HARDWARE_DEVICE_TAG;
    dev->common.version = FINGERPRINT_MODULE_API_VERSION_2_0;
    dev->common.module = (struct hw_module_t*) module;
    dev->common.close = fingerprint_close;
 
    dev->pre_enroll = fingerprint_pre_enroll;
    dev->enroll = fingerprint_enroll;
    dev->post_enroll = fingerprint_post_enroll;
    dev->get_authenticator_id = fingerprint_get_auth_id;
    dev->cancel = fingerprint_cancel;
    dev->remove = fingerprint_remove;
    dev->set_active_group = fingerprint_set_active_group;
    dev->authenticate = fingerprint_authenticate;
    dev->set_notify = set_notify_callback;
    dev->notify = NULL;
 
    g_device = dev;
    if(g_device == NULL) {
        ALOGV("g_device is NULL");
    } else {
        ALOGV("g_device is not NULL");
    }
 
    *device = (hw_device_t*) dev;
    
    hal_init(mDevice)；
 
    return 0;
}




![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

就是填充实现[Android](http://lib.csdn.net/base/android "Android知识库") 在fingerprint_device.h定义fingerprint_device_t需要实现的这些接口。然后赋给指针device。上层，也就是fingerprintd，就能用这个device来操作hal层的指纹模块了。

#### 二、重要的hal_init函数。

* * *

hal init有如下几个重要的工作要做：

1、 hal_device_open()的工作很简单，就是打开指纹驱动层的设备节点，然后初始化一个用来接收驱动层消息的消息队列。当然在此之前，指纹的驱动层肯定已经正常probe，生成了相应的设备节点。

```cobol
fd = open(/dev/xxx_fp, O_RDWR);
...
TAILQ_INIT(&head);
...






代码解释
```

2、检查指纹芯片是否已经正常工作了（在驱动层probe阶段，就会给芯片上电复位，并且加载相应的指纹固件和配置，正常指纹芯片已经开始正常工作了）。如果没有正常工作，就会给芯片复位。将其重新拉到正常的工作状态。

```perl
    err = hal_get_fw_info(&download_fw_flag);
    if (err != GF_SUCCESS) {
        LOG_E(LOG_TAG "[%s] failed to get firmware info", __func__);
    }
    if (!download_fw_flag) {
        hal_reset_chip();
    }






代码解释
```

3、与指纹ta建立session，然后调用接口初始化指纹ta。

```r
result = TEEC_OpenSession(g_context, g_session,
             &UUID, TEEC_LOGIN_PUBLIC, NULL, &operation, NULL);
...
 
TEEC_Operation operation = { 0 };
operation.paramTypes = GF_CMD_TEEC_PARAM_TYPES;
operation.params[0].tmpref.buffer = GF_CMD_INIT;
operation.params[0].tmpref.size = len;
ret = TEEC_InvokeCommand(g_session, GF_OPERATION_ID, &operation, NULL);
...






代码解释
```

对android指纹模块不了解的人可能会问指纹ta是什么？我们先说一下TEE， Trusted Execution Environment (TEE)是主控芯片厂商（mtk，高通等）提供的一个安全的硬件运行环境。指纹ta就是运行在这样一个硬件安全环境下的程序。它保证了指纹敏感数据的安全性。

4、与指纹驱动层建立通信。这里给大家看一种基于netlink，巧妙而简洁的方式。

4.1.1、通信的接收端（hal层）做了哪些处理？我们往下看

```cpp
//初始化信号量 g_sem，配合消息队列，用于从消息接受者hal_netlink_recv
//到消息处理者handle_thread的消息传递
if (0 != sem_init(&g_sem, 0, 0)) {
    LOG_E(LOG_TAG, "[%s] init semaphore failed", __func__);
    break;
}
 
//消息处理线程handle_thread
if (pthread_create(&g_handle_thread, NULL, handle_thread, NULL) != 0) {
    LOG_E(LOG_TAG, "[%s] pthread_create failed", __func__);
    break;
}
//用ioctl的方式将netlink描述符g_netlink_route传递给驱动层。
//这样驱动层就能用这个g_netlink_route与hal层建立消息管道
if (ioctl(fd, GF_IOC_INIT, &g_netlink_route) != 0) {
    LOG_E(LOG_TAG, "[%s] GF_IOC_INIT ioctl failed", __func__);
    err = GF_ERROR_OPEN_DEVICE_FAILED;
    break;
}
LOG_I(LOG_TAG, "[%s] g_netlink_route = %d", __func__, g_netlink_route);
 
//消息接收线程hal_netlink_recv
if (pthread_create(&g_netlink_thread, NULL, hal_netlink_recv, NULL) != 0) {
    LOG_E(LOG_TAG, "[%s] pthread_create failed", __func__);
    break;
}




![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

4.1.2、我们先看消息接收线程hal_netlink_recv做了什么。

```csharp
        /* 初始化netlink并binder 下面这些都是netlink的标准流程*/
        g_netlink_sock_id = socket(AF_NETLINK, SOCK_RAW, g_netlink_route);
        if (g_netlink_sock_id < 0) {
            break;
        }
 
        memset(&local, 0, sizeof(struct sockaddr_nl));
        local.nl_family = AF_NETLINK;
        local.nl_pid = getpid();/*local process id*/
 
        local.nl_groups = 0;
 
        ret = bind(g_netlink_sock_id, (struct sockaddr*) &local, 
                    sizeof(struct sockaddr_nl));
        if (ret != 0) {
            break;
        }
        
 
        /* send init message */
        memset(&dest, 0, sizeof(struct sockaddr_nl));
        dest.nl_family = AF_NETLINK;
        dest.nl_pid = 0; /*destination is kernel so set to 0*/
        dest.nl_groups = 0;
 
        nlh = (struct nlmsghdr *) malloc(NLMSG_SPACE(MAX_NL_MSG_LEN));
        if (NULL == nlh) {
            LOG_E(LOG_TAG, "[%s] nlh out of memery", __func__);
            break;
        }
        nlh->nlmsg_len = NLMSG_SPACE(MAX_NL_MSG_LEN);
        nlh->nlmsg_pid = getpid();
        nlh->nlmsg_flags = 0;
        strcpy(NLMSG_DATA(nlh), "GF");
 
        iov.iov_base = (void*) nlh;
        iov.iov_len = nlh->nlmsg_len;
 
        memset(&msg, 0, sizeof(struct msghdr));
        msg.msg_iov = &iov;
        msg.msg_iovlen = 1;
        msg.msg_name = (void*) &dest;
        msg.msg_namelen = sizeof(struct sockaddr_nl);
        
        //发送一个包含pid的消息给驱动层，相当于握手，告诉驱动层，我这边已经准备ok了。
        if (sendmsg(g_netlink_sock_id, &msg, 0) < 0) {
            break;
        }
        LOG_D(LOG_TAG, "[%s] send init msg to kernel", __func__);
 
        /* 开启一个循环，接收来自驱动层的消息 */
        memset(nlh, 0, NLMSG_SPACE(MAX_NL_MSG_LEN));
        
        while (1) {
            //LOG_D(LOG_TAG, "here wait message from kernel");
            ret = recvmsg(g_netlink_sock_id, &msg, 0);
            if (ret < 0) {
                LOG_E(LOG_TAG, "[%s] recvmsg failed, ret %d", __func__, ret);
                continue;
            }
            if (0 == ret) {
                LOG_E(LOG_TAG, "[%s] recvmsg failed, ret %d", __func__, ret);
                continue;
            }
            value = *((char *) NLMSG_DATA(nlh));
            //根据消息类别做处理
            if (GF_NETLINK_TEST == value) {
                LOG_D(LOG_TAG, "[%s] received GF_NETLINK_TEST command", __func__);
 
            } else if (NETLINK_IRQ == value || NETLINK_SCREEN_OFF == value
                    || NETLINK_SCREEN_ON == value) {
                //如果是中断消息，或者亮灭屏事件，就把消息值push到消息队列。
                //然后post信号量，让消息处理线程去处理了。
                enqueue(value);
                sem_post(&g_netlink_sem);
                LOG_D(LOG_TAG, "[%s] send message : %d", __func__, value);
            } else {
                LOG_E(LOG_TAG, "[%s] wrong netlink command %d", __func__, value);
            }
        }




![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

4.1.3、再看处理线程，等待信号量，收到之后就从消息队列里边取出消息。然后根据不同的值调用相应的处理函数。

```csharp
void *handle_thread(void *handle) {
 
    while (1) {
        sem_wait(&g_netlink_sem);
 
        err = dequeue(&value);
        if (err != GF_SUCCESS) {
            continue;
        }
 
        if (GF_NETLINK_IRQ == value) {
            hal_irq();
 
        } else if (GF_NETLINK_SCREEN_OFF == value) {
            hal_screen_off();
 
        } else if (GF_NETLINK_SCREEN_ON == value) {
            hal_screen_on();
        }
    } 
}




![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

hal层的设计很清晰。由于中断来的很快，频率也很高，所以这边使用快速接收中断，缓存起来，再慢慢处理的方式处理中断事件，类似于内核中断上下文的处理方式。

4.2.1、讲到这里，肯定对驱动层怎么发送接收消息产生了好奇？本来打算在写驱动层的地方讲的，但是这样这部分内容就中断了，还是现在这里写完吧。很简单，直接看下面的代码注释就能理解。

```cpp
static int netlink_init(void)
{
    struct netlink_kernel_cfg cfg;
    memset(&cfg, 0, sizeof(struct netlink_kernel_cfg));
    cfg.input = netlink_recv;
    //创建netlink 驱动层的接收hal层消息函数，注意NETLINK_ROUTE要与hal层一致。
    g_dev->nl_sk = netlink_kernel_create(&init_net, NETLINK_ROUTE, &cfg);
}






代码解释
```

4.2.2、接收消息的处理：

```cpp
static void netlink_recv(struct sk_buff *__skb)
{
    
    skb = skb_get(__skb);
 
    //消息大于5byte才做处理
 
    if (skb->len >= NLMSG_SPACE(0)) {
        nlh = nlmsg_hdr(skb);
        memcpy(str, NLMSG_DATA(nlh), sizeof(str));
        //拿到了hal层穿下来的pid，保存起来。
        g_gf_dev->pid = nlh->nlmsg_pid;
        
    } else {
        debug(ERR_LOG, "[%s] : not enough data length\n", __func__);
    }
 
    kfree_skb(skb);
}




![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

4.2.3、收到中断或者亮灭屏事件，就调用netlink_send通知hal层：

```cpp
void netlink_send(const int command)
{
    //netlink kernel层发送消息的典型流程，就是构造一个消息结构体，然后
    //用api netlink_unicast发出去
    skb = alloc_skb(MAX_NL_MSG_LEN, GFP_ATOMIC);
    if (skb == NULL) {
        gf_debug(ERR_LOG, "[%s] : allocate skb failed\n", __func__);
        return;
    }
 
    nlh = nlmsg_put(skb, 0, 0, 0, MAX_NL_MSG_LEN, 0);
    if (!nlh) {
        kfree_skb(skb);
        return;
    }
 
    NETLINK_CB(skb).portid = 0;
    NETLINK_CB(skb).dst_group = 0;
    //消息类型的赋值，中断，亮灭屏等
    *(char *)NLMSG_DATA(nlh) = command;
    ret = netlink_unicast(g_gf_dev->nl_sk, skb, g_gf_dev->pid, MSG_DONTWAIT);
}




![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

这样，hal层和驱动层就建立好了通信管道。以后中断等事件就能从驱动层报给hal层，hal层会根据事件类型，做相应处理。

5、调用ta init，初始化ta。

6、开启看门狗，监听ic状态，如果ic挂了就重启ic。

至此，hal层就算初始化完毕了。接下来，上层就可以开始注册指纹了。

  

下面实例：：：：：：：：：：

 

## [Android 6.0指纹识别App开发demo](http://blog.csdn.net/createchance/article/details/51991764)

在[Android](http://lib.csdn.net/base/android "Android知识库") 6.0中google终于给[android](http://lib.csdn.net/base/android "Android知识库")系统加上了指纹识别的支持，这个功能在iPhone上早就已经实现了，并且在很多厂商的定制的ROM中也都自己内部实现这个功能了，这个功能来的有点晚啊。在google全新发布的nexus设备：nexus 5x和nexus 6p中都携带了一颗指纹识别芯片在设备的背面，如下图(图片来自网络)： 

![这里写图片描述](https://img-blog.csdn.net/20160722093726402)  
笔者手中的设备就是图上的那台黑色的nexus 5x，话说这台机器很是好看呢！手感超棒！   
废话不多说，下面我出一个指纹识别的demo app，并且详细说明怎么开发一个基于google api的指纹识别app。demo的源码在我的github上：   
https://github.com/CreateChance/AndroidFingerPrintDemo

## Android M中的指纹识别接口

这个是首先需要关注的问题，在实际动手开始写app之前需要知道最新的平台为我们提供了那些指纹识别的接口。所有的指纹识别接口全部在android.hardware.fingerprint这个包下，这个包中的类不是很多，如下：   
![这里写图片描述](https://img-blog.csdn.net/20160722094356687)  
api doc链接地址：   
https://developer.android.com/reference/android/hardware/fingerprint/package-summary.html   
大家最好FQ自己看下。   
上面的图中，我们看到这个包中总共有4个类，下面我们简要介绍一下他们：   
1.FingerprintManager：主要用来协调管理和访问指纹识别硬件设备   
2.FingerprintManager.AuthenticationCallback这个一个callback接口，当指纹认证后系统会回调这个接口通知app认证的结果是什么   
3.FingerprintManager.AuthenticationResult这是一个表示认证结果的类，会在回调接口中以参数给出   
4.FingerprintManager.CryptoObject这是一个加密的对象类，用来保证认证的安全性，这是一个重点，下面我们会分析。   
好了，到这里我们简要知道了android 6.0给出的指纹识别的接口不是很多，可以说是简短干练。

## 动手开发一个指纹识别app

现在，我们要动手写一个利用上面接口的指纹识别app，这个app界面很简单，就一个activity，这个activity上会激活指纹识别，然后提示用户按下指纹，并且会将认证的结果显示出来。

### 开始

在开始之前，我们需要知道使用指纹识别硬件的基本步骤：   
1.在AndroidManifest.xml中申明如下权限：

```
`<uses-permission android:name="android.permission.USE_FINGERPRINT"/>`
      
      
      
      



代码解释
```

2.获得FingerprintManager的对象引用   
3.在运行是检查设备指纹识别的兼容性，比如是否有指纹识别设备等。下面我们详细说一下上面的步骤：

#### 申明权限

这一步比较简单，只要在AndroidManifest.xml中添加上面说到的权限就可以了。

#### 获得FingerprintManager对象引用

这是app开发中获得系统服务对象的常用方式，如下：

```
// Using the Android Support Library v4
fingerprintManager = FingerprintManagerCompat.from(this);
// Using API level 23:
fingerprintManager = (FingerprintManager)getSystemService(Context.FINGERPRINT_SERVICE);



      
      
      
      



代码解释
```

上面给出两种方式，第一种是通过V4支持包获得兼容的对象引用，这是google推行的做法；还有就是直接使用api 23 framework中的接口获得对象引用。

#### 检查运行条件

要使得我们的指纹识别app能够正常运行，有一些条件是必须满足的。   
1）. API level 23   
指纹识别API是在api level 23也就是android 6.0中加入的，因此我们的app必须运行在这个系统版本之上。因此google推荐使用 Android Support Library v4包来获得FingerprintManagerCompat对象，因为在获得的时候这个包会检查当前系统平台的版本。   
2）. 硬件   
指纹识别肯定要求你的设备上有指纹识别的硬件，因此在运行时需要检查系统当中是不是有指纹识别的硬件：

```
if (!fingerprintManager.isHardwareDetected()) {
    // no fingerprint sensor is detected, show dialog to tell user.
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    builder.setTitle(R.string.no_sensor_dialog_title);
    builder.setMessage(R.string.no_sensor_dialog_message);
    builder.setIcon(android.R.drawable.stat_sys_warning);
    builder.setCancelable(false);
    builder.setNegativeButton(R.string.cancel_btn_dialog, new DialogInterface.OnClickListener() {
        @Override
        public void onClick(DialogInterface dialog, int which) {
            finish();
        }
    });
    // show this dialog.
    builder.create().show();
}



      
      
      
      

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

调用上面的接口接可以知道系统中是不是有一个这样的硬件，如果没有的话，那就需要做一些合适的事情，比如提示用户当前系统中没有指纹识别硬件等。   
3）. 当前设备必须是处于安全保护中的   
这个条件的意思是，你的设备必须是使用屏幕锁保护的，这个屏幕锁可以是password，PIN或者图案都行。为什么是这样呢？因为google原生的逻辑就是：想要使用指纹识别的话，必须首先使能屏幕锁才行，这个和android 5.0中的smart lock逻辑是一样的，这是因为google认为目前的指纹识别技术还是有不足之处，安全性还是不能和传统的方式比较的。   
我们可以使用下面的代码检查当前设备是不是处于安全保护中的：

```
KeyguardManager keyguardManager =(KeyguardManager)getSystemService(Context.KEYGUARD_SERVICE);
if (keyguardManager.isKeyguardSecure()) {
    // this device is secure.
}



      
      
      
      



代码解释
```

我们使用KeyguardManager的isKeyguardSecure接口就能知道。   
4）. 系统中是不是有注册的指纹   
在android 6.0中，普通app要想使用指纹识别功能的话，用户必须首先在setting中注册至少一个指纹才行，否则是不能使用的。所以这里我们需要检查当前系统中是不是已经有注册的指纹信息了：

```
if (!fingerprintManager.hasEnrolledFingerprints()) {
    // no fingerprint image has been enrolled.
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    builder.setTitle(R.string.no_fingerprint_enrolled_dialog_title);
    builder.setMessage(R.string.no_fingerprint_enrolled_dialog_message);
    builder.setIcon(android.R.drawable.stat_sys_warning);
    builder.setCancelable(false);
    builder.setNegativeButton(R.string.cancel_btn_dialog, new DialogInterface.OnClickListener() {
        @Override
        public void onClick(DialogInterface dialog, int which) {
            finish();
        }
    });
    // show this dialog
    builder.create().show();
}



      
      
      
      

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

如果用户还没有注册一个指纹的话，那么我们的app可以提示用户：如果想要使用指纹是功能，请再setting中注册一个你的指纹。这里需要啰嗦一句，如果你做过bluetooth或者其他设备开发的话，那么你知道你可以通过发送一个intent来启动bluetooth开启的界面，只要是声明了蓝牙的管理权限。但是，到目前位置google任然没有开放让普通app启动指纹注册界面的权限，这一点我们可以从setting的AndroidManifest中看到：

```
<activity android:name=".fingerprint.FingerprintSettings" android:exported="false"/>
<activity android:name=".fingerprint.FingerprintEnrollOnboard" android:exported="false"/>
<activity android:name=".fingerprint.FingerprintEnrollFindSensor" android:exported="false"/>
<activity android:name=".fingerprint.FingerprintEnrollEnrolling" android:exported="false"/>
<activity android:name=".fingerprint.FingerprintEnrollFinish" android:exported="false"/>
<activity android:name=".fingerprint.FingerprintEnrollIntroduction" android:exported="false" />
 
<activity android:name=".fingerprint.SetupFingerprintEnrollOnboard" android:exported="false"/>
<activity android:name=".fingerprint.SetupFingerprintEnrollFindSensor" android:exported="false"/>
<activity android:name=".fingerprint.SetupFingerprintEnrollEnrolling" android:exported="false"/>
<activity android:name=".fingerprint.SetupFingerprintEnrollFinish" android:exported="false"/>
<activity android:name=".fingerprint.SetupFingerprintEnrollIntroduction"
    android:exported="true"
    android:permission="android.permission.MANAGE_FINGERPRINT"
    android:theme="@style/SetupWizardDisableAppStartingTheme">
    <intent-filter>
        <action android:name="android.settings.FINGERPRINT_SETUP" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
</activity>



      
      
      
      

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

大部分的fingerprint设置界面都没有exporte，只有SetupFingerprintEnrollIntroduction，但是这个界面需要android.permission.MANAGE_FINGERPRINT这个权限，并且这个权限只能是系统app使用，这就直接防止第三方app启动这个界面了。（不知道日后google会不会开放这个权限。。。。。）

一个好的app，应该在运行时都检查一下上面的条件，防止app出现意外的错误。

### 扫描用户按下的指纹

要开始扫描用户按下的指纹是很简单的，只要调用FingerprintManager的authenticate方法即可，那么现在我们来看一下这个接口：   
![这里写图片描述](https://img-blog.csdn.net/20160722104416225)  
上图是google的api文档中的描述，现在我们挨个解释一下这些参数都是什么：   
1\. crypto这是一个加密类的对象，指纹扫描器会使用这个对象来判断认证结果的合法性。这个对象可以是null，但是这样的话，就意味这app无条件信任认证的结果，虽然从理论上这个过程可能被攻击，数据可以被篡改，这是app在这种情况下必须承担的风险。因此，建议这个参数不要置为null。这个类的实例化有点麻烦，主要使用javax的security接口实现，后面我的demo程序中会给出一个helper类，这个类封装内部实现的逻辑，开发者可以直接使用我的类简化实例化的过程。   
2\. cancel 这个是CancellationSignal类的一个对象，这个对象用来在指纹识别器扫描用户指纹的是时候取消当前的扫描操作，如果不取消的话，那么指纹扫描器会移植扫描直到超时（一般为30s，取决于具体的厂商实现），这样的话就会比较耗电。建议这个参数不要置为null。   
3\. flags 标识位，根据上图的文档描述，这个位暂时应该为0，这个标志位应该是保留将来使用的。   
4\. callback 这个是FingerprintManager.AuthenticationCallback类的对象，这个是这个接口中除了第一个参数之外最重要的参数了。当系统完成了指纹认证过程（失败或者成功都会）后，会回调这个对象中的接口，通知app认证的结果。这个参数不能为NULL。   
5\. handler 这是Handler类的对象，如果这个参数不为null的话，那么FingerprintManager将会使用这个handler中的looper来处理来自指纹识别硬件的消息。通常来讲，开发这不用提供这个参数，可以直接置为null，因为FingerprintManager会默认使用app的main looper来处理。

### 取消指纹扫描

上面我们提到了取消指纹扫描的操作，这个操作是很常见的。这个时候可以使用CancellationSignal这个类的cancel方法实现：   
![这里写图片描述](https://img-blog.csdn.net/20160722115317726)  
这个方法专门用于发送一个取消的命令给特定的监听器，让其取消当前操作。   
因此，app可以在需要的时候调用cancel方法来取消指纹扫描操作。

### 创建CryptoObject类对象

上面我们分析FingerprintManager的authenticate方法的时候，看到这个方法的第一个参数就是CryptoObject类的对象，现在我们看一下这个对象怎么去实例化。   
我们知道，指纹识别的结果可靠性是非常重要的，我们肯定不希望认证的过程被一个第三方以某种形式攻击，因为我们引入指纹认证的目的就是要提高安全性。但是，从理论角度来说，指纹认证的过程是可能被第三方的中间件恶意攻击的，常见的攻击的手段就是拦截和篡改指纹识别器提供的结果。这里我们可以提供CryptoObject对象给authenticate方法来避免这种形式的攻击。   
FingerprintManager.CryptoObject是基于[Java](http://lib.csdn.net/base/java "Java 知识库")加密API的一个包装类，并且被FingerprintManager用来保证认证结果的完整性。通常来讲，用来加密指纹扫描结果的机制就是一个Javax.Crypto.Cipher对象。Cipher对象本身会使用由应用调用Android keystore的API产生一个key来实现上面说道的保护功能。   
为了理解这些类之间是怎么协同工作的，这里我给出一个用于实例化CryptoObject对象的包装类代码，我们先看下这个代码是怎么实现的，然后再解释一下为什么是这样。

```
public class CryptoObjectHelper
{
    // This can be key name you want. Should be unique for the app.
    static final String KEY_NAME = "com.createchance.android.sample.fingerprint_authentication_key";
 
    // We always use this keystore on Android.
    static final String KEYSTORE_NAME = "AndroidKeyStore";
 
    // Should be no need to change these values.
    static final String KEY_ALGORITHM = KeyProperties.KEY_ALGORITHM_AES;
    static final String BLOCK_MODE = KeyProperties.BLOCK_MODE_CBC;
    static final String ENCRYPTION_PADDING = KeyProperties.ENCRYPTION_PADDING_PKCS7;
    static final String TRANSFORMATION = KEY_ALGORITHM + "/" +
    BLOCK_MODE + "/" +
    ENCRYPTION_PADDING;
    final KeyStore _keystore;
 
    public CryptoObjectHelper() throws Exception
    {
        _keystore = KeyStore.getInstance(KEYSTORE_NAME);
        _keystore.load(null);
    }
 
    public FingerprintManagerCompat.CryptoObject buildCryptoObject() throws Exception
    {
        Cipher cipher = createCipher(true);
        return new FingerprintManagerCompat.CryptoObject(cipher);
    }
 
    Cipher createCipher(boolean retry) throws Exception
    {
        Key key = GetKey();
        Cipher cipher = Cipher.getInstance(TRANSFORMATION);
        try
        {
            cipher.init(Cipher.ENCRYPT_MODE | Cipher.DECRYPT_MODE, key);
        } catch(KeyPermanentlyInvalidatedException e)
        {
            _keystore.deleteEntry(KEY_NAME);
            if(retry)
            {
                createCipher(false);
            } else
            {
                throw new Exception("Could not create the cipher for fingerprint authentication.", e);
            }
        }
        return cipher;
    }
 
    Key GetKey() throws Exception
    {
        Key secretKey;
        if(!_keystore.isKeyEntry(KEY_NAME))
        {
            CreateKey();
        }
 
        secretKey = _keystore.getKey(KEY_NAME, null);
        return secretKey;
    }
 
    void CreateKey() throws Exception
    {
        KeyGenerator keyGen = KeyGenerator.getInstance(KEY_ALGORITHM, KEYSTORE_NAME);
        KeyGenParameterSpec keyGenSpec =
                new KeyGenParameterSpec.Builder(KEY_NAME, KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                        .setBlockModes(BLOCK_MODE)
                        .setEncryptionPaddings(ENCRYPTION_PADDING)
                        .setUserAuthenticationRequired(true)
                        .build();
        keyGen.init(keyGenSpec);
        keyGen.generateKey();
    }
}



      
      
      
      

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

上面的类会针对每个CryptoObject对象都会新建一个Cipher对象，并且会使用由应用生成的key。这个key的名字是使用KEY_NAME变量定义的，这个名字应该是保证唯一的，建议使用域名区别。GetKey方法会尝试使用Android Keystore的API来解析一个key（名字就是上面我们定义的），如果key不存在的话，那就调用CreateKey方法新建一个key。   
cipher变量的实例化是通过调用Cipher.getInstance方法获得的，这个方法接受一个transformation参数，这个参数制定了数据怎么加密和解密。然后调用Cipher.init方法就会使用应用的key来完成cipher对象的实例化工作。   
这里需要强调一点，在以下情况下，android会认为当前key是无效的：   
1\. 一个新的指纹image已经注册到系统中   
2\. 当前设备中的曾经注册过的指纹现在不存在了，可能是被全部删除了   
3\. 用户关闭了屏幕锁功能   
4\. 用户改变了屏幕锁的方式   
当上面的情况发生的时候，Cipher.init方法都会抛出KeyPermanentlyInvalidatedException的异常，上面我的代码中捕获了这个异常，并且删除了当前无效的key，然后根据参数尝试再次创建。   
上面的代码中使用了android的KeyGenerator来创建一个key并且把它存储在设备中。KeyGenerator类会创建一个key，但是需要一些原始数据才能创建key，这些原始的信息是通过KeyGenParameterSpec类的对象来提供的。KeyGenerator类对象的实例化是使用它的工厂方法getInstance进行的，从上面的代码中我们可以看到这里使用的AES（Advanced Encryption Standard ）加密[算法](http://lib.csdn.net/base/datastructure "算法与数据结构知识库")的，AES会将数据分成几个组，然后针对几个组进行加密。   
接下来，KeyGenParameterSpec的实例化是使用它的Builder方法，KeyGenParameterSpec.Builder封装了以下重要的信息：   
1\. key的名字   
2\. key必须在加密和解密的时候是有效的   
3\. 上面代码中BLOCK_MODE被设置为Cipher Block Chaining也就是KeyProperties.BLOCK_MODE_CBC，这意味着每一个被AES切分的数据块都与之前的数据块进行了异或运算了，这样的目的就是为了建立每个数据块之间的依赖关系。   
4\. CryptoObjectHelper类使用了PKSC7（Public Key Cryptography Standard #7）的方式去产生用于填充AES数据块的字节，这样就是要保证每个数据块的大小是等同的（因为需要异或计算还有方面算法进行数据处理，详细可以查看AES的算法原理）。   
5\. setUserAuthenticationRequired(true)调用意味着在使用key之前用户的身份需要被认证。   
每次KeyGenParameterSpec创建的时候，他都被用来初始化KeyGenerator，这个对象会产生存储在设备上的key。

#### 怎么使用CryptoObjectHelper呢？

下面我们看一下怎么使用CryptoObjectHelper这个类，我们直接看代码就知道了：

```
CryptoObjectHelper cryptoObjectHelper = new CryptoObjectHelper();
fingerprintManager.authenticate(cryptoObjectHelper.buildCryptoObject(), 0,
                            cancellationSignal, myAuthCallback, null);



      
      
      
      



代码解释
```

使用是比较简单的，首先new一个CryptoObjectHelper对象，然后调用buildCryptoObject方法就能得到CryptoObject对象了。

### 处理用户的指纹认证结果

前面我们分析authenticate接口的时候说道，调用这个接口的时候必须提供FingerprintManager.AuthenticationCallback类的对象，这个对象会在指纹认证结束之后系统回调以通知app认证的结果的。在android 6.0中，指纹的扫描和认证都是在另外一个进程中完成（指纹系统服务）的，因此底层什么时候能够完成认证我们app是不能假设的。因此，我们只能采取异步的操作方式，也就是当系统底层完成的时候主动通知我们，通知的方式就是通过回调我们自己实现的FingerprintManager.AuthenticationCallback类，这个类中定义了一些回调方法以供我们进行必要的处理：   
![这里写图片描述](https://img-blog.csdn.net/20160722131735358)  
下面我们简要介绍一下这些接口的含义：   
1\. OnAuthenticationError（int errorCode, ICharSequence errString） 这个接口会再系统指纹认证出现不可恢复的错误的时候才会调用，并且参数errorCode就给出了错误码，标识了错误的原因。这个时候app能做的只能是提示用户重新尝试一遍。   
2\. OnAuthenticationFailed() 这个接口会在系统指纹认证失败的情况的下才会回调。注意这里的认证失败和上面的认证错误是不一样的，虽然结果都是不能认证。认证失败是指所有的信息都采集完整，并且没有任何异常，但是这个指纹和之前注册的指纹是不相符的；但是认证错误是指在采集或者认证的过程中出现了错误，比如指纹传感器工作异常等。也就是说认证失败是一个可以预期的正常情况，而认证错误是不可预期的异常情况。   
3\. OnAuthenticationHelp(int helpMsgId, ICharSequence helpString) 上面的认证失败是认证过程中的一个异常情况，我们说那种情况是因为出现了不可恢复的错误，而我们这里的OnAuthenticationHelp方法是出现了可以回复的异常才会调用的。什么是可以恢复的异常呢？一个常见的例子就是：手指移动太快，当我们把手指放到传感器上的时候，如果我们很快地将手指移走的话，那么指纹传感器可能只采集了部分的信息，因此认证会失败。但是这个错误是可以恢复的，因此只要提示用户再次按下指纹，并且不要太快移走就可以解决。  
4\. OnAuthenticationSucceeded(FingerprintManagerCompati.AuthenticationResult result)这个接口会在认证成功之后回调。我们可以在这个方法中提示用户认证成功。这里需要说明一下，如果我们上面在调用authenticate的时候，我们的CryptoObject不是null的话，那么我们在这个方法中可以通过AuthenticationResult来获得Cypher对象然后调用它的doFinal方法。doFinal方法会检查结果是不是会拦截或者篡改过，如果是的话会抛出一个异常。当我们发现这些异常的时候都应该将认证当做是失败来来处理，为了安全建议大家都这么做。   
关于上面的接口还有2点需要补充一下：   
1\. 上面我们说道OnAuthenticationError 和 OnAuthenticationHelp方法中会有错误或者帮助码以提示为什么认证不成功。Android系统定义了几个错误和帮助码在FingerprintManager类中，如下：   
![这里写图片描述](https://img-blog.csdn.net/20160722133935198)  
我们的callback类实现的时候最好需要处理这些错误和帮助码。   
2\. 当指纹扫描器正在工作的时候，如果我们取消本次操作的话，系统也会回调OnAuthenticationError方法的，只是这个时候的错误码是FingerprintManager.FINGERPRINT_ERROR_CANCELED（值为5），因此app需要区别对待。   
下面给出我的代码中实现的callback子类：

```
package com.createchance.fingerprintdemo;
 
import android.os.Handler;
import android.support.v4.hardware.fingerprint.FingerprintManagerCompat;
 
import javax.crypto.BadPaddingException;
import javax.crypto.IllegalBlockSizeException;
 
/**
 * Created by baniel on 7/21/16.
 */
public class MyAuthCallback extends FingerprintManagerCompat.AuthenticationCallback {
 
    private Handler handler = null;
 
    public MyAuthCallback(Handler handler) {
        super();
 
        this.handler = handler;
    }
 
    @Override
    public void onAuthenticationError(int errMsgId, CharSequence errString) {
        super.onAuthenticationError(errMsgId, errString);
 
        if (handler != null) {
            handler.obtainMessage(MainActivity.MSG_AUTH_ERROR, errMsgId, 0).sendToTarget();
        }
    }
 
    @Override
    public void onAuthenticationHelp(int helpMsgId, CharSequence helpString) {
        super.onAuthenticationHelp(helpMsgId, helpString);
 
        if (handler != null) {
            handler.obtainMessage(MainActivity.MSG_AUTH_HELP, helpMsgId, 0).sendToTarget();
        }
    }
 
    @Override
    public void onAuthenticationSucceeded(FingerprintManagerCompat.AuthenticationResult result) {
        super.onAuthenticationSucceeded(result);
 
        try {
            result.getCryptoObject().getCipher().doFinal();
 
            if (handler != null) {
                handler.obtainMessage(MainActivity.MSG_AUTH_SUCCESS).sendToTarget();
            }
        } catch (IllegalBlockSizeException e) {
            e.printStackTrace();
        } catch (BadPaddingException e) {
            e.printStackTrace();
        }
    }
 
    @Override
    public void onAuthenticationFailed() {
        super.onAuthenticationFailed();
 
        if (handler != null) {
            handler.obtainMessage(MainActivity.MSG_AUTH_FAILED).sendToTarget();
        }
    }
}



      
      
      
      

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

这个子类实现很简单，主要的实现方式就是将消息抛给主界面的Handler来处理：

```
handler = new Handler() {
    @Override
    public void handleMessage(Message msg) {
        super.handleMessage(msg);
 
        Log.d(TAG, "msg: " + msg.what + " ,arg1: " + msg.arg1);
        switch (msg.what) {
            case MSG_AUTH_SUCCESS:
                setResultInfo(R.string.fingerprint_success);
                mCancelBtn.setEnabled(false);
                mStartBtn.setEnabled(true);
                cancellationSignal = null;
                break;
            case MSG_AUTH_FAILED:
                setResultInfo(R.string.fingerprint_not_recognized);
                mCancelBtn.setEnabled(false);
                mStartBtn.setEnabled(true);
                cancellationSignal = null;
                break;
            case MSG_AUTH_ERROR:
                handleErrorCode(msg.arg1);
                break;
            case MSG_AUTH_HELP:
                handleHelpCode(msg.arg1);
                break;
        }
    }
};



      
      
      
      

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

这里分别处理四中回调，并且针对错误码调用handleErrorCode方法处理：

```
private void handleErrorCode(int code) {
    switch (code) {
        case FingerprintManager.FINGERPRINT_ERROR_CANCELED:
            setResultInfo(R.string.ErrorCanceled_warning);
            break;
        case FingerprintManager.FINGERPRINT_ERROR_HW_UNAVAILABLE:
            setResultInfo(R.string.ErrorHwUnavailable_warning);
            break;
        case FingerprintManager.FINGERPRINT_ERROR_LOCKOUT:
            setResultInfo(R.string.ErrorLockout_warning);
            break;
        case FingerprintManager.FINGERPRINT_ERROR_NO_SPACE:
            setResultInfo(R.string.ErrorNoSpace_warning);
            break;
        case FingerprintManager.FINGERPRINT_ERROR_TIMEOUT:
            setResultInfo(R.string.ErrorTimeout_warning);
            break;
        case FingerprintManager.FINGERPRINT_ERROR_UNABLE_TO_PROCESS:
            setResultInfo(R.string.ErrorUnableToProcess_warning);
            break;
    }
}



      
      
      
      

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

很简单，就是针对不同的错误码，设置界面上不同的显示文字，以提示用户。这里大家可以很据自己的需要修改逻辑。   
针对帮助码调用handleHelpCode方法处理：

```
private void handleHelpCode(int code) {
    switch (code) {
        case FingerprintManager.FINGERPRINT_ACQUIRED_GOOD:
            setResultInfo(R.string.AcquiredGood_warning);
            break;
        case FingerprintManager.FINGERPRINT_ACQUIRED_IMAGER_DIRTY:
            setResultInfo(R.string.AcquiredImageDirty_warning);
            break;
        case FingerprintManager.FINGERPRINT_ACQUIRED_INSUFFICIENT:
            setResultInfo(R.string.AcquiredInsufficient_warning);
            break;
        case FingerprintManager.FINGERPRINT_ACQUIRED_PARTIAL:
            setResultInfo(R.string.AcquiredPartial_warning);
            break;
        case FingerprintManager.FINGERPRINT_ACQUIRED_TOO_FAST:
            setResultInfo(R.string.AcquiredTooFast_warning);
            break;
        case FingerprintManager.FINGERPRINT_ACQUIRED_TOO_SLOW:
            setResultInfo(R.string.AcquiredToSlow_warning);
            break;
    }
}



      
      
      
      

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)





代码解释
```

这里的处理和handleErrorCode是一样的。

## 总结

这里我们总计一下，android 6.0上的指纹识别开发的几个要点：   
1\. 建议使用Android Support Library v4 Compatibility API，不要使用直接framework中的api。   
2\. 在使用指纹硬件之前一定要检查上面提到的几个检查条件   
3\. 根据google的建议最好使用google提供的指纹是被icon来标示你的指纹识别界面：   
![这里写图片描述](https://img-blog.csdn.net/20160722134745928)   
这个做的目的就是为了很明确地提示用户这是一个指纹识别操作，就像人们看到蓝牙的那个小标识就知道这是蓝牙操作一样。当然，这只是google的一个实践性的建议，并非强制。   
4\. app需要及时通知用户当前的操作以及操作的结果，比如需要明确告诉用户当前正在扫描指纹，请把你的指纹放在传感器上等。   
5\. 最后需要注意的就是Android Support Library v4中的FingerprintManager类名字是FingerprintManagerCompat，并且他们的authenticate方法参数顺序不一样,flags和cancel的位置在两个类中是不一样的，这一点需要注意（个人觉得，这会不会是google的失误呢？？？嘿嘿。。。。。）

### demo运行效果截图（运行于nexus 5x）

初始状态   
![这里写图片描述](https://img-blog.csdn.net/20160722135716426)   
扫描状态   
![这里写图片描述](https://img-blog.csdn.net/20160722135730458)   
扫描失败（出现可以恢复的错误，这里是手指移动太快）   
![这里写图片描述](https://img-blog.csdn.net/20160722135743392)   
认证失败   
![这里写图片描述](https://img-blog.csdn.net/20160722135756923)   
认证成功   
![这里写图片描述](https://img-blog.csdn.net/20160722135805501)