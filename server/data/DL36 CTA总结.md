### DL36 CTA认证总结

关于CTA认证的详细描述与认证流程，mtkonline上有详细介绍，链接为： https://online.mediatek.com/QuickStart/cfbbb3ad-8509-4ce3-a5f2-8507cb4760d9

定期与wiki同步：http://192.168.4.2:8090/display/SW/CTA



**WLAN，无相关权限配置，调用无提示WLAN开关可直接开启。**

Problem statement: 

需要在第三方apk调用打开WIFI时进行弹框提示

```
http://192.168.4.5:8083/#/c/android/platform/frameworks/opt/net/wifi/+/43484/
http://192.168.4.5:8083/#/c/android/platform/frameworks/opt/net/wifi/+/44367/1/service/java/com/android/server/wifi/WifiServiceImpl.java
```



**通话录音，调用允许生成可播放无声录音文件**

Problem statement: 

提供声明：不支持第三方应用调用通话录音，我司该型号终端目前是基于Android 11平台，因为Android平台机制，应用进行通话录音需获取CAPTURE_AUDIO_OUTPUT权限，而第三方应用无法获取该权限,只有系统自带的预置应用才可以获取到CAPTURE_AUDIO_OUTPUT权限进行正常通话录音功能,第三方应用不满足该条件,所以只能生成可播放无声文件。



**NFC，无法通过NFC传输文本，请确认是否支持NFC文件传输，若不支持请提供声明并说明NFC使用场景**

Problem statement: 

提供声明：支持NFC，但不支持NFC文件数据传输。支持使用场景NFC卡的会员卡管理，支持刷卡功能



**操作系统更新；无电子版说明书，需提供**

Problem statement: 

提供电子版说明书（即刷机操作文档即工具）



**6.0接口：定位、本地录音、拍照/摄像：提示选项有“仅限这一次”，对应的配置为“每次都询问”配置和提示描述有误，选择后再次调用短时间会记住**

Problem statement: 

实验室提供修改说明：“仅限这一次”改成“仅本次使用时允许”，“每次都询问”改成"每次使用时询问"

```
http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/apps/PackageInstaller/+/44363/
```



**定位，单项配置开关和总开关之间逻辑关系混乱，请确认配置是否以单项配置开关为准，若是请在总开关每次使用时询问中添加文字描述（文字描述为：请参考细分权限详情）**

Problem statement: 

在xml文件中修改字符串内容，添加"请参考细分权限详情"

```
http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/apps/PackageInstaller/+/43531/
```



**多项内容无受控机制**

**4.3.1.1.7.2 WLAN网络连接开启、关闭的受控机制---无受控机制**
**4.3.1.2.1.1 定位功能受控机制---无受控机制**
**4.3.1.2.2 通话录音功能启动的受控机制---无受控机制**
**4.3.1.2.3 本地录音功能启动的受控机制---无受控机制**
**4.3.1.2.4 拍照/摄像功能启动的受控机制---无受控机制**
**4.3.1.3 操作系统的授权更新或非授权更新---未提供相关说明**
**4.4.1.3.2 NFC接口连接提示---提示有误**

Problem statement: 

开启受控机制的宏控

注意：MSSI编译的项目和非MSSI编译的项目有两套不同的宏控

MTK_WAPI_SUPPORT默认关闭

MSSI编译方式后多了两个属性

MSSI_MTK_CTA_SET = yes

MSSI_MTK_CTA_SUPPORT = yes

MSSI_MTK_MOBILE_MANAGEMENT = yes

MSSI_MTK_PRIVACY_PROTECTION_LOCK = yes

```
http://192.168.4.5:8083/#/c/android/alps/device/mediatek/system/mssi_t_64_cn/+/43654/
```



**卡机引导明示为英文，需点确认后才能更改语言**

Problem statement: 

更改默认语言为中文

```
http://192.168.4.5:8083/#/c/android/platform/build/+/43438/
```



**蓝牙读联系人行为未明示（蓝牙开启状态下，新建联系人）**

Problem statement: 

这是Google AOSP原生设计行为，联系人更新（增/删），Bluetooth就会去获取最新联系人信息，Bluetooth进程是platform组件，非第三方apk不存在隐私问题 

建议重复测试



**SoftSpot内容为英文**

Problem statement: 

datalogic开发的第三方APK，按照常规处理直接移除

```
http://192.168.4.5:8083/#/c/android/alps/device/datalogic/datalogic-common/+/44446/
```



**通用业务功能：6.1.1.1.1 语音通话---该设备语音未默认开启免提通话**

Problem statement: 

接收与拨打电话时能够自动开启免提功能

```
http://192.168.4.5:8083/#/c/android/alps/device/datalogic/dl36/+/44036/
http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/services/Telecomm/+/44037/
```



**可卸载状态的问题：图库，SoftSpot，DebugLoggerUI这三个应用要改为可卸载状态**

Problem statement: 

将反馈应用设置为可卸载

```
在这个xml文件中将包名加进去
vendor/mediatek/proprietary/frameworks/base/data/etc/pms_sysapp_removable_system_list.txt
```



