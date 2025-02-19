------
#### 问题背景

DL36项目从A11升级到A13，由于GMS包以及系统空间增大，导致SUPER分区超过A11定义的大小（4G）。但是OTA升级需要保持分区大小的一致，遂将大部分应用的DEX预编译给关闭了，节省出一大部分空间，此时已经可以使分区保持一致去进行OTA升级。
但是由于预编译被关闭了，导致应用的DEX优化操作从编译阶段转变到首次开机过程中，使得开机时间变长（大概多了1分40秒），客户无法接收开机时间过长。后续更改了DEX优化的流程，将其延迟到开机之后在后台静默优化更新。



#### DEX概述

DEX（Dalvik Executable）是Android平台上的一种字节码格式，用于在Dalvik虚拟机上执行应用程序。DEX文件包含了Android应用程序的可执行代码，以及相关的类、方法等信息。DEX文件是在构建Android应用时生成的，并且通常包含应用的所有Java类。

DEX优化是指对这些DEX文件进行一系列优化操作，以提高应用的性能、减小应用包的大小等方面的目标。Android中的DEX优化主要通过以下几种方式实现：

- **DEX文件合并：** 将多个DEX文件合并成一个，减小DEX文件的数量。这有助于提高应用的启动速度，因为在加载应用时需要加载的DEX文件数量减少。
- **DEX文件压缩：** 对DEX文件进行压缩，减小应用包的大小。这有助于在网络传输和应用安装过程中减少数据传输量
- **DEX文件预处理：** 在应用构建过程中，对DEX文件进行一些预处理，例如去除无用的代码、优化代码结构等。这有助于提高应用的运行时性能。
- **DEX文件编译：** 将Java源代码编译成DEX文件时，进行一些优化操作，例如内联、循环优化等。这有助于生成更有效的DEX代码。
- **分包：** 当应用的方法数超过Dalvik虚拟机的限制时，会采用分包的方式，将多个DEX文件按需加载。这有助于解决应用方法数过多的问题。

DEX优化的目的是提高Android应用的运行性能、减小应用包的体积，并在一些特殊情况下处理方法数限制。这些优化通常是由构建工具、编译器和打包工具自动完成的，而开发者无需手动进行大部分的DEX优化操作。

APK本质是一个Zip压缩包，其中打包了源代码编译出的class.dex、一些图片视屏资源文件和一些Native库文件

![image-20240418133222704](image-20240418133222704.png)

当APK安装时Dalvik将dex文件中可执行文件class.dex解压存储在本地的文件就是ODEX文件。ART运行生成的文件是OAT。 



#### 什么是ODEX / VDEX / OAT

- **ODEX（Optimized Dalvik Executable）**是一种用于优化Android应用的 Dalvik 虚拟机执行文件格式。在Android中，应用的Java源代码首先被编译成DEX文件，而为了提高执行效率，这些DEX文件可以被进一步优化生成对应的ODEX文件。ODEX文件的生成旨在提高应用的启动速度和运行性能。
- **VDEX（Verification DEX**）是Android系统中引入的一种文件格式，用于在应用安装时执行应用程序的验证。VDEX文件通常与ODEX文件一起使用，一起协同工作。VDEX文件记录了DEX文件的散列值等验证相关的信息，以确保应用的完整性。
- **OAT（Optimized Ahead of Time）**是在Android 5.0（Lollipop）及以上版本中引入的新的文件格式，用于替代ODEX文件。OAT文件包含了经过优化的本机代码，它是由ART（Android Runtime）编译器生成的。(虽然生成的名字后缀仍然是ODEX，但已经不是之前的文件格式了)

**ODEX 文件的生成过程：**

**<Android 5.0之前：Dalvik虚拟机>**

Dalvik虚拟机会在执行dex文件前对dex文件做优化，生成可执行文件odex，保存到 `data/dalvik-cache` 目录，最后把Apk文件中的dex文件删除。

ps:此时生成的odex文件后缀依然是dex ，它是一个dex文件，里面仍然是字节码，而不是本地机器码。



**<Android5.0 <= Version < Android 8.0 (Android O)：ART虚拟机>**

Android5.0之后使用ART虚拟机，ART虚拟机使用AOT预编译生成oat文件。oat文件是ART虚拟机运行的文件，是ELF格式二进制文件。oat文件包含dex和编译的本地机器指令，因此比Android5.0之前的odex文件更大。

ps:此时生成的oat文件后缀是odex ，它是一个oat文件，里面仍然是本地机器码，而不是字节码。



**<Android O及之后(>=Android 8.0)：ART虚拟机>**

Android 8.0及之后版本，dex2oat会直接生成两个oat文件 (即`vdex文件` 和 `odex文件`)。其中 odex 文件是从vdex 文件中提取了部分模块生成的一个新的可执行二进制码文件，odex 从vdex 中提取后，vdex 的大小就减少了。

App在首次安装的时候，odex 文件就会生成在 `/system/app/<packagename>/oat/` 下。

在系统运行过程中，虚拟机将其 从`/system/app` 下 copy 到 `/data/dalvik-cache/` 下。

![image-20240418145233369](image-20240418145233369.png)

不论是Dalvik还是ART，生成的优化文件后缀都是odex，只是其中的文件格式有差异。

Dalvik生成的文件里面是字节码，ART生成的文件是经过优化的本机码。



#### 优化模式

在**compiler_filter.h** ，我们可以看到dex2oat一共有9种编译优化模式： 

```c
  enum Filter {
    kAssumeVerified,      // Skip verification but mark all classes as verified anyway.
    kExtract,             // Delay verication to runtime, do not compile anything.
    kVerify,              // Only verify classes.
    kSpaceProfile,        // Maximize space savings based on profile.
    kSpace,               // Maximize space savings.
    kSpeedProfile,        // Maximize runtime performance based on profile.
    kSpeed,               // Maximize runtime performance.
    kEverythingProfile,   // Compile everything capable of being compiled based on profile.
    kEverything,          // Compile everything capable of being compiled.
  };
```

通过目前调研系统性能来看，我们一般涉及到的场景主要有以下这几种编译模式：

- **Verify**：仅验证类，不进行编译；仅需要确保类的正确性而不需要进行编译时使用

  优点：确保类的正确性，避免潜在的运行时错误

  缺点：不进行编译，无法提升运行时性能

- **SpeedProfile** ：根据实际使用情况优化运行时性能，而不是在编译时进行全面优化

  优点：根据实际使用情况优化运行时性能，达到性能和空间的平衡

  缺点：需要分析数据，增加编译复杂性;不能保证所有情况下的最佳性能

- **Speed**：尽可能提高运行时性能而不考虑编译时间和空间消耗时使用

  优点：最大化提高运行时性能，适合对性能要求高的应用

  缺点：可能会增加编译时间和生成的代码大小，增加存储需求



接下来以拼多多应用为例，测试三种不同编译模式的性能差异：

执行效率上：

以拼多多为例测试应用冷启动的时间(adb shell am start -W -n com.xunmeng.pinduoduo/.ui.activity.HomeActivity)：

![image-20240604093054959](image-20240604093054959.png)

| 模式          | 启动时间 | DEX文件大小 |
| ------------- | -------- | ----------- |
| speed         | 846ms    | 83M         |
| speed-profile | 750ms    | 31M         |
| verify        | 939ms    | 20M         |

```
verify < speed-profile < speed
```

优化速度上：

通过shell命令手动触发dex2oat进行编译优化（eg: adb shell cmd package **compile -m speed-profile** -f com.xunmeng.pinduoduo）

| 模式          | 编译时间 |
| ------------- | -------- |
| speed         | 26820ms  |
| speed-profile | 12370ms  |
| verify        | 5820ms   |

```
verify > speed-profile > speed
```



#### 如何开启/关闭编译阶段的ODEX优化

![image-20240507131623886](image-20240507131623886.png)

针对bp和mk两种文件，有以下不同的方式进行开启关闭。只要胆子大，你甚至可以改变编译时的优化类型

**Android.bp**

```makefile
android_app {
    name: "xxxxx",
    
+    dex_preopt: {
+        enabled: true,
+		 compiler_filter: "speed",
+    },

}
```

**Android.mk**

```makefile
LOCAL_MODULE := xxxxx

+LOCAL_DEX_PREOPT := true
+LOCAL_DEX_PREOPT_FLAGS := --compiler-filter=speed
```

关闭后在编译时不会生成对应的OAT优化文件，编译的image会变小。

这个优化的过程会在转变到首次开机中进行，在PackageManagerServices安装应用时采取优化，开机时间会变长。属于用空间换取时间的做法。



#### 如何判断应用是否做了ODEX优化

1：最简单的方式，在生成APK的对应目录查看有无相应的oat文件夹（odex/vdex文件保存在内），表示在编译阶段做过了dex2oat优化

![image-20240418150522927](image-20240418150522927.png)

2：可以在 `data/dalvik-cache` 目录下看到对应的dex文件：

arm:

![image-20240125155958484](image-20240125155958484.png)

arm64:

![image-20240125160030643](image-20240125160030643.png)

当然，你也可以在应用对应目录的oat下可以看到生成的dex文件

![image-20240125162040791](image-20240125162040791.png)

3：为什么有些应用安装时间会比较长呢？

原因之一是安装过程进行的DEX优化，通常来说odex+vdex文件越大，说明dex2oat优化的类越多越彻底，性能也相对较好，优化时间也相对较长。
像youtube、wechat等apk，本身应用较大且code复杂度高，往往会出现安装失败，安装慢等问题。安装失败是由于dex2oat进程编译时间过久打到了timeout，安装慢当然就是dex2oat做的compiler久的原因。

Apk安装时间过长可以通过调整--compiler-filter，加快安装（不展开细讲，可以参考MTK Online FAQ20644）



#### Dex2oat

通过dex2oat优化后，可以将APK的dex文件字节码转换成效率更高的oat机器码，运行阶段会更加快速流畅。

以下是Dex2oat的主要触发场景:

![image-20240419170051895](image-20240419170051895.png)

那么主要的触发的方式有以下几种：

| 触发场景 | 触发方式                                                     | 优化方式      | 对应属性值               |
| -------- | ------------------------------------------------------------ | ------------- | ------------------------ |
| OTA升级  | installd触发                                                 | verify        | pm.dexopt.boot-after-ota |
| 系统启动 | installd触发                                                 | verify        | pm.dexopt.first-boot     |
| 应用安装 | installd触发                                                 | speed-profile | pm.dexopt.install        |
| 系统空闲 | 同时满足充电、Device idle状态下触发                          | verify        | pm.dexopt.inactive       |
| 手动触发 | adb shell cmd package compile -m speed-profile -f com.xunmeng.pinduoduo | 自定义参数    | pm.dexopt.cmdline        |

在手机上执行`getprop | grep pm`，查看系统默认采用了哪些优化模式

![image-20240419144014767](image-20240419144014767.png)

安装拼多多应用时，logcat中dex2oat相关的log

```fortran
04-25 13:30:25.961   953  2197 V installd: Running /apex/com.android.art/bin/dex2oat32 in=base.apk out=/data/app/~~YYcYRu9m__EBpQioxwaUFQ==/com.xunmeng.pinduoduo-4Y47H8bBuVOYwEdFFcdp3w==/oat/arm64/base.odex

04-25 13:30:26.019  9864  9864 I dex2oat32: /apex/com.android.art/bin/dex2oat32 --input-vdex-fd=-1 --output-vdex-fd=9 --classpath-dir=/data/app/~~YYcYRu9m__EBpQioxwaUFQ==/com.xunmeng.pinduoduo-4Y47H8bBuVOYwEdFFcdp3w== --class-loader-context=PCL[]{PCL[/system/framework/android.test.base.jar]#PCL[/system/framework/org.apache.http.legacy.jar]} --compact-dex-level=none --compiler-filter=speed-profile --compilation-reason=install --max-image-block-size=524288 --resolve-startup-const-strings=true --generate-mini-debug-info

--classpath-dir=/data/app/~~YYcYRu9m__EBpQioxwaUFQ==/com.xunmeng.pinduoduo-4Y47H8bBuVOYwEdFFcdp3w==		//文件路径
--compiler-filter=speed-profile		//编译模式
--compilation-reason=install	//触发场景
```

系统空闲触发：

speed-profile会在安装的时候采用interperter-only，然后，运行一段时间之后，会将那些常用的方法优化成为speed模式。也就是说是有选择性的优化。



#### Dex2oat 流程分析

本次分析基于Android T 代码。上述触发场景主要涉及PackageManagerService , 所以从该服务作为入口，分析dex2oat的相关流程。
主要涉及到OTA升级、系统启动等场景
在系统开机过程中，首先会在SystemServer中执行updatePackagesIfNeeded，在pkms中执行后通过mDexOptHelper进一步执行performPackageDexOptUpgradeIfNeeded操作

```java
frameworks/base/services/java/com/android/server/SystemServer.java

if (!mOnlyCore) {
            t.traceBegin("UpdatePackagesIfNeeded");
            try {
                Watchdog.getInstance().pauseWatchingCurrentThread("dexopt");
                mPackageManagerService.updatePackagesIfNeeded();
            } catch (Throwable e) {
                reportWtf("update packages", e);
            } finally {
                Watchdog.getInstance().resumeWatchingCurrentThread("dexopt");
            }
            t.traceEnd();
        }
```

```java
frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java

public void updatePackagesIfNeeded() {
        mDexOptHelper.performPackageDexOptUpgradeIfNeeded();
    }
```

在DexOptHelper中，首先会检查systemui，作为系统起来之后的高优先级应用，对用户体验很重要

随后causeUpgrade / causeFirstBoot分别判断是否为ota升级后的启动以及第一次启动，如果都不是，则进行return，不需要进行dex2oat。

是的话则获取当前所有的pkgs，并将参数一并传到performDexOptUpgrade去执行

```java
frameworks/base/services/core/java/com/android/server/pm/DexOptHelper.java

@RequiresPermission(Manifest.permission.READ_DEVICE_CONFIG)
    public void performPackageDexOptUpgradeIfNeeded() {
        PackageManagerServiceUtils.enforceSystemOrRoot(
                "Only the system can request package update");

        // The default is "true".
        if (!"false".equals(DeviceConfig.getProperty("runtime", "dexopt_system_ui_on_boot"))) {
            // System UI is important to user experience, so we check it after a mainline update or
            // an OTA. It may need to be re-compiled in these cases.
            if (hasBcpApexesChanged() || mPm.isDeviceUpgrading()) {
                checkAndDexOptSystemUi();
            }
        }

        // We need to re-extract after an OTA.
        boolean causeUpgrade = mPm.isDeviceUpgrading();

        // First boot or factory reset.
        // Note: we also handle devices that are upgrading to N right now as if it is their
        //       first boot, as they do not have profile data.
        boolean causeFirstBoot = mPm.isFirstBoot() || mPm.isPreNUpgrade();

        if (!causeUpgrade && !causeFirstBoot) {
            return;
        }

       ......

        List<AndroidPackage> pkgs = new ArrayList<>(pkgSettings.size());
        for (int index = 0; index < pkgSettings.size(); index++) {
            pkgs.add(pkgSettings.get(index).getPkg());
        }

        final long startTime = System.nanoTime();
        final int[] stats = performDexOptUpgrade(pkgs, mPm.isPreNUpgrade() /* showDialog */,
                causeFirstBoot ? REASON_FIRST_BOOT : REASON_BOOT_AFTER_OTA,
                false /* bootComplete */);

        .......
    }
```

接着，在performDexOptUpgrade中继续进行操作。

performDexOptUpgrade会返回一组应用优化的数据，通过名字大概可以看出表示对应的状态。在这个方法中，会循环读取之前获取的pkgs,分别对每个应用进行performDexOptTraced，将包名等参数传入，通过返回的结果增加对应的优化状态数据。

```java
frameworks/base/services/core/java/com/android/server/pm/DexOptHelper.java

public int[] performDexOptUpgrade(List<AndroidPackage> pkgs, boolean showDialog,
            final int compilationReason, boolean bootComplete) {
            
	int numberOfPackagesVisited = 0;
	int numberOfPackagesOptimized = 0;
	int numberOfPackagesSkipped = 0;
	int numberOfPackagesFailed = 0;
    
	for (AndroidPackage pkg : pkgs) {
            numberOfPackagesVisited++;
            ...
            if (!mPm.mPackageDexOptimizer.canOptimizePackage(pkg)) {
                if (DEBUG_DEXOPT) {
                    Log.i(TAG, "Skipping update of non-optimizable app " + pkg.getPackageName());
                }
                numberOfPackagesSkipped++;
                continue;
            }
            ...
            int primaryDexOptStatus = performDexOptTraced(new DexoptOptions(
                    pkg.getPackageName(),
                    pkgCompilationReason,
                    dexoptFlags));
            switch (primaryDexOptStatus) {
                case PackageDexOptimizer.DEX_OPT_PERFORMED:
                    numberOfPackagesOptimized++;
                    break;
                case PackageDexOptimizer.DEX_OPT_SKIPPED:
                    numberOfPackagesSkipped++;
                    break;
                case PackageDexOptimizer.DEX_OPT_CANCELLED:
                    // ignore this case
                    break;
                case PackageDexOptimizer.DEX_OPT_FAILED:
                    numberOfPackagesFailed++;
                    break;
                default:
                    Log.e(TAG, "Unexpected dexopt return code " + primaryDexOptStatus);
                    break;
            }
    }

    android.util.Log.d("SecondaryDex","do dex down ");
    return new int[]{numberOfPackagesOptimized, numberOfPackagesSkipped,
                     numberOfPackagesFailed};
}
```

后续通过层层调用，并在其中做了一些空包的校验，一步一步调用到PackageDexOptimizer.java的performDexOpt方法中

随后通过校验canOptimizePackage，继续调用performDexOptLI

```java
    int performDexOpt(AndroidPackage pkg, @NonNull PackageStateInternal pkgSetting,
            String[] instructionSets, CompilerStats.PackageStats packageStats,
            PackageDexUsage.PackageUseInfo packageUseInfo, DexoptOptions options) {
        if (PLATFORM_PACKAGE_NAME.equals(pkg.getPackageName())) {
            throw new IllegalArgumentException("System server dexopting should be done via "
                    + " DexManager and PackageDexOptimizer#dexoptSystemServerPath");
        }
        if (pkg.getUid() == -1) {
            throw new IllegalArgumentException("Dexopt for " + pkg.getPackageName()
                    + " has invalid uid.");
        }
        if (!canOptimizePackage(pkg)) {
            return DEX_OPT_SKIPPED;
        }
        synchronized (mInstallLock) {
            final long acquireTime = acquireWakeLockLI(pkg.getUid());
            try {
                //[238596]The first bootup time is too long
                String dexPort = SystemProperties.get(MDEXPROP,"0");
                if("0".equals(dexPort) && isWhiteAppWithDex(pkg.getPackageName())){
                    android.util.Log.d("SecondaryDex","dex skipp: ");
                    return DEX_OPT_SKIPPED;
                }else{
                    return performDexOptLI(pkg, pkgSetting, instructionSets,
                        packageStats, packageUseInfo, options);
                }
                //[238596]The first bootup time is too long
            } finally {
                releaseWakeLockLI(acquireTime);
            }
        }
    }
```

到了performDexOptLI此方法，已经把需要dex的AndroidPackage传了过来，并且在这一步会获取对应的编译模式getRealCompilerFilter(pkg, options.getCompilerFilter())以及相关配置文件，随后将这些作为参数传入dexOptPath

```java
 int newResult = dexOptPath(pkg, pkgSetting, path, dexCodeIsa, compilerFilter,
                            profileAnalysisResult, classLoaderContexts[i], dexoptFlags, sharedGid,
                            packageStats, options.isDowngrade(), profileName, dexMetadataPath,
                            options.getCompilationReason());
```

在dexOptPath中，可以看到存放otaDir文件存放的路径，并且在这个部分会计算开始结束时间，也就表示DEX优化的操作就在这之间：

```java
            if (packageStats != null) {
                long endTime = System.currentTimeMillis();
                packageStats.setCompileTime(path, (int)(endTime - startTime));
                //@datalogic-begin [JAZZ_192285]
                spentDexCompileTime += (endTime - startTime);
                Log.d("liziluo","[dex2oat compiling time]: "+ pkg.getPackageName() + ":[" + (endTime - startTime)
                        + " ms] , total:[" + spentDexCompileTime + " ms]");
                //@datalogic-end [JAZZ_192285]
            }
```

getInstallerLI().dexopt,后续会调用到IInstalld的dexopt，通过aidl去调用native层的实现。

```java
String oatDir = getPackageOatDirIfSupported(pkg,
                pkgSetting.getTransientState().isUpdatedSystemApp());

try {
            long startTime = System.currentTimeMillis();

            // TODO: Consider adding 2 different APIs for primary and secondary dexopt.
            // installd only uses downgrade flag for secondary dex files and ignores it for
            // primary dex files.
            String seInfo = AndroidPackageUtils.getSeInfo(pkg, pkgSetting);
            boolean completed = getInstallerLI().dexopt(path, uid, pkg.getPackageName(), isa,
                    dexoptNeeded, oatDir, dexoptFlags, compilerFilter, pkg.getVolumeUuid(),
                    classLoaderContext, seInfo, /* downgrade= */ false ,
                    pkg.getTargetSdkVersion(), profileName, dexMetadataPath,
                    getAugmentedReasonName(compilationReason, dexMetadataPath != null));
            if (!completed) {
                return DEX_OPT_CANCELLED;
            }
            if (packageStats != null) {
                long endTime = System.currentTimeMillis();
                packageStats.setCompileTime(path, (int)(endTime - startTime));
                //[238596]The first bootup time is too long
                android.util.Log.d("SecondaryDex","dex CompileTime: " + pkg.getPackageName() + "  " + (endTime - startTime));
            }
            if (oatDir != null) {
                // Release odex/vdex compressed blocks to save user space.
                // Compression support will be checked in F2fsUtils.
                // The system app may be dexed, oatDir may be null, skip this situation.
                final ContentResolver resolver = mContext.getContentResolver();
                F2fsUtils.releaseCompressedBlocks(resolver, new File(oatDir));
            }
            return DEX_OPT_PERFORMED;
        } catch (InstallerException e) {
            Slog.w(TAG, "Failed to dexopt", e);
            return DEX_OPT_FAILED;
        }
```



**BackgroundDexOptService**

BackgroundDexOptService 作为Android 系统中的一个服务，其作用是负责在后台进行dex优化（Controls background dex optimization run as idle job or command line.）
触发场景为系统闲置时，一般在设备进入IDLE状态，且为充电状态会激活BackgroundDexOptService Job



整体流程图：

![image-20240523172219751](image-20240523172219751.png) 

**PKMS** **DEX2OAT**触发流程：

```
startOtherServices
updatePackagesIfNeeded
performPackageDexOptUpgradeIfNeeded
checkAndDexOptSystemUi	performDexOptUpgrade
performDexOptTraced
performDexOptInternal
performDexOptInternalWithDependenciesLI
performDexOpt
performDexOptLI   
dexOptPath
getInstallerLI().dexopt
```

**BackgroundDexOptService**触发流程

```
runBackgroundDexoptJob
runIdleOptimization
idleOptimizePackages
optimizePackages
optimizePackage
performDexOptPrimary   /   performDexOptSecondary
mDexOptHelper.performDexOptWithStatus	/	mDexOptHelper.performDexOpt
performDexOptTraced
performDexOptInternal
performDexOptInternalWithDependenciesLI
performDexOpt		//应用白名单在这一步
performDexOptLI   
dexOptPath			//编译参数获取在这一步
getInstallerLI().dexopt
```



![image-20240607160949738](image-20240607160949738.png)

![image-20240419143650822](image-20240419143650822.png)

目前开机后调用dex，会在优化过程中突然重启framwork

已发现问题原因：在主线程做dex耗时太长，一直持有锁导致被watchdog 检测到，随后杀死了system server，重启

```
01-19 06:34:03.387  1038  1066 W Watchdog: *** WATCHDOG KILLING SYSTEM PROCESS: Blocked in handler on main thread (main)
01-19 06:34:03.392  1038  1066 W Watchdog: main annotated stack trace:
01-19 06:34:03.392  1038  1066 W Watchdog:     at android.os.BinderProxy.transactNative(Native Method)
01-19 06:34:03.393  1038  1066 W Watchdog:     at android.os.BinderProxy.transact(BinderProxy.java:584)
01-19 06:34:03.393  1038  1066 W Watchdog:     at android.os.IInstalld$Stub$Proxy.dexopt(IInstalld.java:1573)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.pm.Installer.dexopt(Installer.java:623)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.pm.PackageDexOptimizer.dexOptPath(PackageDexOptimizer.java:501)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.pm.PackageDexOptimizer.performDexOptLI(PackageDexOptimizer.java:375)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.pm.PackageDexOptimizer.performDexOpt(PackageDexOptimizer.java:234)
01-19 06:34:03.393  1038  1066 W Watchdog:     - locked <0x0a7f80d7> (a java.lang.Object)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.pm.DexOptHelper.performDexOptInternalWithDependenciesLI(DexOptHelper.java:523)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.pm.DexOptHelper.performDexOptInternal(DexOptHelper.java:468)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.pm.DexOptHelper.performDexOptTraced(DexOptHelper.java:445)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.pm.DexOptHelper.performDexOptUpgrade(DexOptHelper.java:264)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.pm.DexOptHelper.performPackageDexOptUpgradeIfNeeded(DexOptHelper.java:384)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.pm.PackageManagerService.updatePackagesIfNeeded(PackageManagerService.java:2931)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.pm.PackageManagerService.tryReloadDex(PackageManagerService.java:4075)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.pm.PackageManagerService$4.onReceive(PackageManagerService.java:4141)
01-19 06:34:03.393  1038  1066 W Watchdog:     at android.app.LoadedApk$ReceiverDispatcher$Args.lambda$getRunnable$0$android-app-LoadedApk$ReceiverDispatcher$Args(LoadedApk.java:1863)
01-19 06:34:03.393  1038  1066 W Watchdog:     at android.app.LoadedApk$ReceiverDispatcher$Args$$ExternalSyntheticLambda0.run(Unknown Source:2)
01-19 06:34:03.393  1038  1066 W Watchdog:     at android.os.Handler.handleCallback(Handler.java:942)
01-19 06:34:03.393  1038  1066 W Watchdog:     at android.os.Handler.dispatchMessage(Handler.java:99)
01-19 06:34:03.393  1038  1066 W Watchdog:     at android.os.Looper.loopOnce(Looper.java:201)
01-19 06:34:03.393  1038  1066 W Watchdog:     at android.os.Looper.loop(Looper.java:288)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.SystemServer.run(SystemServer.java:981)
01-19 06:34:03.393  1038  1066 W Watchdog:     at com.android.server.SystemServer.main(SystemServer.java:657)
01-19 06:34:03.394  1038  1066 W Watchdog:     at java.lang.reflect.Method.invoke(Native Method)
01-19 06:34:03.394  1038  1066 W Watchdog:     at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:569)
01-19 06:34:03.394  1038  1066 W Watchdog:     at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:997)
01-19 06:34:03.394  1038  1066 W Watchdog: *** GOODBYE!
```



```
664:04-01 13:17:21.506499  1395  1395 I Watchdog: Pausing HandlerChecker: main thread for reason: packagemanagermain. Pause count: 1
730:04-01 13:17:21.941803   511   858 I keystore2: keystore2::watchdog: Watchdog thread idle -> terminating. Have a great day.
1133:04-01 13:17:27.044170  1395  1395 I Watchdog: Resuming HandlerChecker: main thread for reason: packagemanagermain. Pause count: 0
1136:04-01 13:17:27.052107  1395  1395 I Watchdog: Pausing HandlerChecker: main thread for reason: moveab. Pause count: 1
1138:04-01 13:17:27.054229  1395  1395 I Watchdog: Resuming HandlerChecker: main thread for reason: moveab. Pause count: 0
1148:04-01 13:17:27.083183  1395  1395 D SystemServerTiming: InitWatchdog
1184:04-01 13:17:27.554549  1395  1395 I PackageWatchdog: Syncing state, reason: added new observer
1185:04-01 13:17:27.554855  1395  1395 I PackageWatchdog: Not pruning observers, elapsed time: 0ms
1186:04-01 13:17:27.555116  1395  1428 I PackageWatchdog: Saving observer state to file
1226:04-01 13:17:27.874615  1395  1395 D SystemServerTiming: UpdateWatchdogTimeout
1227:04-01 13:17:27.875291  1395  1395 I Watchdog: Watchdog timeout updated to 60000 millis
1393:04-01 13:17:28.283066  1395  1395 I Watchdog: Pausing HandlerChecker: main thread for reason: dexopt. Pause count: 1
1394:04-01 13:17:28.305708  1395  1395 I Watchdog: Resuming HandlerChecker: main thread for reason: dexopt. Pause count: 0
2988:04-01 13:17:42.230618  1395  1395 I PackageWatchdog: Syncing state, reason: health check state enabled
2989:04-01 13:17:42.230842  1395  1395 I PackageWatchdog: Discarding observer rollback-observer. All packages expired
2990:04-01 13:17:42.231171  1395  1428 I PackageWatchdog: Saving observer state to file
3614:04-01 13:17:43.482227  1395  1430 I Watchdog: Interesting Java process com.android.phone started. Pid 1895
3843:04-01 13:17:44.168657  1395  1395 I PackageWatchdog: Syncing health check requests for packages: {}
3927:04-01 13:17:44.574789  1395  1395 I PackageWatchdog: Syncing health check requests for packages: {}
3938:04-01 13:17:44.579717  1395  1410 D PackageWatchdog: Received supported packages [PackageConfig{com.google.android.networkstack, 86400000}]
4064:04-01 13:17:46.473058  1395  1428 I PackageWatchdog: Syncing state, reason: observing new packages
4066:04-01 13:17:46.473171  1395  1428 D PackageWatchdog: rollback-observer started monitoring health of packages [com.google.android.tzdata4]
4067:04-01 13:17:46.473240  1395  1395 I PackageWatchdog: Syncing health check requests for packages: {com.google.android.tzdata4}
4071:04-01 13:17:46.474572  1395  1428 I PackageWatchdog: Syncing state, reason: updated observers
4072:04-01 13:17:46.474730  1395  1428 I PackageWatchdog: Saving observer state to file
4076:04-01 13:17:46.486420  1395  1428 I PackageWatchdog: Syncing state, reason: observing new packages
4078:04-01 13:17:46.486634  1395  1428 D PackageWatchdog: rollback-observer added the following packages to monitor [com.google.android.os.statsd, com.google.mainline.telemetry]
4079:04-01 13:17:46.486757  1395  1428 I PackageWatchdog: Syncing state, reason: updated observers
4080:04-01 13:17:46.486824  1395  1428 I PackageWatchdog: Not pruning observers, elapsed time: 0ms
4081:04-01 13:17:46.486947  1395  1428 I PackageWatchdog: Saving observer state to file
4086:04-01 13:17:46.493367  1395  1395 I PackageWatchdog: Syncing health check requests for packages: {com.google.android.tzdata4, com.google.android.os.statsd, com.google.mainline.telemetry}
4095:04-01 13:17:46.495879  1395  1428 I PackageWatchdog: Syncing state, reason: observing new packages

```



```
528:04-01 11:20:48.956672   510   525 I keystore2: keystore2::watchdog: Watchdog thread idle -> terminating. Have a great day.
583:04-01 11:20:49.413416  1168  1168 I Watchdog: Pausing HandlerChecker: main thread for reason: packagemanagermain. Pause count: 1
1004:04-01 11:20:51.743543  1168  1168 I Watchdog: Resuming HandlerChecker: main thread for reason: packagemanagermain. Pause count: 0
1007:04-01 11:20:51.749406  1168  1168 I Watchdog: Pausing HandlerChecker: main thread for reason: moveab. Pause count: 1
1009:04-01 11:20:51.750460  1168  1168 I Watchdog: Resuming HandlerChecker: main thread for reason: moveab. Pause count: 0
1018:04-01 11:20:51.783745  1168  1168 D SystemServerTiming: InitWatchdog
1053:04-01 11:20:52.328704  1168  1168 I PackageWatchdog: Syncing state, reason: added new observer
1054:04-01 11:20:52.328900  1168  1168 I PackageWatchdog: Not pruning observers, elapsed time: 0ms
1055:04-01 11:20:52.329090  1168  1198 I PackageWatchdog: Saving observer state to file
1094:04-01 11:20:52.525016  1168  1168 D SystemServerTiming: UpdateWatchdogTimeout
1095:04-01 11:20:52.525478  1168  1168 I Watchdog: Watchdog timeout updated to 60000 millis
1262:04-01 11:20:52.872285  1168  1168 I Watchdog: Pausing HandlerChecker: main thread for reason: dexopt. Pause count: 1
1263:04-01 11:20:52.875789  1168  1168 I Watchdog: Resuming HandlerChecker: main thread for reason: dexopt. Pause count: 0
2529:04-01 11:20:56.243241  1168  1168 I PackageWatchdog: Syncing state, reason: health check state enabled
2530:04-01 11:20:56.243501  1168  1168 I PackageWatchdog: Discarding observer rollback-observer. All packages expired
2533:04-01 11:20:56.244043  1168  1198 I PackageWatchdog: Saving observer state to file
3173:04-01 11:20:56.920947  1168  1200 I Watchdog: Interesting Java process com.android.phone started. Pid 1543
3332:04-01 11:20:57.092519  1168  1168 I PackageWatchdog: Syncing health check requests for packages: {}
3456:04-01 11:20:57.762024  1168  1168 I PackageWatchdog: Syncing health check requests for packages: {}
3466:04-01 11:20:57.768697  1168  1606 D PackageWatchdog: Received supported packages [PackageConfig{com.google.android.networkstack, 86400000}]
4052:04-01 11:21:00.941339  1168  1200 I Watchdog: Interesting Java process com.google.android.providers.media.module started. Pid 1917
```

客户应用DEX：

```
system@priv-app@DLBatteryManager@DLBatteryManager.apk@classes.dex
system@priv-app@DLBatteryManager@DLBatteryManager.apk@classes.vdex
system@priv-app@DLService@DLService.apk@classes.dex
system@priv-app@DLService@DLService.apk@classes.vdex
system@priv-app@DLSettings@DLSettings.apk@classes.dex
system@priv-app@DLSettings@DLSettings.apk@classes.vdex
system@priv-app@DLSystemUpdate@DLSystemUpdate.apk@classes.dex
system@priv-app@DLSystemUpdate@DLSystemUpdate.apk@classes.vdex
system@priv-app@DatalogicProvider@DatalogicProvider.apk@classes.dex
system@priv-app@DatalogicProvider@DatalogicProvider.apk@classes.vdex
system@priv-app@datalogic-resources@datalogic-resources.apk@classes.dex
system@priv-app@datalogic-resources@datalogic-resources.apk@classes.vdex
system@priv-app@datalogic-services@datalogic-services.apk@classes.dex
system@priv-app@datalogic-services@datalogic-services.apk@classes.vdex
```



```
06-06 07:53:06.059  1151  1151 D PackageDexOptimizer: dex CompileTime---com.android.systemui:12925ms  all compileTime:12925ms
06-06 07:53:07.864  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.service:1717ms  all compileTime:14642ms
06-06 07:53:19.941  1151  1151 D PackageDexOptimizer: dex CompileTime---com.android.settings:12028ms  all compileTime:26670ms
06-06 07:53:20.322  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.provider:356ms  all compileTime:27026ms
06-06 07:53:20.876  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.systemupdate:505ms  all compileTime:27531ms
06-06 07:53:21.233  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.resources:313ms  all compileTime:27844ms
06-06 07:53:21.546  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.dlhomescreen:309ms  all compileTime:28153ms
06-06 07:53:34.944  1151  1151 D PackageDexOptimizer: dex CompileTime---com.android.launcher3:13381ms  all compileTime:41534ms
06-06 07:53:35.311  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.shakingscanner:349ms  all compileTime:41883ms
06-06 07:53:42.540  1151  1151 D PackageDexOptimizer: dex CompileTime---com.google.android.setupwizard:7224ms  all compileTime:49107ms
06-06 07:53:45.061  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.scan2deploy:2509ms  all compileTime:51616ms
06-06 07:53:48.861  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.ptt.ext.zello:3795ms  all compileTime:55411ms
06-06 07:53:50.755  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.softspot:1890ms  all compileTime:57301ms
06-06 07:53:51.990  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.dlsettings:1193ms  all compileTime:58494ms
06-06 07:56:14.400  1151  1151 D PackageDexOptimizer: dex CompileTime---com.google.android.gms:142401ms  all compileTime:200895ms
06-06 07:58:34.490  1151  1151 D PackageDexOptimizer: dex CompileTime---com.google.android.gms:140085ms  all compileTime:340980ms
06-06 07:58:35.209  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.devicepolicymanager:677ms  all compileTime:341657ms
06-06 07:58:35.920  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.scan:683ms  all compileTime:342340ms
06-06 07:58:36.903  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.setupwizardscanner:964ms  all compileTime:343304ms
06-06 07:58:37.613  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.factory:704ms  all compileTime:344008ms
06-06 07:58:38.336  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.packageinstaller:691ms  all compileTime:344699ms
06-06 07:58:39.751  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.battery:1379ms  all compileTime:346078ms
06-06 07:58:40.162  1151  1151 D PackageDexOptimizer: dex CompileTime---com.datalogic.enterpriseupdater:405ms  all compileTime:346483ms
06-06 08:04:41.530  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.ext.services:1970ms  all compileTime:348453ms
06-06 08:04:42.631  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.providers.telephony:1027ms  all compileTime:349480ms
06-06 08:04:43.222  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.telephony:529ms  all compileTime:350009ms
06-06 08:04:43.769  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.ext.shared:482ms  all compileTime:350491ms
06-06 08:04:44.580  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.ons:502ms  all compileTime:350993ms
06-06 08:04:45.873  1151  5315 D PackageDexOptimizer: dex CompileTime---com.debug.loggerui:1239ms  all compileTime:352232ms
06-06 08:04:52.672  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.permissioncontroller:6737ms  all compileTime:358969ms
06-06 08:04:53.637  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.providers.settings:900ms  all compileTime:359869ms
06-06 08:04:55.528  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.networkstack:1690ms  all compileTime:361559ms
06-06 08:04:57.385  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.server.telecom:1794ms  all compileTime:363353ms
06-06 08:05:05.853  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.dialer:8389ms  all compileTime:371742ms
06-06 08:05:06.521  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.capctrl.service:482ms  all compileTime:372224ms
06-06 08:05:10.982  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.documentsui:4398ms  all compileTime:376622ms
06-06 08:05:12.159  1151  5315 D PackageDexOptimizer: dex CompileTime---com.datalogic.server:1116ms  all compileTime:377738ms
06-06 08:05:17.535  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.phone:5265ms  all compileTime:383003ms
06-06 08:05:18.440  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.shell:843ms  all compileTime:383846ms
06-06 08:05:20.969  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.providers.contacts:2335ms  all compileTime:386181ms
06-06 08:05:53.361  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.inputmethod.latin:32290ms  all compileTime:418471ms
06-06 08:05:54.879  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.providers.calendar:1455ms  all compileTime:419926ms
06-06 08:06:00.711  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.providers.media.module:5769ms  all compileTime:425695ms
06-06 08:06:05.587  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.managedprovisioning:4812ms  all compileTime:430507ms
06-06 08:06:07.055  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.networkstack.tethering:1403ms  all compileTime:431910ms
06-06 08:06:07.695  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.cellbroadcastservice:578ms  all compileTime:432488ms
06-06 08:06:08.484  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.location.lppe.main:724ms  all compileTime:433212ms
06-06 08:06:09.475  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.providers.downloads:927ms  all compileTime:434139ms
06-06 08:06:11.178  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.mtp:1645ms  all compileTime:435784ms
06-06 08:06:15.997  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.webview:4750ms  all compileTime:440534ms
06-06 08:06:20.558  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.webview:4557ms  all compileTime:445091ms
06-06 08:06:32.728  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.providers.blockednumber:800ms  all compileTime:445891ms
06-06 08:06:33.256  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.providers.userdictionary:462ms  all compileTime:446353ms
06-06 08:08:05.593  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.youtube:92153ms  all compileTime:538506ms
06-06 08:08:06.259  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.dynsystem:580ms  all compileTime:539086ms
06-06 08:12:24.456  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.googlequicksearchbox:257985ms  all compileTime:797071ms
06-06 08:16:35.986  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.googlequicksearchbox:251521ms  all compileTime:1048592ms
06-06 08:16:40.757  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.camera:4703ms  all compileTime:1053295ms
06-06 08:16:42.843  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.providers.media:2029ms  all compileTime:1055324ms
06-06 08:16:43.638  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.onetimeinitializer:627ms  all compileTime:1055951ms
06-06 08:16:44.423  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.externalstorage:592ms  all compileTime:1056543ms
06-06 08:16:45.148  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.simprocessor:605ms  all compileTime:1057148ms
06-06 08:16:47.242  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.companiondevicemanager:1977ms  all compileTime:1059125ms
06-06 08:16:55.398  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.engineermode:8036ms  all compileTime:1067161ms
06-06 08:16:56.451  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.omacp:918ms  all compileTime:1068079ms
06-06 08:17:08.111  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.configupdater:11599ms  all compileTime:1079678ms
06-06 08:17:08.891  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.soundrecorder:714ms  all compileTime:1080392ms
06-06 08:18:37.399  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.vending:88332ms  all compileTime:1168724ms
06-06 08:18:38.185  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.simappdialog:674ms  all compileTime:1169398ms
06-06 08:18:45.233  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.adservices.api:6978ms  all compileTime:1176376ms
06-06 08:18:45.956  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.certinstaller:659ms  all compileTime:1177035ms
06-06 08:18:57.810  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.marvin.talkback:11733ms  all compileTime:1188768ms
06-06 08:18:59.323  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.wifi.dialog:1445ms  all compileTime:1190213ms
06-06 08:19:02.137  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.emcamera:2683ms  all compileTime:1192896ms
06-06 08:19:02.771  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.sdksandbox:489ms  all compileTime:1193385ms
06-06 08:19:12.329  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.egg:9497ms  all compileTime:1202882ms
06-06 08:19:26.697  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.nfc:14296ms  all compileTime:1217178ms
06-06 08:19:40.497  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.deskclock:13564ms  all compileTime:1230742ms
06-06 08:19:52.624  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.as:12044ms  all compileTime:1242786ms
06-06 08:21:55.011  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.gm:122272ms  all compileTime:1365058ms
06-06 08:22:56.082  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.apps.tachyon:60945ms  all compileTime:1426003ms
06-06 08:22:57.002  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.batterywarning:514ms  all compileTime:1426517ms
06-06 08:22:58.377  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.printspooler:1315ms  all compileTime:1427832ms
06-06 08:23:05.317  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.as.oss:6735ms  all compileTime:1434567ms
06-06 08:23:06.243  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.se:725ms  all compileTime:1435292ms
06-06 08:23:24.673  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.apps.wellbeing:18335ms  all compileTime:1453627ms
06-06 08:23:25.473  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.captiveportallogin:666ms  all compileTime:1454293ms
06-06 08:23:26.073  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.duraspeed:536ms  all compileTime:1454829ms
06-06 08:24:11.623  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.apps.docs:45392ms  all compileTime:1500221ms
06-06 08:26:29.533  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.apps.maps:137712ms  all compileTime:1637933ms
06-06 08:26:31.227  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.cellbroadcastreceiver:1557ms  all compileTime:1639490ms
06-06 08:27:01.607  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.contacts:30279ms  all compileTime:1669769ms
06-06 08:27:08.045  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.calculator:6300ms  all compileTime:1676069ms
06-06 08:27:39.129  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.chrome:31002ms  all compileTime:1707071ms
06-06 08:28:09.422  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.chrome:30284ms  all compileTime:1737355ms
06-06 08:28:11.594  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.packageinstaller:2110ms  all compileTime:1739465ms
06-06 08:28:15.030  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.gsf:3302ms  all compileTime:1742767ms
06-06 08:28:27.751  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.ims:12635ms  all compileTime:1755402ms
06-06 08:28:28.777  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.tag:963ms  all compileTime:1756365ms
06-06 08:28:41.995  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.tts:13137ms  all compileTime:1769502ms
06-06 08:28:43.758  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.partnersetup:1591ms  all compileTime:1771093ms
06-06 08:28:44.475  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.localtransport:600ms  all compileTime:1771693ms
06-06 08:29:21.246  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.videos:36683ms  all compileTime:1808376ms
06-06 08:29:24.907  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.nearby.halfsheet:3587ms  all compileTime:1811963ms
06-06 08:29:26.036  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.feedback:864ms  all compileTime:1812827ms
06-06 08:29:26.664  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.printservice.recommendation:570ms  all compileTime:1813397ms
06-06 08:30:53.439  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.apps.photos:86661ms  all compileTime:1900058ms
06-06 08:31:31.121  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.calendar:37574ms  all compileTime:1937632ms
06-06 08:31:33.956  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.atci.service:2778ms  all compileTime:1940410ms
06-06 08:31:35.752  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.soundpicker:1737ms  all compileTime:1942147ms
06-06 08:31:37.173  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.voicecommand:1230ms  all compileTime:1943377ms
06-06 08:31:38.403  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.voicecommand:1227ms  all compileTime:1944604ms
06-06 08:31:42.677  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.wallpaper.livepicker:4083ms  all compileTime:1948687ms
06-06 08:31:46.187  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.imsserviceentitlement:3434ms  all compileTime:1952121ms
06-06 08:31:51.542  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.storagemanager:5285ms  all compileTime:1957406ms
06-06 08:31:57.899  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.apps.turbo:6024ms  all compileTime:1963430ms
06-06 08:31:59.149  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.remoteprovisioner:1127ms  all compileTime:1964557ms
06-06 08:32:25.085  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.wallpaper:25855ms  all compileTime:1990412ms
06-06 08:32:49.649  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.keep:24426ms  all compileTime:2014838ms
06-06 08:32:55.103  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.emergency:5187ms  all compileTime:2020025ms
06-06 08:32:55.826  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.hotspot2.osulogin:659ms  all compileTime:2020684ms
06-06 08:32:57.714  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.voiceunlock:1825ms  all compileTime:2022509ms
06-06 08:32:58.251  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.gms.location.history:478ms  all compileTime:2022987ms
06-06 08:32:58.806  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.ondevicepersonalization.services:491ms  all compileTime:2023478ms
06-06 08:33:55.926  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.apps.youtube.music:57041ms  all compileTime:2080519ms
06-06 08:34:02.164  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.traceur:6025ms  all compileTime:2086544ms
06-06 08:34:06.238  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.cellbroadcastreceiver:4002ms  all compileTime:2090546ms
06-06 08:34:09.119  1151  5315 D PackageDexOptimizer: dex CompileTime---com.mediatek.sensorhub.ui:2821ms  all compileTime:2093367ms
06-06 08:34:14.024  1151  5315 D PackageDexOptimizer: dex CompileTime---com.android.bluetooth:4781ms  all compileTime:2098148ms
06-06 08:34:25.751  1151  5315 D PackageDexOptimizer: dex CompileTime---com.google.android.apps.restore:11395ms  all compileTime:2109543ms

```

