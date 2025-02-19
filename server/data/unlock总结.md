# XQT-518 LOCK/UNLOCK总结 

a11大体上沿用a10之前的修改方法，adb想要remount成功，必须进行fastboot解锁，解锁之后进行adb disable-verity 操作，再执行adb root →  adb remount操作



操作流程:
1.打开OEM unlock的开关
2.adb reboot bootloader
3.fastboot flashing unlock
4.fastboot reboot
5.adb root
6.adb disable-verity && adb reboot(1-6为前置条件，需要先将手机解锁)
然后进行验证：
7.adb root && adb remount（remount成功）



修改文件:

![](unlock-change.png)

## 定义属性值，通过修改ro.adb.secure和ro.secure让进程名称可见

根据dl释放的文件，定义对应的属性值，并将属性值写入到文件当中。将ro.adb.secure设为0默认打开usb调试不弹框

**build/core/main.mk**

![](/home/liziluo/Pictures/1.png)

**build/core/Makefile**

![](/home/liziluo/Pictures/2.png)

将定义好的属性值写入到system/etc/prop.default_root当中,为其添加上下文的权限，分配权限组



在**system/sepolicy / prebuilts/api/30.0/private/file_contexts**和**system/sepolicy / private/file_contexts**中添加上下文：default_root\.prop u:object_r:rootfs:s0



**system/core/libcutils/fs_config.cpp**

![](/home/liziluo/Pictures/4.png)

**vender/mediatek/proprietary/bootable/bootloader/lk/app/mt_boot/mt_boot.c**

![](/home/liziluo/Pictures/5.png)

创建一个属性值secreboot，当值为48时能够进行unlock操作 ，在bsp_api.h中定义了，初始值为49，

为了方便调试，现在将其设置为48



## 修改SELinux权限为Permissive

本来是按照之前a10的改法，在selinux.cpp中IsEnforcing() 直接返回false，这样改了直接跑不起来，开机就进入fastboot模式，显然a11在user模式下，不允许关闭selinux

将SelinuxInitialize()中的这段话注释，可以开机但是无法关闭selinux

**PLOG(FATAL) << "security_setenforce(" << (is_enforcing ? "true" : "false")**

**<< ") failed";**

**11 eng** **版本，默认烧写后 enforce 即为 Permissive，在之前的低版本 eng 中，默认 enforce 为 Enforcing**

通过跟踪代码，发现关闭selinux方法在selinux_enforcing_boot 默认值定义由**CONFIG_SECURITY_SELINUX_DEVELOP** 决定

通过全局搜索，在kernel-4.19\kernel\configs\userdebug.config 中定义了 **CONFIG_SECURITY_SELINUX_DEVELOP=y**

而且通过vnd_dl36.mk可知，eng版本并没有引入userdebug.config，这也就能解释为什么之前说的

eng版本为 **Permissive**，所以在user中引入userdebug.config即可关闭selinux

**!!!!!!!后续发现**引入userdebug,config会导致在开机弹框(当前设备出现了一些问题，请联系您的制造商) 所以不能引入userdebug.config，只需要在

dl36_defconfig中加入CONFIG_SECURITY_SELINUX_DEVELOP=y即可



**kernel-4.19/arch/arm64/configs/dl36_defconfig**

![image-20220615141710439](/home/liziluo/.config/Typora/typora-user-images/image-20220615141710439.png)

**system/core/init/selinux.cpp**

![](/home/liziluo/Pictures/7.png)

## 解锁fastboot，关闭verity

**system/core/adb/Android.bp**

![](/home/liziluo/Pictures/8.png)

**system/core/adb/daemon/main.cpp**

![](/home/liziluo/Pictures/9.png)


**system/core/set-verity-state/set-verity-state.cpp**

![](/home/liziluo/Pictures/10.png)

**system/core/fs_mgr/fs_mgr_verity.cpp**

![](/home/liziluo/Pictures/11.png)

## 加载属性值property 进行adb root

**在上一个版本当中，PropertyLoadBootDefaults()是在init.cpp中执行的，而a11是在property_services.cpp的	PropertyInit()当中，根据原生的方法，写了一个想要加载自己属性文件的方法，再到init.cpp中进行判断seureboot的值是否为48，加载不同的属性文件**

**但是发现这样操作并没有正确的加载属性值，ro.debuggle始终为0**

**因为 PropertyInit的存在，在初始化的时候已经加载的属性文件，所以我们可以转变思路**

**在 PropertyLoadBootDefaults中进行secreboot的判断，将原生的属性文件替换成我们root的文件，更改属性值ro.debuggle = 1，得以adb root**

**system/core/init/property_services.cpp**

![](/home/liziluo/Pictures/12.png)


**通过getprop可以查看到当前的属性值，adb shell进去就直接执行了su，adb root完成**

![](/home/liziluo/Pictures/13.png)

## adb remount

**经过以上的操作，重新进行烧录，按照操作步骤的流程，已经可以进行adb root ，关闭verity等操作，然后重启机器 准备进行remount**

发现了报错：**system/bin/sh:remount :inaccessible or not found**

**remount****命令不存在 ，进入system/bin目录下查看，发现编译后的out下缺少remount可执行文件**

**在debug版本下remount文件是存在，推测user版本并不编译remount对应模块**

**按照编译模块的格式全局搜索“remount ”**

**build/target/product/base_system.mk**

![](/home/liziluo/Pictures/14.png)

**在  base_system.mk  文件中PRODUCT_PACKAGES_DEBUG加载了remount模块**

**证实了我们的猜想，所以在基础模块下加入remount即可编译出文件**

**PRODUCT_PACKAGES += remount**

**重新编译 但是在编译的过程中报错了**

![](/home/liziluo/Pictures/15.png)

**在system/core/fs_mgr下未定义方法**

**可能是编译remount模块需要相关的依赖，然后在查阅资料之后发现**

**只需要在android.bp中将allow-dabd-disable-verity打开即可**



**system/core/fs_mgr/android.bp**

![](/home/liziluo/Pictures/18.png)


**重新进行编译烧录，执行操作流程**

**在执行完adb disable-verity要重新启动让其生效**

![](/home/liziluo/Pictures/17.png)

**adb remount之后进入system目录下随便删除一个文件进行测试**

**rm -rf之后文件删除**

**remount成功**

## 编译unlock的factory.img进行测试

测试成功之后，记得将之前在mt_boot.c中设置的secureboot = 48清除 

secureboot在load_image.c中会从factory分区中读出来

所以我们需要进行验证，当刷入普通的factory.img时，设备不允许unlock

刷入unlock的factory.img时，设备可以unlock

本地编译unlock的factory.img方法：

**make out/target/product/dl35/factory.img secure_boot_type="0x30"**

**到此unlock就结束了 有错误的地方欢迎大家指出**

![]()
