### A11 upgrade to A13

问题背景：

1. The final user shall be allowed to perform the software OTA upgrade of the product from Android 11 to Android 13.

2. The final user shall be allowed to perform the software OTA downgrade of the product from Android 13 to Android 11, with factory reset or with enterprise reset.

   

想要A11跨版本升级到A13，首先需要将分区进行对齐，A13必须保持与A11拥有相同的可刷入分区，并且分区的起始位置也需要保持一致。

目前碰到的问题是：
SUPER分区是由product+system+vendor以及一些其他信息组成的，但是由于A13的GMS包增大以及system增大，导致在A11上定义的SUPER分区大小在A13上不够使用，以下是各版本的分区大小对比：

| TEST TYPE       | product | system | vendor |
| --------------- | ------- | ------ | ------ |
| A11 + GMS       | 1.7G    | 1.2G   | 310M   |
| A13 driver only | 43M     | 1.5G   | 366M   |
| A13 + GMS       | 2.2G    | 1.6G   | 349M   |

SUPER SIZE在A11上定义的为4GB，可以看到A11合入GMS包之后还有700MB左右的富余空间，但是A13在合入GMS包之后，SUPER整体大小来到了4.2GB，超出了A11定义的大小余200MB，所以需要缩减分区大小。



目前解决方案：
对于一些GMS包中的可选应用取消预制，包括以下APP（取消预制后，没有override的应用将不会存在，有override的应用将会采用原生APP或是MTK的APP）：

| 序号  | GMS optional application packages                    | A11      | A12      | A13      | override                                                  |
| :-: | ---------------------------------------------------- | -------- | -------- | -------- | --------------------------------------------------------- |
|  1  | AndroidSystemIntelligence_Features    (only a12 a13) | /        | 34.4 MB  | 38.9 MB  | /                                                         |
|  2  | CalendarGoogle                                       | 26.6 MB  | 28.5 MB  | 28.7 MB  | Calendar <br />GoogleCalendarSyncAdapter<br />MtkCalendar |
|  3  | DeskClockGoogle                                      | 9.1 MB   | 10.3 MB  | 11.2 MB  | /                                                         |
|  4  | LatinImeGoogle                                       | 74.7 MB  | 79.0 MB  | 70.5 MB  | LatinIME                                                  |
|  5  | TagGoogle                                            | 694.8 kB | 715.7 kB | 683.8 kB | Tag                                                       |
|  6  | talkback                                             | 27.1 MB  | 34.3 MB  | 35.6 MB  | /                                                         |
|  7  | Keep                                                 | 15.9 MB  | 17.2 MB  | 18.6 MB  | /                                                         |
|  8  | CalculatorGoogle                                     | 2.9 MB   | 3.2 MB   | 3.3 MB   | Calculator <br />ExactCalculator                          |
|     | Total                                                | 157MB    | 207.6MB  | 207.5MB  |                                                           |

**可以看到A13的可选应用大小总共加起来为207.5MB，实测去除这些后仍然不够，会在编译时报错，提示super空间不足：**

```
LERROR << "liziluo partition->name() " << partition->name();
LERROR << "liziluo group->name() " << group->name();
LERROR << "liziluo space_needed " << space_needed;
LERROR << "liziluo group->maximum_size() " << group->maximum_size();
LERROR << "liziluo group_size " << group_size;

LERROR << "Partition " << partition->name();
LERROR << "Partition " << partition->name();
```



```
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:660] [liblp]liziluo partition->name() product_a
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:661] [liblp]liziluo group->name() main_a
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:662] [liblp]liziluo space_needed 2203095040
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:663] [liblp]liziluo group->maximum_size() 4292870144
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:666] [liblp]liziluo group_size 0
lpmake I 11-16 16:46:11 211870 211870 builder.cpp:1098] [liblp]Partition product_a will resize from 0 bytes to 2203095040 bytes

lpmake E 11-16 16:46:11 211870 211870 builder.cpp:660] [liblp]liziluo partition->name() system_a
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:661] [liblp]liziluo group->name() main_a
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:662] [liblp]liziluo space_needed 1603473408
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:663] [liblp]liziluo group->maximum_size() 4292870144
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:666] [liblp]liziluo group_size 2203095040
lpmake I 11-16 16:46:11 211870 211870 builder.cpp:1098] [liblp]Partition system_a will resize from 0 bytes to 1603473408 bytes

lpmake E 11-16 16:46:11 211870 211870 builder.cpp:660] [liblp]liziluo partition->name() vendor_a
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:661] [liblp]liziluo group->name() main_a
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:662] [liblp]liziluo space_needed 420454400
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:663] [liblp]liziluo group->maximum_size() 4292870144
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:666] [liblp]liziluo group_size 3806568448
lpmake E 11-16 16:46:11 211870 211870 builder.cpp:768] [liblp]Not enough free space to expand partition: vendor_a

lpmake I 11-16 16:46:11 211870 211870 builder.cpp:1098] [liblp]Partition vendor_a will resize from 0 bytes to 420454400 bytes
lpmake E 11-16 16:46:20 211870 211870 images.cpp:338] [liblp]Image for partition 'vendor_a' is greater than its size (420454400, expected 318767104)
```

所以还需要空余出空间，解决方案是关闭部分GMS应用的DEX优化，关闭之后测试可以正常编译，分区能够对齐，经测试，可以通过OTA包从A11升级到A13，也可以直接通过flash tool直接download升级。



**那么针对以上的解决方案，有以下几个弊端：**

**1：首先是可选应用将不会被预制，目前在进行GMS测试，需要确认会不会对GMS认证有影响**

**2：关闭DEX优化后，首次开机时间会变长，以下是开机时间对比：**

| Fitst-TA分支       | 2023-11-18 (user) <br />未关闭DEX优化 | 2023-12-12 (user) <br />关闭部分GMS应用DEX优化<br />9月MainLine(未压缩) | 2023-12-16 (user) <br />关闭部分GMS应用DEX优化 <br />11月Mainline(压缩) | 本地软件<br />DEX基本全部关闭<br />11月Mainline(压缩) |
| ------------------ | ------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ----------------------------------------------------- |
| 首次开机按下power  | 00:05.50                              | 00:05.37                                                     | 00:06.43                                                     | 00:06.45                                              |
| 首次开机第一屏结束 | 01:12.22 (+01:06.72)                  | 01:12.82 (+01:07.45)                                         | 01:27.81 (+01:21.38)                                         | 01:23.08 (+01:16.63)                                  |
| 首次开机总时间     | 02:00.73 (+00:47.51)                  | 02:53.55 (+01:40.72)                                         | 03:53.00 (+02:25.18)                                         | 03:23.12 (+02:00.03)                                  |
| 二次开机按下power  | 00:06.36                              | 00:06.09                                                     | 00:08.26                                                     | 00:08.89                                              |
| 二次开机第一屏结束 | 01:07.92 (+01:01.57)                  | 01:06.69 (+01:00.60)                                         | 00:31.64 (+00:23.38)                                         | 01:19.51 (+01:10.62)                                  |
| 二次开机总时间     | 01:22.53 (+00:14.61)                  | 01:20.92 (+00:14.23)                                         | 00:49.05 (+00:17.41)                                         | 01:35.70 (+00:16.19)                                  |
| 当前SUPER大小      | 4235MB                                | 3748MB                                                       | 3797MB                                                       | 3748MB                                                |
| SUPER剩余大小      |                                       | 349MB                                                        | 299MB                                                        | 349MB                                                 |

```
Android.bp

android_app {
	name: "xxxxx",
	dex_preopt: {
		enabled: false,
	},
}
```

```
Android.mk

LOCAL_DEX_PREOPT := false
```

du -h --max-depth=1 | sort -hr


```
system:
frameworks/base/
packages/apps/CellBroadcastReceiver/
packages/apps/CertInstaller/
packages/apps/ManagedProvisioning/
packages/apps/Nfc/
packages/apps/RemoteProvisioner/
packages/apps/SecureElement/
packages/apps/StorageManager/
packages/apps/ThemePicker/
packages/apps/Traceur/
packages/providers/BlockedNumberProvider/
packages/providers/DownloadProvider/
packages/providers/MediaProvider/
packages/services/Mtp/
packages/wallpapers/LivePicker/
vendor/datalogic/dl36/
vendor/mediatek/proprietary/operator/frameworks/ims/
vendor/mediatek/proprietary/packages/apps/Dialer/
vendor/mediatek/proprietary/packages/apps/EmergencyInfo/
vendor/mediatek/proprietary/packages/apps/EngineerMode/
vendor/mediatek/proprietary/packages/apps/MTKLogger/
vendor/mediatek/proprietary/packages/apps/MtkSettings/
vendor/mediatek/proprietary/packages/apps/Omacp/
vendor/mediatek/proprietary/packages/apps/SoundRecorder/
vendor/mediatek/proprietary/packages/apps/Stk/
vendor/mediatek/proprietary/packages/apps/SystemUI/
vendor/mediatek/proprietary/packages/apps/VoiceCommand/
vendor/mediatek/proprietary/packages/apps/VoiceUnlock/
vendor/mediatek/proprietary/packages/providers/CalendarProvider/
vendor/mediatek/proprietary/packages/providers/ContactsProvider/
vendor/mediatek/proprietary/packages/services/AtciService/
vendor/mediatek/proprietary/packages/services/Ims/
vendor/mediatek/proprietary/scripts/
vendor/mobiiot/
vendor/partner_gms/

vnd:
device/datalogic/dl36/
device/mediatek/mt6765/
vendor/mediatek/proprietary/custom/
vendor/mediatek/proprietary/tools/ptgen/
```

```
vendor/mediatek/proprietary/packages/apps/SystemUI
git fetch "ssh://liziluo@192.168.4.5:29418/android/alps/vendor/mediatek/proprietary/packages/apps/SystemUI" refs/changes/84/63984/1 && git cherry-pick FETCH_HEAD

vendor/mediatek/proprietary/packages/apps/MtkSettings
git fetch "ssh://liziluo@192.168.4.5:29418/android/alps/vendor/mediatek/proprietary/packages/apps/MtkSettings" refs/changes/85/63985/1 && git cherry-pick FETCH_HEAD

vendor/mediatek/proprietary/packages/apps/Calendar
git fetch "ssh://liziluo@192.168.4.5:29418/android/alps/vendor/mediatek/proprietary/packages/apps/Calendar" refs/changes/86/63986/1 && git cherry-pick FETCH_HEAD

vendor/mediatek/proprietary/packages/apps/EngineerMode
git fetch "ssh://liziluo@192.168.4.5:29418/android/alps/vendor/mediatek/proprietary/packages/apps/EngineerMode" refs/changes/87/63987/1 && git cherry-pick FETCH_HEAD

vendor/mediatek/proprietary/packages/apps/MTKLogger
git fetch "ssh://liziluo@192.168.4.5:29418/android/alps/vendor/mediatek/proprietary/packages/apps/MTKLogger" refs/changes/89/63989/1 && git cherry-pick FETCH_HEAD

frameworks/base
git fetch "ssh://liziluo@192.168.4.5:29418/android/platform/frameworks/base" refs/changes/90/63990/1 && git cherry-pick FETCH_HEAD
```

调试A11-A13  A13-A11 TEE的变化

```
A11->A13
A11：
        Validity
            Not Before: Mar 20 18:07:48 2022 GMT
            Not After : Mar 15 18:07:48 2042 GMT
A13：
        Validity
            Not Before: Mar 20 18:07:48 2022 GMT
            Not After : Mar 15 18:07:48 2042 GMT

A13->A11
A13：
        Validity
            Not Before: Mar 20 18:07:48 2022 GMT
            Not After : Mar 15 18:07:48 2042 GMT
A11：
        Validity
            Not Before: Mar 20 18:07:48 2022 GMT
            Not After : Mar 15 18:07:48 2042 GMT

```

二次开机时间对比

ack boot_progressack

```
A11
41:02-28 14:20:04.406203   535   535 I boot_progress_start: 11159
57:02-28 14:20:06.127171   535   535 I boot_progress_preload_start: 12880
58:02-28 14:20:09.000599   535   535 I boot_progress_preload_end: 15753
60:02-28 14:20:09.576748   956   956 I boot_progress_system_run: 16329
73:02-28 14:20:10.632451   956   956 I boot_progress_pms_start: 17385
76:02-28 14:20:11.194141   956   956 I boot_progress_pms_system_scan_start: 17947
78:02-28 14:20:15.934375   956   956 I boot_progress_pms_data_scan_start: 22687
79:02-28 14:20:15.953809   956   956 I boot_progress_pms_scan_end: 22706
82:02-28 14:20:16.389785   956   956 I boot_progress_pms_ready: 23142
152:02-28 14:20:19.296524   956   956 I boot_progress_ams_ready: 26049
238:02-28 14:20:20.672740   956   980 I boot_progress_enable_screen: 27425


16266
```

```
A13
34:04-28 06:24:58.655876   649   649 I boot_progress_start: 13038
56:04-28 06:25:00.468616   649   649 I boot_progress_preload_start: 14851
59:04-28 06:25:04.018566   649   649 I boot_progress_preload_end: 18401
61:04-28 06:25:05.766729  1142  1142 I boot_progress_system_run: 20149
74:04-28 06:25:07.408330  1142  1142 I boot_progress_pms_start: 21791
131:04-28 06:25:07.893727  1142  1142 I boot_progress_pms_system_scan_start: 22276
133:04-28 06:25:09.410490  1142  1142 I boot_progress_pms_data_scan_start: 23793
134:04-28 06:25:09.425544  1142  1142 I boot_progress_pms_scan_end: 23808
138:04-28 06:25:09.741440  1142  1142 I boot_progress_pms_ready: 24124
187:04-28 06:25:13.189172  1142  1142 I boot_progress_ams_ready: 27571
308:04-28 06:25:16.707419  1142  1162 I boot_progress_enable_screen: 31090

18052
```


#开机流程
“boot_progress_start”代表着Android屏幕点亮，开始显示启动动画，开始闪烁Android字样。
“boot_progress_enable_screen”代表着整个系统启动结束，用这个总时间减去Linux Kernel的启动时间即可得到Android OS部分的时间。

| 阶段                                  | 描述                                                                   |
| ----------------------------------- | -------------------------------------------------------------------- |
| boot_progress_start                 | 系统进入用户空间，标志着kernel启动完成                                               |
| boot_progress_preload_start         | Zygote启动                                                             |
| boot_progress_preload_end           | Zygote结束                                                             |
| boot_progress_system_run            | SystemServer ready,开始启动Android系统服务                                   |
| boot_progress_pms_start             | PMS开始扫描安装的应用                                                         |
| boot_progress_pms_system_scan_start | PMS先行扫描/system目录下的安装包                                                |
| boot_progress_pms_data_scan_start   | PMS扫描/data目录下的安装包                                                    |
| boot_progress_pms_scan_end          | PMS扫描结束                                                              |
| boot_progress_pms_ready             | PMS就绪                                                                |
| boot_progress_ams_ready             | AMS就绪                                                                |
| boot_progress_enable_screen         | AMS启动完成后开始激活屏幕，从此以后屏幕才能响应用户的触摸，它在WindowManagerService发出退出开机动画的时间节点之前 |
| sf_stop_bootanim                    | SF设置service.bootanim.exit属性值为1，标志系统要结束开机动画了                          |
| wm_boot_animation_done              | 开机动画结束，这一步用户能直观感受到开机结束                                               |
