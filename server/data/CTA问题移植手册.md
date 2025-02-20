### 介绍

此问题移植手册集合了目前遇到的所有需要修改的CTA问题，后续有认证问题会持续更新...

移植时可能会因为平台不同，导致修改点位置改变，此文档修改方式仅供参考。



**问题移植列表：**

| 序号  | 问题描述                                                                          | 是否新规case |
| :-: | :---------------------------------------------------------------------------- | :------: |
|  1  | 预制应用可卸载                                                                       |          |
|  2  | 关于Settings汉化和文本需求                                                             |          |
|  3  | CTA测试的分支代码需要打开对应的宏控                                                           |          |
|  4  | 开启CTA受控机制                                                                     |          |
|  5  | 相机开启定位权限未明示                                                                   |          |
|  6  | WLAN、蓝牙：有功能、无配置、调用无提示直接开启                                                     |          |
|  7  | 屏蔽发送/读取彩信、读取联系人、读取通话记录、发送/短信功能（无相关功能才需要移除）                                    |          |
|  8  | 定位相关问题                                                                        |          |
|  9  | 恢复出厂设置后，未见操作系统启动后有个人信息保护（收集使用个人信息的目的、方式和范围，并获得用户同意）等相关提示/向导/协议                |    Y     |
| 10  | 调用读取设备唯一可识别信息（IEMI、MAC地址）读取失败，需整改                                             |    Y     |
| 11  | 调用软件列表读取操作无控制机制，调用可成功读取，需整改                                                   |    Y     |
| 12  | 设置中无应用自启动配置，调用应用开机自启动成功，需整改                                                   |    Y     |
| 13  | 应用软件敏感信息的调用行为记录不全面，事件不明确，需整改                                                  |    Y     |
| 14  | 6.0接口：定位、本地录音、拍照/摄像：提示选项有“仅限这一次”，对应的配置为“每次都询问”配置和提示描述有误，选择后再次调用短时间会记住         |          |
| 15  | 定位，单项配置开关和总开关之间逻辑关系混乱，请确认配置是否以单项配置开关为准，若是请在总开关每次使用时询问中添加文字描述（文字描述为：请参考细分权限详情） |          |
| 16  | 卡机引导明示为英文，需点确认后才能更改语言                                                         |          |
| 17  | 语音通话---该设备语音未默认开启免提通话                                                         |          |
| 18  | GPS定位和网络定位联动问题                                                                |          |
| 19  |                                                                               |          |

------

### 修改方案

#### 1：预制应用可卸载

送测的软件，系统预制应用需要变成可卸载状态

除了以下这些原生应用需要改为可卸载外，其他的预制应用（例如客户APK）也要加到此处

修改方式：vendor/mediatek/proprietary/frameworks/base/data/etc/pms_sysapp_removable_system_list.txt

```
com.android.quicksearchbox
com.android.calendar
com.android.dreams.basic
com.android.musicfx
com.android.calculator2
com.android.email
com.android.exchange
com.mediatek.camera
com.android.gallery3d
```



#### 2：关于Settings汉化和文本需求

WiFi字样需全部改成WLAN

修改方式：vendor/mediatek/proprietary/packages/apps/MtkSettings/res/values-zh-rCN/strings.xml将xml文件中的Wi-Fi字样改成WLAN



#### 3：CTA测试的分支代码需要打开对应的宏控

Android12之前的宏控：在对应的device.mk中

```
MTK_CTA_SUPPORT = yes
MTK_WAPI_SUPPORT = no
```

Android12之后的宏控

```
如果贵司使用到是legacy build,非split build看看是否有开以下compile option:
MTK_MOBILE_MANAGEMENT = no
MTK_CTA_SET= no
MTK_PRIVACY_PROTECTION_LOCK = no
MTK_CTA_SUPPORT = no
如果贵司使用的是Split build,请看看是否有开以下Compile option:
MSSI_MTK_MOBILE_MANAGEMENT = no
MSSI_MTK_CTA_SET= no
MSSI_MTK_PRIVACY_PROTECTION_LOCK = no
MSSI_MTK_CTA_SUPPORT = no
```



#### 4：开启CTA受控机制

添加相关的应用以针对不同情境进行受控

修改方式：device/mediatek/system/common/device.mk

```
PRODUCT_PACKAGES += NetworkDataController
PRODUCT_PACKAGES += NetworkDataControllerService
PRODUCT_PACKAGES += AutoBootController
```



#### 5：相机开启定位权限未明示

在打开摄像机时会自动获取定位，没有给用户相关的提示

修改方式(修改量较大，请参考此链接)：http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/apps/Camera2/+/36023/



#### 6：WLAN、蓝牙：有功能、无配置、调用无提示直接开启

- **WLAN**

  第三方应用调用WLAN接口时，需要进行弹框提示（需要包含确定和取消）

  修改方式(修改量较大，请参考此链接)：http://192.168.4.5:8083/#/c/android/platform/packages/modules/Wifi/+/57717/

- **蓝牙**

  第三方应用调用蓝牙接口时，需要进行弹框提示（需要包含确定和取消）
  
  修改方式(请参考此链接中对应文件修改)：http://192.168.4.5:8083/#/c/MTK/alps-release-t0.mp1.rc-tb/+/61564/{
  
  ​		vendor/mediatek/proprietary/packages/modules/Bluetooth/service/java/com/android/server/bluetooth/BluetoothManagerService.java
  
  }



#### 7：屏蔽发送/读取彩信、读取联系人、读取通话记录、发送/短信功能（无相关功能才需要移除）

- **屏蔽发送/读取彩信**

  修改方式:

  external/okhttp/okhttp/src/main/java/com/squareup/okhttp/internal/io/RealConnection.java

  ![image-20240614164738317](image-20240614164738317.png)

  vendor/mediatek/proprietary/packages/apps/Mms/src/com/android/mms/MmsConfig.java

  ![image-20240614164802699](image-20240614164802699.png)

  vendor/mediatek/proprietary/packages/providers/TelephonyProvider/src/com/android/providers/telephony/MmsProvider.java

  ![image-20240614164847497](image-20240614164847497.png)

  vendor/mediatek/proprietary/packages/providers/TelephonyProvider/AndroidManifest.xml

  ![image-20240614164908431](image-20240614164908431.png)

- **读取联系人**

  修改方式(请参考此链接)：http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/providers/ContactsProvider/+/40587/

- **读取通话记录**

  修改方式：vendor/mediatek/proprietary/packages/providers/ContactsProvider/AndroidManifest.xml

  ![image-20240614165038734](image-20240614165038734.png)

- **发送/短信功能、通话录音**

  修改方式：frameworks/base/core/res/res/values/config.xml

  ![image-20240614165141078](image-20240614165141078.png)



#### 8：

从Android11之后定位权限统一由permissionController APP管理，Android11之后一般出现定位相关的问题，需要提ES让MTK把patch合入。
设置-应用和通知-应用信息-权限界面，只有总开关权限配置，无单项权限配置，点击右上角三个点，显示所有权限，进入只有但文字描述，无单项权限配置开关。

修改方式：device/mediatek/system/common/device.mk

```
PRODUCT_PACKAGES += MtkPermissionController
PRODUCT_PACKAGES += mediatek-cta
```



#### 9：恢复出厂设置后，未见操作系统启动后有个人信息保护（收集使用个人信息的目的、方式和范围，并获得用户同意）等相关提示/向导/协议

在开机向导处加上收集使用个人信息的目的、方式和范围；并在底部添加取消的选项，用户选择取消后直接关机

修改方式(修改量较大，请参考以下链接)：
http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/apps/PackageInstaller/+/58136/
http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/apps/PackageInstaller/+/62504/



#### 10：调用读取设备唯一可识别信息（IEMI、MAC地址）读取失败，需整改

设备读取唯一可识别信息时，读取失败; 禁用第三方应用读取，后续出示声明文件

**Android13**平台：修改方式(请参考此链接)：http://192.168.4.5:8083/#/c/android/platform/packages/modules/Wifi/+/59174/

**Android9**平台：修改方式(请参考此链接中对应文件修改)：
http://192.168.4.5:8083/#/c/MTK/alps-release-p0.mp1-tb/+/65334/{
		frameworks/base/wifi/java/android/net/wifi/WifiInfo.java
		libcore/ojluni/src/main/java/java/net/NetworkInterface.java
}



#### 11：调用软件列表读取操作无控制机制，调用可成功读取，需整改

读取软件列表操作时，需要弹框提示用户，由用户选择同意或是拒绝

此问题有两个解决方案：

- **禁止第三方引用调用软件列表读取操作，并提供不支持声明文件**

  修改方式(请参考此链接中对应文件修改)：
  http://192.168.4.5:8083/#/c/MTK/alps-release-t0.mp1.rc-tb/+/60765/{

  ​		frameworks/base/core/java/android/app/ApplicationPackageManager.java
  }

- **调用软件列表读取操作时增加弹框提示（需要包含确定和取消）**

  修改方式(请参考此链接中对应文件修改)：
  http://192.168.4.5:8083/#/c/MTK/alps-release-s0.mp1.rc-tb/+/62595/{

  ​		frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java
  }



#### 12：设置中无应用自启动配置，调用应用开机自启动成功，需整改

在设置中增加自启动相关配置
自启动应用源码请查看附件：MAIDU_CTA_AUTORUN

修改方式(修改量较大，请参考以下链接)：
http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/apps/CtaAutoRun/+/58329/
http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/apps/MtkSettings/+/58322/



#### 13：应用软件敏感信息的调用行为记录不全面，事件不明确，需整改

此问题修改量非常大，初次送测可以不take这部分修改，等待第一次问题反馈时再一同改入

**Android13平台：**
此问题需要记录所有的权限调用记录，目前在A13上的方案采用的是MTK的patch，如果如要合入PATCH解决此问题，请确保MTKSettings中有此面板：settings-Privacy-Privacy dashboard，且存在PermissionControler应用。由于patch没有先后顺序，可以参考以下顺序合入，且需要自行解决冲突

```
 frameworks/base/   (sys 使用android12的vnd时,可能会有部分修改在vnd)
 8313b1b.diff
 af2419b.diff
 73a61b0.diff
 6040a59.diff
 d8f2036.diff
  
 vendor/mediatek/proprietary/frameworks/base/ (sys)
 1fe4f88.diff
 55550d7.diff
 9386104.diff
 ef61924.diff
  
 vendor/mediatek/proprietary/frameworks/opt/cta/ (sys)
 315196d.diff
 b615874.diff
 82e7237.diff
 875e3b0.diff
 af4593d.diff
  
 vendor/mediatek/proprietary/packages/apps/PermissionController/ (vnd)
 0be6a5f.diff
 7299c39.diff
 cab4397.diff
 38da52f.diff
  
 vendor/mediatek/proprietary/packages/apps/SystemUI/ (sys)
 7c43998.diff
```

修改方式(请参考以下提交链接)：

http://192.168.4.5:8083/#/c/MTK/alps-release-t0.mp1.rc-tb/+/62593/
http://192.168.4.5:8083/#/c/MTK/alps-release-t0.mp1.rc-tb/+/63417/
http://192.168.4.5:8083/#/c/MTK/alps-release-s0.mp1.rc-tb/+/62595/



**Android9平台：**

用A9送测新规同样会碰到此问题，但是由于permissioncontroler与A13不一致，不能直接移植
需要添加调用行为相关的权限配置，哪些调用行为没记录到，就在frameworks/base/core/res/AndroidManifest.xml中加权限，然后通过AppToPermissionActivity.java去显示
注意：XQT406只反馈了（缺少后台截屏录屏、读取媒体影音数据），有其他调用行为需要自行对照添加

修改方式(请参考此链接)：http://192.168.4.5:8083/#/c/MTK/alps-release-p0.mp1-tb/+/65420/



#### 14：6.0接口：定位、本地录音、拍照/摄像：提示选项有“仅限这一次”，对应的配置为“每次都询问”配置和提示描述有误，选择后再次调用短时间会记住

修改说明：“仅限这一次”改成“仅本次使用时允许”，“每次都询问”改成"每次使用时询问"

修改方式(请参考此链接)：http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/apps/PackageInstaller/+/44363/



#### 15：定位，单项配置开关和总开关之间逻辑关系混乱，请确认配置是否以单项配置开关为准，若是请在总开关每次使用时询问中添加文字描述（文字描述为：请参考细分权限详情）

在xml文件中修改字符串内容，添加"请参考细分权限详情"

修改方式(请参考此链接)：http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/apps/PackageInstaller/+/43531/



#### 16：卡机引导明示为英文，需点确认后才能更改语言

更改系统默认语言为中文

修改方式(请参考此链接)：http://192.168.4.5:8083/#/c/android/platform/build/+/43438/



#### 17： 语音通话---该设备语音未默认开启免提通话

接收与拨打电话时能够自动开启免提功能

修改方式(请参考以下提交链接)：
http://192.168.4.5:8083/#/c/android/alps/device/datalogic/dl36/+/44036/
http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/services/Telecomm/+/44037/



#### 18：  GPS定位和网络定位联动问题

修改方式(请参考此链接)：http://192.168.4.5:8083/#/c/androidO/alps/vendor/mediatek/proprietary/frameworks/opt/cta/+/17746/

