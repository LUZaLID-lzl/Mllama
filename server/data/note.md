### **设置亮度值** 

```
Settings.System.putInt(mContext.getContentResolver(), Settings.System.SCREEN_BRIGHTNESS, value);
```



### **GMS测试方法**

CTS:
```
./cts-tradefed
CtsLocationFineTestCases
run cts -m CtsAccessibilityServiceTestCases -t android.accessibilityservice.cts.AccessibilityViewTreeReportingTest#testAddViewToLayout_receiveSubtreeEvent
```


GTS-ON-GSI & VTS
```
For cts-on-gsi:
adb reboot bootloader
fastboot flashing unlock 之后按⾳量上键解锁。
fastboot reboot fastboot (⼿机会重启然后进⼊另⼀个界⾯，⼿机上不需要⼿动进⾏任何操作)
fastboot flash system system.img (刷⼊⾕歌的GSI镜像)
fastboot reboot bootloader（⼿机会重启并进⼊fastboot mode）
fastboot flashing lock（加锁）
fastboot reboot

For vts：
adb reboot bootloader
fastboot flashing unlock 之后按⾳量上键解锁。
fastboot flash boot boot-debug.img (刷⼊out包中的boot-debug.img)
fastboot reboot fastboot (⼿机会重启然后进⼊另⼀个界⾯，⼿机上不需要⼿动进⾏任何操作)
fastboot flash system system.img (刷⼊⾕歌的GSI镜像)
fastboot reboot
```


### **保持屏幕常亮**

 getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);



### **添加selinux** 

avc: denied { read } for comm="om.mbw.testcase" name="onFEMChanged" dev="sysfs" ino=22767 scontext=u:r:system_app:s0 tcontext=u:object_r:sysfs:s0 tclass=file permissive=1 

分析过程： 
缺少什么权限：      { read }
权限， 谁缺少权限：        scontext=u:r:system_app:s0 
对哪个文件缺少权限：tcontext=u:object_r:sysfs
什么类型的文件：    tclass=file 
完整的意思： system_app进程对sysfs类型的file缺少read权限。 

解决方法：
定义一个上下文 赋予读写查的权限: allow system_app sysfs_fem_changes:file { read open write getattr };  (system_app.te) 
赋予属性: type sysfs_fem_changes, sysfs_type, fs_type; (file.te) 
/sys/devices/platform/proinfo_data/onFEMChanged    u:object_r:sysfs_fem_changes:s0  (file_contexts)


### **使用反射访问包名代码** 

``` java
public boolean isDeviceUpgrading() {

​	boolean isDeviceUpgrading = false;

​	try {

​		Class honeywellSystemManagerServiceClass = Class.forName("com.android.server.pm.PackageManagerService");

​		Constructor con = honeywellSystemManagerServiceClass.getDeclaredConstructor(Context.class);

​		Object obj = con.newInstance(this);
    
			Method isDeviceUpgradingMethod = honeywellSystemManagerServiceClass.getDeclaredMethod("isDeviceUpgrading()");    

​		sDeviceUpgradingMethod.setAccessible(true);

​		isDeviceUpgrading = (boolean)isDeviceUpgradingMethod.invoke(obj);

​		}catch (Exception e) {

​			e.printStackTrace();

​		}

​		return isDeviceUpgrading;

​	}

saveFlag=pressed;

}
```



### **#include 尖括号和双引号的区别**

1 加双引号表示，应用程序先在当前的文件夹里面寻找该[头文件](https://so.csdn.net/so/search?q=头文件&spm=1001.2101.3001.7020)，若没有找到，再到系统文件夹里去找。一般加双引号多为自己编写的头文件。

2  加尖括号则表示，应用程序直接到系统文件夹去找该文件。这类多为系统头文件。



### **本地代码更新至以前版本**

先将项目拉取代码命令复制下来

```
repo init -u ssh://192.168.4.5:29418/manifest -b maidu -m maidu/dl35/DL35_Q_DEV.xml --repo-url ssh://192.168.4.5:29418/tools/repo --repo-branch stable --no-repo-verify;repo sync -c -d -j4 --no-tags
```

在.repo下找到之前的版本，将**maidu/dl35/DL35_Q_DEV.xml**路径替换 重新执行代码dailybuild/dl36_r_dev/DL36_R_DEV_3.00.03.20220713_USERDEBUG_284.xml

通过**ll .repo**可以查看当前manifist指向的文件



### **GIT仓库拉取失败**

![image-20240511102825906](image-20240511102825906.png)

```
执行完此步骤后再重新拉取代码

rm -rf .repo/manifests
rm -rf .repo/repo
```



### **清空repo仓库的修改**

```
repo forall -c "git reset --hard;git clean -fd";repo sync -c -d
```



### **android源码结构**

```
├── bionic    android上实现的libc库
├── bootable  存放可启动项，如recovery、bootloader等
├── build     android编译系统所用到的make文件及其它工具
├── cts       android兼容性测试
├── dalvik    dalvik虚拟机
├── development  与开发相关的一些东西
├── device    存放需要适配的设备信息
├── external  第三方库
├── frameworks  framework部分
├── hardware  硬件相关代码
├── kernel    kernel相关代码
├── libcore   android上实现的Java基础库
├── Makefile
├── ndk
├── out       编译输出目录
├── packages  包含系统应用、壁纸应用、内容提供者、输入法等
├── prebuilt  预编译好的工具
├── sdk       sdk相关内容
├── system    操作系统层次的一些可执行程序和配置文件
├── u-boot    用于引导linux启动的u-boot
└── vendor    存放与厂商相关的信息，也可粗放需要适配的设备信息
```



### **android系统启动流程**

```
1、启动电源以及系统启动 -> 当电源按下时，引导芯片代码从预定义的地方（固化在ROM中）开始执行。加载引导程序BootLoader到RAM，然后执行。

2、引导程序BootLoader -> 引导程序BootLoader是在android操作系统开始运行前的一个小程序，他的主要作用是把系统OS拉起来并运行。

3、Linux内核启动 -> 当内核启动时，设置缓存、被保护存储器、计划列表、加载驱动。当内核完成系统设置时，它首先在系统文件中寻找init.rc文件，并启动init进程。

4、init进程启动 -> 初始化和启动属性服务，并且启动Zygote进程。

5、Zygote进程启动 -> 创建Java虚拟机并为Java虚拟机注册JNI方法，创建服务器端Socket，启动SystemServer进程。

6、SystemServer进程启动 -> 启动Binder线程池和SystemServiceManager，并且启动各种系统服务。

7、Launcher启动 -> 被SystemServer进程启动的AMS会启动Launcher，Launcher启动后会将已安装应用的快捷图标显示到界面上。
```



### **匿名类创建线程**

```java
new Thread(() -> {
	while(true){
		//TODO
		Thread.sleep(1000);
	}
}).start();

new Thread(){
	@Override
    public void run(){
        super.run();
    }
}.start();
```



### **匿名注册广播**

```java
mContext.registerReceiver(new BroadcastReceiver() {
    @Override
    public void onReceive(Context context, Intent intent) {

    }
}, new IntentFilter(Intent.ACTION_BOOT_COMPLETED));
```



### **输入gsi镜像**

```
打开OEM开关
adb reboot bootloader
fastboot flashing unlock -> 按音量上键确认
fastboot reboot fastboot
fastboot flash system system.img
音量下键选择recovery,power确认,选择恢复出厂设置(Wipe data/factory reset -> factory reset)，然后开机(reboot system now)
```



### **自定义属性值**

生成在out/../system的build.prop里     >>>	

1:devices/mobydata/m82/system.prop   persist.sys.aod.default=0

2: device/datalogic/dl35/device.mk        PRODUCT_PROPERTY_OVERRIDES += persist.sys.aod.default=0



### **Adb Remount步骤**

```
1.打开OEM unlock的开关
2.adb reboot bootloader
3.fastboot flashing unlock
4.fastboot reboot
5.adb root
6.adb disable-verity && adb reboot(1-6为前置条件，需要先将手机解锁)
然后进行验证：
7.adb root && adb remount（remount成功）  
```



### **自定义文件夹内和Hotseat的应用**

Path1 :[packages](http://192.168.4.16:8080/source/xref/dl36_r_dev/packages/)/[apps](http://192.168.4.16:8080/source/xref/dl36_r_dev/packages/apps/)/[Launcher3](http://192.168.4.16:8080/source/xref/dl36_r_dev/packages/apps/Launcher3/)/[res](http://192.168.4.16:8080/source/xref/dl36_r_dev/packages/apps/Launcher3/res/)/[xml](http://192.168.4.16:8080/source/xref/dl36_r_dev/packages/apps/Launcher3/res/xml/)/[default_workspace_4x4.xml]   ps:path1一般会覆盖path2的修改

Path2 :vendor/partner_gms/apps/GmsSampleIntegration



### **gradew编译apk**

```
./gradlew assemble
```



### **git解决冲突 part1**

```
1.到对应的仓库下回退到提交之前那个版本，然后更新最新的仓库 (git pull)

2.cherry-pick gerrit的改动到仓库

3.git status 查看文件状态 对both modified:进行修改，解决冲突

4.解决完以后 git cherry-pick --continue

5.git add -> git commit -> git push origin HEAD:refs/for/dl36_s_vnd_dev
```



### **替换系统的默认静态壁纸**

path1:  alps/frameworks/base/core/res/res目录下drawable-nodpi/drawable-xhpi/drawable-xxhdpi/drawable-xxxhdpi这四个下面的default_wallpaper。

path2:  devices/datalogic/dl36/overlay/frameworks/base/core/res/res

path3:  vendor/partner_gms/overlay/rvc_beta_overlay/frameworks/base/core/res/res


### 替换开机动画
**bootanimation.zip**文件的问题，开机动画文件需要使用打包的方式进行压缩
![[../../resource/Pasted image 20241216133231.png]]
在part0 part1 desc.txt 相同的路径下执行以下指令（**Ubuntu**）：
**zip -r -0 bootanimation.zip part0 part1 desc.txt**
在当前路径下会生成图中的**bootanimation.zip**，这个文件开机时才可以打开。

### **主机Ubuntu 虚拟机Virtualbox 下安装win10 无法识别USB **

```
首先确认安装了VM Virtualbox增强包
wiFiEnabledState == WifiManager.WIFI_STATE_ENABLING
                    || wiFiEnabledState
需要一个USB用户组，可以用vboxusers这个在安装VirtualBox的时候产生的用户组，把你使用的这个用户加到vboxusers组中，确保该用户是否有权限去读写usbfs这个文件系统
$ cat /etc/group | grep vboxusers
vboxusers:x:127:
$ whoami
liziluo

把liziluo用户加到vboxusers组中，后面的liziluo就是你自己的用户名
$ sudo adduser liziluo vboxusers

完成后重启电脑
```



### **apk平台签名**

```
java -D java.library.path=out_sys/host/linux-x86/lib64 -jar out_sys/host/linux-x86/framework/signapk.jar device/datalogic/security/platform.x509.pem device/datalogic/security/platform.pk8 '/home/liziluo/TemporaryFile/CameraImagingSwitch.apk' /home/liziluo/LUZaLID/CameraImagingSwitch.apk

password : cat device/datalogic/security/password
```



### **MTKlog开机自启**

不同机型配置路径有些微差异，生效的文件路径在device/mediatek/system/common/mtklog下的mtklog-config-basic-user.prop　mtklog-config-bsp-user.prop文件中的属性值设为true即可。

可以根据自身需求，通过改变属性设置，自动开启不同的的Log。
```
com.mediatek.log.mobile.enabled = true
com.mediatek.log.modem.enabled = true
com.mediatek.log.net.enabled = true
com.mediatek.log.connsysfw.enabled = true
com.mediatek.log.gpshost.enabled = true
com.mediatek.log.bthost.enabled = true
```


### **selinux中的non_plat(vendor)上下文赋予set权限**

1. plat_public中将上下文设置为system_public_prop --- Properties with no restrictions

   be like : system_public_prop(vendor_hwservicemanager_prop)

2. 在对应的te中setprop

   be like : set_prop(system_app, vendor_hwservicemanager_prop)

​	同理，对于需要read权限的plat_private(system)上下文需要使用getprop



### **移除应用**

1.在.mk文件中找到对应包的PRODUCT_PACKAGES +=将其注释，可能会有覆盖导致不生效，需要全局查看

2.在PKMS的assertPackageIsValid中去判断，根据包名判断到则抛出安装失败异常

```
if ("com.google.android.dialer".equals(pkg.getPackageName()){
                throw new PackageManagerException(INSTALL_FAILED_DUPLICATE_PACKAGE,
                        "forbid install " + pkg.getPackageName());
            }
```



### **ADB安装应用校验失败**

eg：adb: failed to install xxx.apk: Failure [INSTALL_FAILED_VERIFICATION_FAILURE]   

可以试试：

```
adb shell settings put global verifier_verify_adb_installs 0

adb shell settings put global package_verifier_enable 0
```



### **长按电源键弹出的对话框**

在frameworks\base\policy\src\com\android\internal\policy\impl\GlobalActions.java文件中

在GlobalActionsDialog方法可以看 mItems.add这个方法是添加菜单选项的



### **设置系统默认语言**

1.修改PRODUCT_LOCALES字段

在buildinfo.sh中，echo "ro.product.locale=$PRODUCT_DEFAULT_LOCALE"

关于这个PRODUCT_DEFAULT_LOCALE又在build/core/Makefile下找到PRODUCT_DEFAULT_LOCALE="$(call get-default-product-locale,$(PRODUCT_LOCALES))"

继续查找get-default-product-locale、

```
define get-default-product-locale
$(strip $(subst _,-, $(firstword $(1))))
endef
```

在这里，可以看到是选择第一个。
系统默认语言是英语，如果你要修改为中文，只需把PRODUCT_LOCALES := en_US zh_CN fr_FR it_IT es_ES de_DE nl_NL cs_CZ pl_PL中zh_CN移到最前就可以了
或者你直接将build.sh中echo "ro.product.locale=zh-CN"改为你需要的语言。

2:修改build/tools/buildinfo.sh

```
echo "persist.sys.language=zh"
echo "persist.sys.country=CN"
echo "persist.sys.localevar="
echo "persist.sys.timezone=Asia/Shanghai"
echo "ro.product.locale.language=zh"
echo "ro.product.locale.region=CN"
```



### **设置应用为可卸载**

在这个xml文件中将包名加进去
vendor/mediatek/proprietary/frameworks/base/data/etc/pms_sysapp_removable_system_list.txt



### **MTK应用调度策略**

vendor/mediatek/proprietary/hardware/power/config/mt6765/app_list/power_whitelist_cfg.xml



### **ANR**

1：KeyDispatchTimeout(5 seconds) --主要类型  按键或触摸事件在特定时间内无响应

2：BroadcastTimeout(10 seconds)  BroadcastReceiver在特定时间内无法处理完成

3：ServiceTimeout(20 seconds) --小概率类型  Service在特定的时间内无法处理完成

UI线程主要包括如下：

Activity:onCreate(), onResume(), onDestroy(), onKeyDown(), onClick(),etc

AsyncTask: onPreExecute(), onProgressUpdate(), onPostExecute(), onCancel,etc

Mainthread handler: handleMessage(), post*(runnable r), etc

首先排查有没有在子线程中更新UI的操作

从LOG可以看出ANR的类型，CPU的使用情况，如果CPU使用量接近100%，说明当前设备很忙，有可能是CPU饥饿导致了ANR

如果CPU使用量很少，说明主线程被BLOCK了

如果IOwait很高，说明ANR有可能是主线程在进行I/O操作造成的


### **亮度配置**

修改默认屏幕亮度：\frameworks\base\packages\SettingsProvider\res\values\defaults.xml

```xml
<!-- Default screen brightness, from 0 to 255.  102 is 40%. -->
<integer name="def_screen_brightness">102</integer>
```

修改默认屏幕亮度最大值和最小值：\frameworks\base\core\res\res\values\config.xml

```xml
<!-- Minimum screen brightness setting allowed by the power manager.
     The user is forbidden from setting the brightness below this level. -->
<integer name="config_screenBrightnessSettingMinimum">10</integer>
 
<!-- Maximum screen brightness allowed by the power manager.
     The user is forbidden from setting the brightness above this level. -->
<integer name="config_screenBrightnessSettingMaximum">204</integer>
```



### **framwork下赋予应用权限**

frameworks/base/services/core/java/com/android/server/pm/permission/DefaultPermissionGrantPolicy.java

```java
 		// Print Spooler
        grantSystemFixedPermissionsToSystemPackage(pm, PrintManager.PRINT_SPOOLER_PACKAGE_NAME,
                userId, ALWAYS_LOCATION_PERMISSIONS);

        // EmergencyInfo
        grantSystemFixedPermissionsToSystemPackage(pm,
                getDefaultSystemHandlerActivityPackage(pm,
                        TelephonyManager.ACTION_EMERGENCY_ASSISTANCE, userId),
                userId, CONTACTS_PERMISSIONS, PHONE_PERMISSIONS);

```



### **生成签名**

使用Android源码中自带的make_key工具来生成签名，路径为development/tools/make_key 

在Android系统源码根目录下,新建make_key_security目录,进入到该目录，执行下面的命令

```
  ../development/tools/make_key releasekey '/C=US/ST=California/L=Mountain View/O=Android/OU=Android/CN=Android/emailAddress=liziluo@liziluo-mdsw'
```



### **判断当前线程是否为主线程**

```
1: Looper.getMainLooper() == Looper.myLooper();
2: Looper.getMainLooper().getThread() == Thread.currentThread();
3: Looper.getMainLooper().getThread().getId() == Thread.currentThread().getId();
```



### **PKMS中跳过APK安装**

```java
assertPackageIsValid()

if ("com.abfota.systemUpdate".equals(pkg.packageName)){
   throw new PackageManagerException(INSTALL_FAILED_DUPLICATE_PACKAGE,
   "Application package " + pkg.packageName
   + " already installed.  Skipping duplicate.");
}	
```



### **去除状态栏图标**

```xml
vendor/mediatek/proprietary/packages/apps/SystemUI/res/values/config.xml

<string name="quick_settings_tiles_default" translatable="false">
        wifi,bt,dnd,flashlight,rotation,battery,cell,airplane,cast
</string>

<string name="quick_settings_tiles_stock" translatable="false">
        wifi,cell,battery,dnd,flashlight,rotation,bt,airplane,location,hotspot,inversion,saver,work,cast,night
</string>

<string name="quick_settings_tiles_retail_mode" translatable="false">
        cell,battery,dnd,flashlight,rotation,location
</string>   
```



### **Android常用广播**

| 广播名                                          | 说明                                                         | 备注                                                         |
| ----------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Intent.ACTION_AIRPLANE_M                        | 关闭或打开飞行模式时的广播                                   |                                                              |
| Intent.ACTION_BATTERY_CH                        | 充电状态，或者电池的电量发生变化                             | 电荷级别改变，只能在代码注册                                 |
| Intent.ACTION_BATTERY_LO                        | 电池电量低                                                   |                                                              |
| Intent.ACTION_BATTERY_OK                        | 电池电量充足                                                 |                                                              |
| Intent.ACTION_AIRPLANE_MODE_CHANGED             | 关闭或打开飞行模式                                           |                                                              |
| Intent.ACTION_BATTERY_CHANGED                   | 充电状态，或者电池的电量发生变化                             | 电荷级别改变，只能在代码注册                                 |
| Intent.ACTION_BATTERY_LOW                       | 电池电量低                                                   |                                                              |
| Intent.ACTION_BATTERY_OKAY                      | 电池电量充足                                                 | 从电池电量低变化到饱满时会发出广播                           |
| Intent.ACTION_BOOT_COMPLETED                    | 在系统启动完成后，这个动作被广播一次                         | 只有一次                                                     |
| Intent.ACTION_CAMERA_BUTTON                     | 按下照相时的拍照按键时发出的广播                             | 硬件按键                                                     |
| Intent.ACTION_CLOSE_SYSTEM_DIALOGS              | 当屏幕超时进行锁屏时,当用户按下电源按钮,长按或短按(不管有没跳出话框)，进行锁屏 |                                                              |
| Intent.ACTION_CONFIGURATION_CHANGED             | 设备当前设置被改变时发出的广播                               | 界面语言，设备方向，等 请参考Configuration.java              |
| Intent.ACTION_DATE_CHANGED                      | 设备日期发生改变时                                           |                                                              |
| Intent.ACTION_DEVICE_STORAGE_LOW                | 设备内存不足时发出的广播                                     | 此广播只能由系统使用，其它APP不可用                          |
| Intent.ACTION_DEVICE_STORAGE_OK                 | 设备内存从不足到充足时发出的广播                             | 此广播只能由系统使用，其它APP不可用                          |
| Intent.ACTION_EXTERNAL_APPLICATIONS_AVAILABLE   | 移动APP完成之后，发出的广播                                  | 移动是指:APP2SD                                              |
| Intent.ACTION_EXTERNAL_APPLICATIONS_UNAVAILABLE | 正在移动APP时，发出的广播                                    | 移动是指:APP2SD                                              |
| Intent.ACTION_GTALK_SERVICE_CONNECTED           | Gtalk已建立连接时发出的广播                                  |                                                              |
| Intent.ACTION_GTALK_SERVICE_DISCONNECTED        | Gtalk已断开连接时发出的广播                                  |                                                              |
| Intent.ACTION_HEADSET_PLUG                      | 在耳机口上插入耳机时发出的广播                               |                                                              |
| Intent.ACTION_INPUT_METHOD_CHANGED              | 改变输入法时发出的广播                                       |                                                              |
| Intent.ACTION_LOCALE_CHANGED                    | 设备当前区域设置已更改时发出的广播                           |                                                              |
| Intent.ACTION_MANAGE_PACKAGE_STORAGE            | 表示用户和包管理所承认的低内存状态通知应该开始               |                                                              |
| Intent.ACTION_MEDIA_BAD_REMOVAL                 | 未正确移除SD卡                                               | 扩展卡已经从SD卡插槽拔出，但是挂载点 (mount point) 还没解除 (unmount) |
| Intent.ACTION_MEDIA_BUTTON                      | 按下”Media Button” 按键时发出的广播                          | 有”Media Button” 按键的话(硬件按键)                          |
| Intent.ACTION_MEDIA_CHECKING                    | 插入外部储存装置                                             | 比如SD卡时，系统会检验SD卡，此时发出的广播                   |
| Intent.ACTION_MEDIA_EJECT                       | 已拔掉外部大容量储存设备发出的广播                           | 不管有没有正确卸载                                           |
| Intent.ACTION_MEDIA_MOUNTED                     | 插入SD卡并且已正确安装                                       | 扩展介质被插入而且已经被挂载                                 |
| Intent.ACTION_MEDIA_NOFS                        | 拓展介质存在，但使用不兼容FS（或为空）的路径安装点检查介质包含在Intent.mData领域 |                                                              |
| Intent.ACTION_MEDIA_REMOVED                     | 外部储存设备已被移除，扩展介质被移除                         | 不管有没正确卸载,都会发出此广播                              |
| Intent.ACTION_MEDIA_SCANNER_FINISHED            | 已经扫描完介质的一个目录                                     |                                                              |
| Intent.ACTION_MEDIA_SCANNER_SCAN_FILE           | 请求媒体扫描仪扫描文件并将其添加到媒体数据库                 |                                                              |
| Intent.ACTION_MEDIA_SCANNER_STARTED             | 开始扫描介质的一个目录                                       |                                                              |
| Intent.ACTION_MEDIA_SHARED                      | 扩展介质的挂载被解除 (unmount)                               | 它已经作为 USB 大容量存储被共享                              |
| Intent.ACTION_PACKAGE_ADDED                     | 成功的安装APK                                                | 数据包括包名（最新安装的包程序不能接收到这个广播）           |
| Intent.ACTION_PACKAGE_CHANGED                   | 一个已存在的应用程序包已经改变                               | 包括包名                                                     |
| Intent.ACTION_PACKAGE_DATA_CLEARED              | 清除一个应用程序的数据时发出的广播                           | 清除包程序不能接收到这个广播                                 |
| Intent.ACTION_PACKAGE_INSTALL                   | 触发一个下载并且完成安装时发出的广播                         | 比如在电子市场里下载应用                                     |
| Intent.ACTION_PACKAGE_REMOVED                   | 成功的删除某个APK之后发出的广播                              | 正在被安装的包程序不能接收到这个广播                         |
| Intent.ACTION_PACKAGE_REPLACED                  | 替换一个现有的安装包时发出的广播（不管现在安装的APP比之前的新还是旧 |                                                              |
| Intent.ACTION_PACKAGE_RESTARTED                 | 用户重新开始一个包                                           | 重新开始包程序不能接收到这个广播                             |
| Intent.ACTION_POWER_CONNECTED                   | 插上外部电源时发出的广播                                     |                                                              |
| Intent.ACTION_POWER_DISCONNECTED                | 已断开外部电源连接时发出的广播                               |                                                              |
| Intent.ACTION_REBOOT                            | 重启设备时的广播                                             |                                                              |
| Intent.ACTION_SCREEN_OFF                        | 屏幕被关闭之后的广播                                         |                                                              |
| Intent.ACTION_SCREEN_ON                         | 屏幕被打开之后的广播                                         |                                                              |
| Intent.ACTION_SHUTDOWN                          | 关闭系统时发出的广播                                         |                                                              |
| Intent.ACTION_TIMEZONE_CHANGED                  | 时区发生改变时发出的广播                                     |                                                              |
| Intent.ACTION_TIME_CHANGED                      | 时间被设置时发出的广播                                       |                                                              |
| Intent.ACTION_TIME_TICK                         | 当前时间已经变化（正常的时间流逝）                           | 每分钟都发送，只能通过来注册                                 |
| Intent.ACTION_UID_REMOVED                       | 一个用户ID已经从系统中移除发出的广播                         |                                                              |
| Intent.ACTION_UMS_CONNECTED                     | 设备已进入USB大容量储存状态时发出的广播                      |                                                              |
| Intent.ACTION_UMS_DISCONNECTED                  | 设备已从USB大容量储存状态转为正常状态时发出的广播            |                                                              |
| Intent.ACTION_WALLPAPER_CHANGED                 | 设备墙纸已改变时发出的广播                                   |                                                              |
| Intent.ACTION_USER_PRESENT                      | 用户唤醒设备                                                 |                                                              |
| Intent.ACTION_NEW_OUTGOING_CALL                 | 拨打电话                                                     |                                                              |



### **上层去除NFC功能**

注释hardware/nxp/nfc/1.1/android.hardware.nfc@1.1-service.rc文件中所有的内容

正常情况下nfc服务起不来，设置里的NFC相关都会被删除，如果没被删除，可以确认以下文件的信息

正常去除了服务，mNfcAdapter是为空的，所以相关的控件都会不显示

```java
vendor/mediatek/proprietary/packages/apps/MtkSettings/src/com/android/settings/nfc/NfcPreferenceController.java

    @Override
    @AvailabilityStatus
    public int getAvailabilityStatus() {
        return mNfcAdapter != null
                ? AVAILABLE
                : UNSUPPORTED_ON_DEVICE;
    }

```



