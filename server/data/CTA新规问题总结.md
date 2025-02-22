## CTA新规问题总结V1.0

**@Author:cactus::黎子罗  <ziluo.li@mobiiot.com.cn>**

**@comment：CTA new regulation problem solution**



###  CTA相关介绍

CTA认证在中国通信领域具有重要意义，通常是指中国泰尔认证中心（China Telecommunication Technology Labs Authentication Center，简称CTA）提供的认证。它主要用于确保通信设备、手机及相关产品符合中国市场的技术标准和法规要求

- CTA认证是中国政府规定的强制性认证之一，确保通信设备符合国家标准和相关法规。这有助于保护消费者权益，确保设备在安全、兼容性、性能等方面达到规定要求。
- 在中国市场销售的通信设备，如手机、平板、路由器等，必须通过CTA认证。这是进入中国市场的基本条件之一，确保设备合法销售。
- CTA认证流程包含多项测试，如射频、功能、安全、电磁兼容性等。这种严谨的测试过程确保了设备的质量，降低了因产品缺陷导致的风险。
- 通过CTA认证的设备必须符合中国的技术标准，这有助于推动行业标准化和规范化，促进通信领域的技术发展。



以下是CTA认证的流程概述：

1. **申请阶段**：
   - 企业向中国泰尔认证中心提交CTA认证申请，说明要测试的设备类型和型号。
   - 提交相应的技术资料，包括产品的技术规格、功能描述、结构图、测试报告等。
2. **审核阶段**：
   - 认证中心会审查企业的申请和技术资料，确保其符合基本的法规要求。
   - 审查包括设备的功能、性能、安全性、兼容性等方面。
3. **测试阶段**：
   - 设备需要经过一系列测试，包括射频测试、功能测试、安全测试、电磁兼容性测试等。
   - 测试可以在泰尔认证中心的实验室进行，或在其他被授权的实验室进行。
4. **认证阶段**：
   - 如果设备通过了所有测试，认证中心会颁发CTA认证证书，证明该设备符合中国的技术和安全标准。
   - 认证证书可能包括设备的型号、规格、测试结果等信息。
5. **监管和维护**：
   - 企业获得认证后，可能需要定期进行复检，确保设备持续符合标准。
   - 如果设备发生重大变化，可能需要重新认证。



### 文档描述

此文档总结了与XQT554(A13) - XQT532(A13) - XQT406(A9)等项目碰到的CTA新规问题，在查看此文档时，请确保项目合入了CTA 的common修改。
对于A12/13项目，MTK有相关的支持，PATCH文件请查看附件：**A13_CTA_PATCH**。
而A12之前的版本，MTK表示不会进行支持新规认证，需要自行修改
详情请参考：http://192.168.4.2:8090/display/SW/CTA



### 内部测试

在送测CTA之前，请安装内部的CTA测试应用进行测试，以避免遇到的问题反馈出来，测试应用会根据CTA认证需求持续更新（有时间的话）.....

安装方式：http://192.168.4.2:8090/pages/viewpage.action?pageId=31885983



### 问题反馈

相同的问题优先在高平台上展示，对于相同问题但是不同平台有不同的解决方案，都会列出来。

**A13问题汇总**

| 序号 | 问题                                                         | 是否修改 |
| ---- | ------------------------------------------------------------ | -------- |
| 1    | Android 安全补丁程序级别为2023年4月5日（超过6个月），可能存在相应超高中危漏洞（如：高危漏洞： CVE-2022-20244、CVE-2023-21107、CVE-2023-21112、CVE-2023-21118），需整改 | Y        |
| 2    | 设置中没有操作系统更新选项，需确认是否支持（更新受控、自动更新受控、更新下载受控） |          |
| 3    | 恢复出厂设置后，未见操作系统启动后有个人信息保护（收集使用个人信息的目的、方式和范围，并获得用户同意）等相关提示/向导/协议，需整改 | Y        |
| 4    | 蓝牙接口无受控机制                                           | Y        |
| 5    | 调用网络定位功能（Location Manager.NETWORK_PROVIDER）失败，需确认 |          |
| 6    | Android 5.0 (TargetSDk<23) 接口应用在禁用麦克风权限下，调用通话录音、本地录音生成有大小的无声文件，需确认 |          |
| 7    | 开启麦克风权限下，调用通话录音生成有大小的无声文件，需确认   |          |
| 8    | 调用读取上网记录失败，需确认                                 |          |
| 9    | 调用读取生物特征识别信息失败，需确认                         |          |
| 10   | 调用读取设备唯一可识别信息（IEMI、MAC地址）读取失败，需整改  | Y        |
| 11   | 调用软件列表读取操作无控制机制，调用可成功读取，需整改       | Y        |
| 12   | 设置中无应用自启动配置，调用应用开机自启动成功，需整改       | Y        |
| 13   | 相机 com.mediatek.camera 在未同意启用定位服务时，仍存在调用获取位置信息行为，需整改 | Y        |
| 14   | 应用软件敏感信息的调用行为记录不全面，事件不明确，需整改     | Y        |
| 15   | 未见预置应用有更新升级相应配置，需确认是否支持（更新受控、自动更新受控、更新下载受控） |          |
| 16   | 浏览器、日历、通讯录、电话、图库、信息、Search、设置未见收集和使用用户个人信息协议，需整改 |          |
| 17   | 预制应用可卸载                                               | Y        |
| 18   | 调用读取媒体影音数据（照片、音频、视频）无受控机制，需整改   |          |

**A11问题汇总(当前common修改基于此平台)**

| 序号 | 问题                                                         | 是否修改 |
| ---- | ------------------------------------------------------------ | -------- |
| 1    | WLAN，无相关权限配置，调用无提示WLAN开关可直接开启           | Y        |
| 2    | NFC，无法通过NFC传输文本，请确认是否支持NFC文件传输，若不支持请提供声明并说明NFC使用场景 |          |
| 3    | 6.0接口：定位、本地录音、拍照/摄像：提示选项有“仅限这一次”，对应的配置为“每次都询问”配置和提示描述有误，选择后再次调用短时间会记住 | Y        |
| 4    | 定位，单项配置开关和总开关之间逻辑关系混乱，请确认配置是否以单项配置开关为准，若是请在总开关每次使用时询问中添加文字描述（文字描述为：请参考细分权限详情） | Y        |
| 5    | 多项内容无受控机制                                           | Y        |
| 6    | 卡机引导明示为英文，需点确认后才能更改语言                   | Y        |
| 7    | 蓝牙读联系人行为未明示（蓝牙开启状态下，新建联系人）         | Y        |
| 8    | 语音通话---该设备语音未默认开启免提通话                      | Y        |

**A9问题汇总**

| 序号 | 问题                                                         | 是否修改 |
| ---- | ------------------------------------------------------------ | -------- |
| 1    | 调用读取设备唯一可识别信息(MAC地址)地址未经提示且读取成功，需整改; | Y        |
| 2    | 应用软件敏感信息的调用行为记录事件不全面(缺少后台截屏录屏、读取媒体影音数据)，需整改 | Y        |
| 3    | Android 安全补丁程序级别为2021年1月5日 1.Android 安全补丁程序级别为2021年1月5日(超过6个月)，可能存在相应超高中危漏洞(如:高危漏洞:CVE-2021-1036、CVE-2021-39623、CVE-2022-21767、CVE-2022-20111、CVE-2022-21768)，需整改； |          |



### 问题解决方案

一般第一次CTA送测，会反馈大量的问题，不用太过担心，这是正常的。并且整个认证过程会持续数周(除非一次就把所有的问题改好，比较困难)，并且，这次没报的问题，在下次送测时可能会反馈；这次反馈的问题也可能在下一次测试时不复现了，针对这种情况可以向实验室申请复测单条case。

那么拿到反馈问题后，可以从以下几个步骤进行解决：

1. 检查common---首先看common修改的问题是否还有，如果有的话需要考虑是不是平台差异或者内部客制化导致，这时就需要进行解决了。
2. 过滤声明问题---判断哪些问题可以通过声明来解决。一般对于需确认的问题，确认后发现不支持可以提供声明文件。对于有些需修改的问题，也可以声明不支持，但是需要在代码中取消对应的功能。
3. 逐条修改---经过上述两步后过滤出的问题，基本都是要自行修改的。可以优先看看经验总结是否有类似的问题。对于描述不清楚的case，可以询问实验室人员，告知具体的测试步骤以及实验现象，必要时可以让其帮忙抓log。

以下是上述问题汇总的解决方案：

#### 声明类问题：

- 设置中没有操作系统更新选项，需确认是否支持（更新受控、自动更新受控、更新下载受控）
- 调用网络定位功能（Location Manager.NETWORK_PROVIDER）失败，需确认
- 调用读取上网记录失败，需确认
- 调用读取生物特征识别信息失败，需确认
- 调用读取设备唯一可识别信息（IEMI、MAC地址）读取失败，需整改
- 未见预置应用有更新升级相应配置，需确认是否支持（更新受控、自动更新受控、更新下载受控）

声明模板：

```
不支持声明

深圳信息通信研究院:

xxxxx有限公司送检的产品，名称：xxxxx，型号：xxxx，不支持：预置应用更新升级、操作系统更新、网络定位、调用读取上网记录、调用读取生物特征识别信息、调用读取设备唯一可识别信息（IEMI、MAC地址）。
```

- 浏览器、日历、通讯录、电话、图库、信息、Search、设置未见收集和使用用户个人信息协议，需整改

声明模板：

```
xxxxx有限公司送检的产品，名称：xxxxx，型号：xxxx，不支持：收集和使用用户个人信息协议，以下应用不会收集和使用用户个人信息：浏览器、日历、通讯录、电话、图库、信息、Search、设置。

软件信息：
应用名称	版本	开发者
浏览器	android12	Google
日历	android12	Google
通讯录	1.7.33	Google
电话	23.0	Google
图库	1.1.40030	Google
信息	android12	Google
Search	android12	Google
设置	android12	Google
```

- Android 5.0 (TargetSDk<23) 接口应用在禁用麦克风权限下，调用通话录音、本地录音生成有大小的无声文件，需确认
- 开启麦克风权限下，调用通话录音生成有大小的无声文件，需确认

声明模板：

```
声明

深圳信息通信研究院:

xxxxx有限公司送检的产品，名称：xxxxx，型号：xxxx，针对信息安全测试作出以下声明：
Android 12麦克风权限设为拒绝时，使用Android 5.1(API level 22)及更早版本的APK进行本地录音会生成无声的录音文件。原因是当麦克风权限设为拒绝时，Android 6.0(API level 23)及之后版本的APK，录音权限是PERMISSION_HARD_DENIED；Android 5.1 (API level 22)及更早版本的 APK，录音权限是PERMISSION_SOFT_DENIED。Android 12平台机制只有录音权限为PERMISSION_HARD_DENIED时，不会生成录音文件；PERMISSION_SOFT_DENIED时，可以生成录音文件但录不到声音。综上，Android 12麦克风权限设为拒绝时，使用Android 5.1(API level 22)及更早版本的APK录音会生成无声的录音文件。
特作此声明，我司保证入网前后的一致性，上市也不带以上功能销售。  
```



**以下是问题表格中有修改问题的解决方案，请按照问题表格查看是否有解决**

### 	修改类问题

------

 **Android 安全补丁程序级别为2023年4月5日（超过6个月），可能存在相应超高中危漏洞（如：高危漏洞： CVE-2022-20244、CVE-2023-21107、CVE-2023-21112、CVE-2023-21118），需整改**

```
对于此类安全补丁的问题，请联系集成的同学，合入相关的PATCH
可以在通过PATCH ID查看漏洞信息：https://www.cve.org/CVERecord
```

------

 **恢复出厂设置后，未见操作系统启动后有个人信息保护（收集使用个人信息的目的、方式和范围，并获得用户同意）等相关提示/向导/协议，需整改**

```
在开机向导处加上收集使用个人信息的目的、方式和范围；并在底部添加取消的选项，用户选择取消后直接关机

提交记录：
http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/apps/PackageInstaller/+/58136/
http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/apps/PackageInstaller/+/62504/
```

![image-20240507163143168](image-20240507163143168.png)

------

**蓝牙接口无受控机制**

```
第三方应用调用蓝牙接口时，需要进行弹框提示（需要包含确定和取消）

提交记录：
http://192.168.4.5:8083/#/c/MTK/alps-release-t0.mp1.rc-tb/+/61564/{	vendor/mediatek/proprietary/packages/modules/Bluetooth/service/java/com/android/server/bluetooth/BluetoothManagerService.java
}
```

![image-20240507164124062](image-20240507164124062.png)

------

**调用读取设备唯一可识别信息（IEMI、MAC地址）读取失败，需整改**

```
此问题可以通过声明解决，也可以直接禁止第三方应用调用MAC地址来解决

A13提交记录：
http://192.168.4.5:8083/#/c/android/platform/packages/modules/Wifi/+/59174/

A9提交记录：
http://192.168.4.5:8083/#/c/MTK/alps-release-p0.mp1-tb/+/65334/{
frameworks/base/wifi/java/android/net/wifi/WifiInfo.java
libcore/ojluni/src/main/java/java/net/NetworkInterface.java
}
```

![image-20240507164422517](image-20240507164422517.png)

------

**调用软件列表读取操作无控制机制，调用可成功读取，需整改**

```
此问题有两个方案：
1：禁止第三方引用调用软件列表读取操作，并提供不支持声明文件
提交记录：
http://192.168.4.5:8083/#/c/MTK/alps-release-t0.mp1.rc-tb/+/60765/{
frameworks/base/core/java/android/app/ApplicationPackageManager.java
}
```

![image-20240507165422464](image-20240507165422464.png)

```
2：调用软件列表读取操作时增加弹框提示（需要包含确定和取消）
提交记录：
http://192.168.4.5:8083/#/c/MTK/alps-release-s0.mp1.rc-tb/+/62595/{
frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java
}
```

![image-20240507165603425](image-20240507165603425.png)

------

**设置中无应用自启动配置，调用应用开机自启动成功，需整改**

```
在设置中增加自启动相关配置
自启动应用源码请查看附件：MAIDU_CTA_AUTORUN

提交记录：
http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/apps/CtaAutoRun/+/58329/
http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/apps/MtkSettings/+/58322/
```

------

**应用软件敏感信息的调用行为记录不全面，事件不明确，需整改**

```
A13：
此问题需要记录所有的权限调用记录，目前在A13上的方案采用的是MTK的patch，如果如要合入PATCH解决此问题
请确保MTKSettings中有此面板：settings-Privacy-Privacy dashboard，且存在PermissionControler应用。
由于patch没有先后顺序，可以参考以下顺序合入，且需要自行解决冲突

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


除了MTK的方案，也可以采用我开发的权限记录应用，可以记录大部分的权限（可能会反馈有部分权限记录不到；未记录的权限需要通过AIDL到各个调用权限的地方进行记录）。
对于后续反馈未记录到的权限，可以在AppOpsManager中加上
权限记录应用源码请查看附件：MAIDU_CTA_PERMISSIONDISPLAY
提交记录：
http://192.168.4.5:8083/#/c/MTK/alps-release-t0.mp1.rc-tb/+/60765/
```

```
A9：
用A9送测新规同样会碰到此问题，但是由于permissioncontroler与A13不一致，不能直接移植
需要添加调用行为相关的权限配置，哪些调用行为没记录到，就在frameworks/base/core/res/AndroidManifest.xml中加权限，然后通过AppToPermissionActivity.java去显示
注意：XQT406只反馈了（缺少后台截屏录屏、读取媒体影音数据），有其他调用行为需要自行对照添加

提交记录：http://192.168.4.5:8083/#/c/MTK/alps-release-p0.mp1-tb/+/65420/
```

![image-20240507200612796](/home/liziluo/LUZaLID/TyporaPicture/image-20240507200612796.png)

------

**WLAN，无相关权限配置，调用无提示WLAN开关可直接开启**

```
第三方应用调用WLAN接口时，需要进行弹框提示（需要包含确定和取消）

提交记录：
http://192.168.4.5:8083/#/c/android/platform/packages/modules/Wifi/+/57717/
```

![image-20240507192920318](image-20240507192920318.png)

------

**卡机引导明示为英文，需点确认后才能更改语言**

```
开机向导需要默认显示中文

提交记录：
http://192.168.4.5:8083/#/c/android/platform/build/+/43438/
```

![image-20240507195423681](image-20240507195423681.png)

------

**蓝牙读联系人行为未明示（蓝牙开启状态下，新建联系人）**

```
有以下修改仍然反馈此问题，可以申请复测，可能可以PASS
或是提供声明：这是Google AOSP原生设计行为，联系人更新（增/删），Bluetooth就会去获取最新联系人信息，Bluetooth进程是platform组件，非第三方apk不存在隐私问题 

提交记录：
http://192.168.4.5:8083/#/c/MTK/alps-release-p0.mp1-tb/+/50226/
```

![image-20240507201113520](image-20240507201113520.png)

------

**语音通话---该设备语音未默认开启免提通话**

```
接收与拨打电话时需要设置默认开启免提通话

提交记录：
http://192.168.4.5:8083/#/c/android/alps/device/datalogic/dl36/+/44036/
http://192.168.4.5:8083/#/c/android/alps/vendor/mediatek/proprietary/packages/services/Telecomm/+/44037/
```

![image-20240507195847775](image-20240507195847775.png)

------

