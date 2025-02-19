# 深入理解PackageManagerService Part1：整体流程分析

PackageManagerService是Android系统中最常用的服务之一。它负责系统中Package的管理，应用程序的安装、卸载、信息查询等。图展示了PackageManagerService及客户端的类家族。

![](pkms1.png)

在源码中可能找不到IPackageManager.java文件。该文件在编译过程中是经aidl工具处理IPackageManager.aidl后得到，最终的文件位置在Android源码/out/target/common/obj/JAVA_LIBRARIES/framework_intermediates/src/core/java/android/content/pm/目录中。

## 1. PKMS的创建

PKMS作为系统的核心服务，由SystemServer创建:

在startBootstrapServices()方法中，由SystemServer的run方法启动，在此方法中，主要是进行了以下操作：

​	1.获取设备是否加密(手机设置密码)，如果设备加密了，则只解析"core"应用

​	2.调用PKMS main方法初始化PackageManagerService，其中调用PackageManagerService()构造函数创建了PKMS对象

​	3.如果设备没有加密，操作它。管理A/B OTA dexopting。

``` JAVA
		
private void startBootstrapServices(@NonNull TimingsTraceAndSlog t) {
    	...
        // Only run "core" apps if we're encrypting the device.
        //判断是否为加密，比如手机密码  当设备加密时 则只解析"core"应用，mOnlyCore = true
        String cryptState = VoldProperties.decrypt().orElse("");
    	//ENCRYPTING_STATE值为“trigger_restart_min_framework”
        if (ENCRYPTING_STATE.equals(cryptState)) {
            ...
            mOnlyCore = true;
        } else if (ENCRYPTED_STATE.equals(cryptState)) {
            ...
            mOnlyCore = true;
        }

        // Start the package manager.
        ...
		t.traceBegin("StartPackageManagerService");
        try {
            //暂停watchdog对当前packagemanagermain的锁
            Watchdog.getInstance().pauseWatchingCurrentThread("packagemanagermain");
            //创建PackageManagerService对象并执行它的main方法,mFactoryTestMode用于判断是否为工厂测试
            mPackageManagerService = PackageManagerService.main(mSystemContext, installer,
                    mFactoryTestMode != FactoryTest.FACTORY_TEST_OFF, mOnlyCore);
        } finally {
            Watchdog.getInstance().resumeWatchingCurrentThread("packagemanagermain");
        }

        // Now that the package manager has started, register the dex load reporter to capture any
        // dex files loaded by system server.
        // These dex files will be optimized by the BackgroundDexOptService.
        SystemServerDexLoadReporter.configureSystemServerDexReporter(mPackageManagerService);
    	//是否为初次启动
        mFirstBoot = mPackageManagerService.isFirstBoot();
        mPackageManager = mSystemContext.getPackageManager();
        t.traceEnd();
        if (!mRuntimeRestart && !isFirstBootOrUpgrade()) {
            FrameworkStatsLog.write(FrameworkStatsLog.BOOT_TIME_EVENT_ELAPSED_TIME_REPORTED,
                    FrameworkStatsLog
                            .BOOT_TIME_EVENT_ELAPSED_TIME__EVENT__PACKAGE_MANAGER_INIT_READY,
                    SystemClock.elapsedRealtime());
        }
        // Manages A/B OTA dexopting. This is a bootstrap service as we need it to rename
        // A/B artifacts after boot, before anything else might touch/need them.
        // Note: this isn't needed during decryption (we don't have /data anyways).
        //(4)如果设备没有加密，操作它。管理A/B OTA dexopting。
        if (!mOnlyCore) {
            //接下来对ota包进行dex优化
            boolean disableOtaDexopt = SystemProperties.getBoolean("config.disable_otadexopt",
                    false);
            if (!disableOtaDexopt) {
                t.traceBegin("StartOtaDexOptService");
                try {
                    Watchdog.getInstance().pauseWatchingCurrentThread("moveab");
                    OtaDexoptService.main(mSystemContext, mPackageManagerService);
                } catch (Throwable e) {
                    reportWtf("starting OtaDexOptService", e);
                } finally {
                    Watchdog.getInstance().resumeWatchingCurrentThread("moveab");
                    t.traceEnd();
                }
            }
        }
        ...
        t.traceBegin("StartUiModeManager");
        mSystemServiceManager.startService(UiModeManagerService.class);
        t.traceEnd();

        if (!mOnlyCore) {
            t.traceBegin("UpdatePackagesIfNeeded");
            try {
                Watchdog.getInstance().pauseWatchingCurrentThread("dexopt");
                //对包进行dex优化,dex是Android上针对Java字节码的一种优化技术，可提高运行效率
                mPackageManagerService.updatePackagesIfNeeded();
            } catch (Throwable e) {
                reportWtf("update packages", e);
            } finally {
                Watchdog.getInstance().resumeWatchingCurrentThread("dexopt");
            }
            t.traceEnd();
        }    
        ...   
        try {
             //3 通知系统进入就绪状态
             mPackageManagerService.systemReady();
        }
}
```

这个方法中主要执行了mPackageManagerService的几个方法

分别是：main()、isFirstBoot()、onAmsAddedtoServiceMgr()、updatePackagesIfNeeded()、performFstrimIfNeeded()、systemReady()

isFirstBoot()用于判断是否为开机第一次启动

onAmsAddedtoServiceMgr()主要是为了CTA认证的，不进行详细介绍

updatePackagesIfNeeded()进行dex优化

performFstrimIfNeeded()完成了磁盘维护

接下来详细解读main()和systemReady()方法



## 2. 了解main()方法

在main()中，通过Injector初始化一堆类检查Package编译相关系统属性，同时创建一个PackageManagerService对象，并执行它的构造方法

调用installWhitelistedSystemPackages()方法,根据所有用户的用户类型（如果适用）为所有用户安装/卸载系统软件包。

并在ServiceManager中注册了package以及package_native

```java
public static PackageManagerService main(Context context, Installer installer,
            boolean factoryTest, boolean onlyCore) {
            Injector injector = new Injector(
                context, lock, installer, installLock, new PackageAbiHelperImpl(),
                (i, pm) -> new ComponentResolver(i.getUserManagerService(), pm.mPmInternal, lock),
                (i, pm) -> PermissionManagerService.create(context, lock),
                (i, pm) -> new UserManagerService(context, pm,
                                new UserDataPreparer(installer, installLock, context, onlyCore),
                                lock),
                (i, pm) ->new Settings(Environment.getDataDirectory(),
                                i.getPermissionManagerServiceInternal().getPermissionSettings(),
                                lock),
                new Injector.LocalServicesProducer<>(ActivityTaskManagerInternal.class),
                new Injector.LocalServicesProducer<>(ActivityManagerInternal.class),
                new Injector.LocalServicesProducer<>(DeviceIdleInternal.class),
                new Injector.LocalServicesProducer<>(StorageManagerInternal.class),
                new Injector.LocalServicesProducer<>(NetworkPolicyManagerInternal.class),
                new Injector.LocalServicesProducer<>(PermissionPolicyInternal.class),
                new Injector.LocalServicesProducer<>(DeviceStorageMonitorInternal.class),
                new Injector.SystemServiceProducer<>(DisplayManager.class),
                new Injector.SystemServiceProducer<>(StorageManager.class),
                new Injector.SystemServiceProducer<>(AppOpsManager.class),
                (i, pm) -> AppsFilter.create(pm.mPmInternal, i),
                (i, pm) -> (PlatformCompat) ServiceManager.getService("platform_compat"));

        PackageManagerService m = new PackageManagerService(injector, onlyCore, factoryTest);
        
        m.installWhitelistedSystemPackages();
        ServiceManager.addService("package", m);
        final PackageManagerNative pmn = m.new PackageManagerNative();
        ServiceManager.addService("package_native", pmn);
}
```

那么接下来看PackageManagerService的构造函数:
PKMS构造函数的主要功能是，扫描Android系统中几个目标文件夹中的APK，从而建立合适的数据结构以管理诸如Package信息、四大组件信息、权限信息等各种信息。

## 3. 构造函数**分析**

PKMS的构造函数中由两个重要的锁(mInstallLock、mPackages) 和5个阶段构成

mInstallLock ：用来保护所有安装apk的访问权限，此操作通常涉及繁重的磁盘数据读写等操作，并且是单线程操作，故有时候会处理很慢。
此锁不会在已经持有mPackages锁的情况下火的，反之，在已经持有mInstallLock锁的情况下，立即获取mPackages是安全的

mPackages：用来解析内存中所有apk的package信息及相关状态。

在构造函数中的5个阶段：

阶段1：BOOT_PROGRESS_PMS_START

阶段2：BOOT_PROGRESS_PMS_SYSTEM_SCAN_START

阶段3：BOOT_PROGRESS_PMS_DATA_SCAN_START

阶段4：BOOT_PROGRESS_PMS_SCAN_END

阶段5：BOOT_PROGRESS_PMS_READY

```java
public PackageManagerService(Context context, Installer installer,
        boolean factoryTest, boolean onlyCore) {
        ...
        //阶段1：BOOT_PROGRESS_PMS_START
        EventLog.writeEvent(EventLogTags.BOOT_PROGRESS_PMS_START,
                SystemClock.uptimeMillis());

        //阶段2：BOOT_PROGRESS_PMS_SYSTEM_SCAN_START 
        EventLog.writeEvent(EventLogTags.BOOT_PROGRESS_PMS_SYSTEM_SCAN_START,
                    startTime);
        ...
        
        //阶段3：BOOT_PROGRESS_PMS_DATA_SCAN_START 
        if (!mOnlyCore) {
                EventLog.writeEvent(EventLogTags.BOOT_PROGRESS_PMS_DATA_SCAN_START,
                        SystemClock.uptimeMillis());
        }
        ...
        //阶段4：BOOT_PROGRESS_PMS_SCAN_END 
        EventLog.writeEvent(EventLogTags.BOOT_PROGRESS_PMS_SCAN_END,
                    SystemClock.uptimeMillis());
        ...
        //阶段5：BOOT_PROGRESS_PMS_READY
        EventLog.writeEvent(EventLogTags.BOOT_PROGRESS_PMS_READY,
                    SystemClock.uptimeMillis());
}
```

#### **阶段1：BOOT_PROGRESS_PMS_START**

主要工作：

(1)构造 DisplayMetrics ，保存分辨率等相关信息；

(2)创建Installer对象，与installd交互；

(3)创建mPermissionManager对象，进行权限管理；

(4)构造Settings类，保存安装包信息，清除路径不存在的孤立应用，主要涉及/data/system/目录的packages.xml，packages-backup.xml，packages.list，packages-stopped.xml，packages-stopped-backup.xml等文件。

(5)构造PackageDexOptimizer及DexManager类，处理dex优化；

(6)创建SystemConfig实例，获取系统配置信息，配置共享lib库；

(7)创建PackageManager的handler线程，循环处理外部安装相关消息。

```java
		EventLog.writeEvent(EventLogTags.BOOT_PROGRESS_PMS_START,
                SystemClock.uptimeMillis());
        /// M: Add for Mtprof tool
        sMtkSystemServerIns.addBootEvent("Android:PackageManagerService_Start");

        if (mSdkVersion <= 0) {
            Slog.w(TAG, "**** ro.build.version.sdk not set!");
        }

        mContext = injector.getContext();
        mFactoryTest = factoryTest;		// 判断是否为工厂模式，通常为false
        mOnlyCore = onlyCore;			// 根据用户是否加密来判断是否只加载核心服务
        mMetrics = new DisplayMetrics();	// 获取当前屏幕信息
        mInstaller = injector.getInstaller();	//保存installer对象
        android.util.Log.d("liziluo","test_log: mFactoryTest :" + mFactoryTest);
        android.util.Log.d("liziluo","test_log: mOnlyCore :" + mOnlyCore);

        // Create sub-components that provide services / data. Order here is important.
        t.traceBegin("createSubComponents");

        // Expose private service for system components to use.
        // 公开专用服务供系统组件使用，在之前的版本google将这些组件上了锁
        mPmInternal = new PackageManagerInternalImpl();
        // 本地服务
        LocalServices.addService(PackageManagerInternal.class, mPmInternal);
        // 多用户管理服务
        mUserManager = injector.getUserManagerService();
        mComponentResolver = injector.getComponentResolver();
        // 权限管理服务
        mPermissionManager = injector.getPermissionManagerServiceInternal();
        //创建Settings对象
        mSettings = injector.getSettings();
        mPermissionManagerService = (IPermissionManager) ServiceManager.getService("permissionmgr");
        mIncrementalManager =
                (IncrementalManager) mContext.getSystemService(Context.INCREMENTAL_SERVICE);
        PlatformCompat platformCompat = mInjector.getCompatibility();
        mPackageParserCallback = new PackageParser2.Callback() {
            @Override
            public boolean isChangeEnabled(long changeId, @NonNull ApplicationInfo appInfo) {
                return platformCompat.isChangeEnabled(changeId, appInfo);
            }

            @Override
            public boolean hasFeature(String feature) {
                return PackageManagerService.this.hasSystemFeature(feature, 0);
            }
        };

        // CHECKSTYLE:ON IndentationCheck
        t.traceEnd();
		
		//将各种系统shareUserId添加到mSettings中
        t.traceBegin("addSharedUsers");
        mSettings.addSharedUserLPw("android.uid.system", Process.SYSTEM_UID,
                ApplicationInfo.FLAG_SYSTEM, ApplicationInfo.PRIVATE_FLAG_PRIVILEGED);
        mSettings.addSharedUserLPw("android.uid.phone", RADIO_UID,
                ApplicationInfo.FLAG_SYSTEM, ApplicationInfo.PRIVATE_FLAG_PRIVILEGED);
        mSettings.addSharedUserLPw("android.uid.log", LOG_UID,
                ApplicationInfo.FLAG_SYSTEM, ApplicationInfo.PRIVATE_FLAG_PRIVILEGED);
        mSettings.addSharedUserLPw("android.uid.nfc", NFC_UID,
                ApplicationInfo.FLAG_SYSTEM, ApplicationInfo.PRIVATE_FLAG_PRIVILEGED);
        mSettings.addSharedUserLPw("android.uid.bluetooth", BLUETOOTH_UID,
                ApplicationInfo.FLAG_SYSTEM, ApplicationInfo.PRIVATE_FLAG_PRIVILEGED);
        mSettings.addSharedUserLPw("android.uid.shell", SHELL_UID,
                ApplicationInfo.FLAG_SYSTEM, ApplicationInfo.PRIVATE_FLAG_PRIVILEGED);
        mSettings.addSharedUserLPw("android.uid.se", SE_UID,
                ApplicationInfo.FLAG_SYSTEM, ApplicationInfo.PRIVATE_FLAG_PRIVILEGED);
        mSettings.addSharedUserLPw("android.uid.networkstack", NETWORKSTACK_UID,
                ApplicationInfo.FLAG_SYSTEM, ApplicationInfo.PRIVATE_FLAG_PRIVILEGED);
        t.traceEnd();

```

在执行addSharedUserLPw方法的时候，传递了四个参数
第一个是字符串"android.uid.system"；第二个是Process.SYSTEM_UID，第三个是ApplicationInfo.FLAG_SYSTEM，用于标识是否为系统package
第四个是ApplicationInfo.PRIVATE_FLAG_PRIVILEGED，用于标识是否持有特权权限

那么在AndroidManifest中，如下所示：
对于同一个标识了sharedUserId的应用，之间是可以共享数据的，并且可以运行在同一个进程中；更重要的是，通过声明指定的sharedUserId，来获取对应的权限，例如下面声明了android.uid.system的sharedUserId，那么这个应用将被赋予system用户组所对应的权限

```java
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
       package="com.android.systemui"
       coreApp="true"
       android:sharedUserId="android.uid.system"
       android:process="system">
......
```

接下来继续看阶段1的具体步骤

```java
    String separateProcesses = SystemProperties.get("debug.separate_processes");
    android.util.Log.d("liziluo","test_log: separateProcesses :" + separateProcesses);
    if (separateProcesses != null && separateProcesses.length() > 0) {
        if ("*".equals(separateProcesses)) {
            mDefParseFlags = PackageParser.PARSE_IGNORE_PROCESSES;
            mSeparateProcesses = null;
            Slog.w(TAG, "Running with debug.separate_processes: * (ALL)");
        } else {
            mDefParseFlags = 0;
            mSeparateProcesses = separateProcesses.split(",");
            Slog.w(TAG, "Running with debug.separate_processes: "
                    + separateProcesses);
        }
    } else {
        mDefParseFlags = 0;
        mSeparateProcesses = null;
    }
	
	// 进行dex优化
    mPackageDexOptimizer = new PackageDexOptimizer(mInstaller, mInstallLock, mContext,
            "*dexopt*");
    mDexManager =
            new DexManager(mContext, this, mPackageDexOptimizer, mInstaller, mInstallLock);
    // ART虚拟机管理服务
    mArtManagerService = new ArtManagerService(mContext, this, mInstaller, mInstallLock);
    mMoveCallbacks = new MoveCallbacks(FgThread.get().getLooper());

    mViewCompiler = new ViewCompiler(mInstallLock, mInstaller);
	
	//获取默认的屏幕参数
    getDefaultDisplayMetrics(mInjector.getDisplayManager(), mMetrics);
    android.util.Log.d("liziluo","test_log: mMetrics :" + mMetrics);

    t.traceBegin("get system config");
    //获取systemConfig的对象
    SystemConfig systemConfig，根据 = SystemConfig.getInstance();
    android.util.Log.d("liziluo","test_log: systemConfig :" + systemConfig);
    //利用systemConfig获取当前的可用功能
    mAvailableFeatures = systemConfig.getAvailableFeatures();
    ApplicationPackageManager.invalidateHasSystemFeatureCache();
    t.traceEnd();

	//用于管理需要特殊保护的软件包名称
    mProtectedPackages = new ProtectedPackages(mContext);

    mApexManager = ApexManager.getInstance();
    mAppsFilter = mInjector.getAppsFilter();
	
    final List<ScanPartition> scanPartitions = new ArrayList<>();
    final List<ApexManager.ActiveApexInfo> activeApexInfos = mApexManager.getActiveApexInfos();
    for (int i = 0; i < activeApexInfos.size(); i++) {
        final ScanPartition scanPartition = resolveApexToScanPartition(activeApexInfos.get(i));
        if (scanPartition != null) {
            scanPartitions.add(scanPartition);
        }
    }
	
	//扫描system分区目录
    mDirsToScanAsSystem = new ArrayList<>();
    mDirsToScanAsSystem.addAll(SYSTEM_PARTITIONS);
    mDirsToScanAsSystem.addAll(scanPartitions);
    Slog.d(TAG, "Directories scanned as system partitions: " + mDirsToScanAsSystem);
```

apex和apk类似，实际上也是一个压缩文件。只不过apk和apex的目标不一样

​	.apk是应用程序的载体，对应用开发者而言，可以apk方式对应用功能进行升级。

​	.apex是系统功能的载体，对系统开发者（目前看主要是谷歌）而言，可以apex方式对系统功能进行升级。这些apex包将来就发布在谷歌的playstore上供我们	下载。

apex相当于对系统功能进行了更细粒度的划分，可以独立升级这些功能。而从另外某个意义上来说，这种做法也更加限制了设备厂商的魔改行为——这就是谷歌mainline计划的目的。

```java
		// CHECKSTYLE:OFF IndentationCheck
        synchronized (mInstallLock) {
        // writer
        synchronized (mLock) {
            // 启动"PackageManager"线程，负责apk的安装、卸载
            mHandlerThread = new ServiceThread(TAG,
                    Process.THREAD_PRIORITY_BACKGROUND, true /*allowIo*/);
            mHandlerThread.start();
            android.util.Log.d("liziluo","test_log: start mHandlerThread :");
            // 应用handler
            mHandler = new PackageHandler(mHandlerThread.getLooper());
            // 进程记录handler
            mProcessLoggingHandler = new ProcessLoggingHandler();
            // Watchdog监听ServiceThread是否超时：10分钟
            Watchdog.getInstance().addThread(mHandler, WATCHDOG_TIMEOUT);
            // Instant应用注册
            mInstantAppRegistry = new InstantAppRegistry(this);
			// 共享lib库配置
            ArrayMap<String, SystemConfig.SharedLibraryEntry> libConfig
                    = systemConfig.getSharedLibraries();
            final int builtInLibCount = libConfig.size();
            for (int i = 0; i < builtInLibCount; i++) {
                String name = libConfig.keyAt(i);
                SystemConfig.SharedLibraryEntry entry = libConfig.valueAt(i);
                addBuiltInSharedLibraryLocked(entry.filename, name);
            }
    		...
    		// 读取安装相关SELinux策略
            SELinuxMMAC.readInstallPolicy();
    
            t.traceBegin("loadFallbacks");
            // 返回栈加载
            FallbackCategoryProvider.loadFallbacks();
            t.traceEnd();
    
            t.traceBegin("read user settings");
            //读取并解析/data/system下的XML文件
            mFirstBoot = !mSettings.readLPw(mInjector.getUserManagerInternal().getUsers(false));
            android.util.Log.d("liziluo","test_log: mFirstBoot :" + mFirstBoot);
            t.traceEnd();
    
            /// M: Set PMS/UMS to ext
            sPmsExt.init(this, mUserManager);
            
            // Clean up orphaned packages for which the code path doesn't exist
            // and they are an update to a system app - caused by bug/32321269
            // 清理代码路径不存在的孤立软件包
            final int packageSettingCount = mSettings.mPackages.size();
            android.util.Log.d("liziluo","test_log: packageSettingCount :" + packageSettingCount);
            for (int i = packageSettingCount - 1; i >= 0; i--) {
                PackageSetting ps = mSettings.mPackages.valueAt(i);
                if (!isExternal(ps) && (ps.codePath == null || !ps.codePath.exists())
                        && mSettings.getDisabledSystemPkgLPr(ps.name) != null) {
                    mSettings.mPackages.removeAt(i);
                    mSettings.enableSystemPackageLPw(ps.name);
                }
            }
			// 如果不是首次启动，也不是CORE应用，则拷贝预编译的DEX文件
            if (!mOnlyCore && mFirstBoot) {
                requestCopyPreoptedFiles();
            }
			...
            } // synchronized (mLock)
        }
}
```

在setting的构造函数中，会指向
{packages.xml 、 packages-backup.xml 、 packages.list 、packages-stopped.xml 、packages-stopped-backup.xml}几个文件，然后在**readLPw()**中扫描它

文件共分为三组，简单的作用描述如下：

1: packages.xml：PKMS 扫描完目标文件夹后会创建该文件。当系统进行程序安装、卸载和更新等操作时，均会更新该文件。该文件保存了系统中与 package 相关的一些信息

2: packages.list：描述系统中存在的所有非系统自带的 APK 的信息。当这些程序有变动时，PKMS 就会更新该文件。

3: packages-stopped.xml：从系统自带的设置程序中进入应用程序页面，然后在选择强制停止（ForceStop）某个应用时，系统会将该应用的相关信息记录到此文件中。也就是该文件保存系统中被用户强制停止的 Package 的信息。

**Settings.java**

```java
    mSettingsFilename = new File(mSystemDir, "packages.xml");
    mBackupSettingsFilename = new File(mSystemDir, "packages-backup.xml");
    mPackageListFilename = new File(mSystemDir, "packages.list");
    FileUtils.setPermissions(mPackageListFilename, 0640, SYSTEM_UID, PACKAGE_INFO_GID);

    final File kernelDir = new File("/config/sdcardfs");
    mKernelMappingFilename = kernelDir.exists() ? kernelDir : null;

    // Deprecated: Needed for migration
    mStoppedPackagesFilename = new File(mSystemDir, "packages-stopped.xml");
    mBackupStoppedPackagesFilename = new File(mSystemDir, "packages-stopped-backup.xml");
```

将这些目录构建后，将会在readLPw()中进行扫描,这些文件都处于/data/system 下

```java
boolean readLPw(@NonNull List<UserInfo> users) {
	...
	//对XML进行解析
	XmlPullParser parser = Xml.newPullParser();
	...
	//根据XML中的tag进行操作，例如读取权限、shared-user等
	while ((type = parser.next()) != XmlPullParser.END_DOCUMENT
                    && (type != XmlPullParser.END_TAG || parser.getDepth() > outerDepth)) {
                if (type == XmlPullParser.END_TAG || type == XmlPullParser.TEXT) {
                    continue;
                }

                String tagName = parser.getName();
                if (tagName.equals("package")) {
                    readPackageLPw(parser);
                } else if (tagName.equals("permissions")) {
                    mPermissions.readPermissions(parser);
                } else if (tagName.equals("permission-trees")) {
                    mPermissions.readPermissionTrees(parser);
                } else if (tagName.equals("shared-user")) {
                    readSharedUserLPw(parser);
                } else if (tagName.equals("preferred-packages")) {
                    // no longer used.
                } 
	...
	}
	...
}	
	
```

#### 阶段2：BOOT_PROGRESS_PMS_SYSTEM_SCAN_START

主要工作：

(1)从init.rc中获取环境变量BOOTCLASSPATH和SYSTEMSERVERCLASSPATH；

(2)对于旧版本升级的情况，将安装时获取权限变更为运行时申请权限；

(3)扫描system/vendor/product/odm/oem等目录的priv-app、app、overlay包；

(4)清除安装时临时文件以及其他不必要的信息。

```java
// CHECKSTYLE:OFF IndentationCheck
        synchronized (mInstallLock) {
        // writer
        synchronized (mLock) {
			...
			//记录开始的时间
            long startTime = SystemClock.uptimeMillis();

            EventLog.writeEvent(EventLogTags.BOOT_PROGRESS_PMS_SYSTEM_SCAN_START,
                    startTime);
            /// M: Add for Mtprof tool
            sMtkSystemServerIns.addBootEvent("Android:PMS_scan_START");

            /// M: CTA requirement - permission control
            CtaManagerFactory.getInstance().makeCtaManager().createCtaPermsController(mContext);
            /// M: Removable system app support
            sPmsExt.initBeforeScan();
			
            //获取环境变量,init.rc
            final String bootClassPath = System.getenv("BOOTCLASSPATH");
            final String systemServerClassPath = System.getenv("SYSTEMSERVERCLASSPATH");

            android.util.Log.d("liziluo","test_log: bootClassPath :" + bootClassPath);
            android.util.Log.d("liziluo","test_log: systemServerClassPath :" + systemServerClassPath);

            if (bootClassPath == null) {
                Slog.w(TAG, "No BOOTCLASSPATH found!");
            }

            if (systemServerClassPath == null) {
                Slog.w(TAG, "No SYSTEMSERVERCLASSPATH found!");
            }
			// 获取system/framework目录
            File frameworkDir = new File(Environment.getRootDirectory(), "framework");
            // 获取内部版本
            final VersionInfo ver = mSettings.getInternalVersion();
            // 判断fingerprint是否有更新
            mIsUpgrade = !Build.FINGERPRINT.equals(ver.fingerprint);
            android.util.Log.d("liziluo","test_log: mIsUpgrade :" + mIsUpgrade);
            if (mIsUpgrade) {
                logCriticalInfo(Log.INFO,
                        "Upgrading from " + ver.fingerprint + " to " + Build.FINGERPRINT);
            }
            // when upgrading from pre-M, promote system app permissions from install to runtime
            // 对于Android M之前版本升级上来的情况，需将系统应用程序权限从安装升级到运行时
            mPromoteSystemApps =
                    mIsUpgrade && ver.sdkVersion <= Build.VERSION_CODES.LOLLIPOP_MR1;

            // When upgrading from pre-N, we need to handle package extraction like first boot,
            // as there is no profiling data available.
            // 对于Android N之前版本升级上来的情况，需像首次启动一样处理package
            mIsPreNUpgrade = mIsUpgrade && ver.sdkVersion < Build.VERSION_CODES.N;
            mIsPreNMR1Upgrade = mIsUpgrade && ver.sdkVersion < Build.VERSION_CODES.N_MR1;
            mIsPreQUpgrade = mIsUpgrade && ver.sdkVersion < Build.VERSION_CODES.Q;

            // Save the names of pre-existing packages prior to scanning, so we can determine
            // which system packages are completely new due to an upgrade.
            //在扫描之前保存已存在的包的名称，以便我们可以确定由于升级，哪些系统包是全新的。
            if (isDeviceUpgrading()) {
                mExistingPackages = new ArraySet<>(mSettings.mPackages.size());
                for (PackageSetting ps : mSettings.mPackages.values()) {
                    mExistingPackages.add(ps.name);
                }
            }
			//准备解析package的缓存
            mCacheDir = preparePackageParserCache();

            // Set flag to monitor and not change apk file paths when
            // scanning install directories.
            //设置flag，而不在扫描安装时更改文件路径
            int scanFlags = SCAN_BOOTING | SCAN_INITIAL;

            if (mIsUpgrade || mFirstBoot) {
                scanFlags = scanFlags | SCAN_FIRST_BOOT_OR_UPGRADE;
            }

            final int systemParseFlags = mDefParseFlags | PackageParser.PARSE_IS_SYSTEM_DIR;
            final int systemScanFlags = scanFlags | SCAN_AS_SYSTEM;

            PackageParser2 packageParser = new PackageParser2(mSeparateProcesses, mOnlyCore,
                    mMetrics, mCacheDir, mPackageParserCallback);

            ExecutorService executorService = ParallelPackageParser.makeExecutorService();
            // Prepare apex package info before scanning APKs, these information are needed when
            // scanning apk in apex.
            mApexManager.scanApexPackagesTraced(packageParser, executorService);
            // Collect vendor/product/system_ext overlay packages. (Do this before scanning
            // any apps.)
            // For security and version matching reason, only consider overlay packages if they
            // reside in the right directory.
            //扫描此路径下的所有app 在scanDirTracedLI进行安装
            for (int i = mDirsToScanAsSystem.size() - 1; i >= 0; i--) {
                final ScanPartition partition = mDirsToScanAsSystem.get(i);
                /// M: Support RSC overlay dir
                sPmsExt.scanDirLI(partition.type, true, systemParseFlags,
                        systemScanFlags | partition.scanFlag, 0,
                        packageParser, executorService);

                if (partition.getOverlayFolder() == null) {
                    continue;
                }
                scanDirTracedLI(partition.getOverlayFolder(), systemParseFlags,
                        systemScanFlags | partition.scanFlag, 0,
                        packageParser, executorService);
            }

            /// M: Support RSC framework dir
            //jar包、apk的安装
            scanDirTracedLI(frameworkDir, systemParseFlags,
                    systemScanFlags | SCAN_NO_DEX | SCAN_AS_PRIVILEGED, 0,
                    packageParser, executorService);
			scanDirTracedLI(partition.getPrivAppFolder(), systemParseFlags,
                    systemScanFlags | SCAN_AS_PRIVILEGED | partition.scanFlag, 0,
                    packageParser, executorService);
            scanDirTracedLI(partition.getAppFolder(), systemParseFlags,
                    systemScanFlags | partition.scanFlag, 0,
                    packageParser, executorService);
            ...
            // 后续的操作主要是删掉不存在的package，并且对于系统应用，不允许被删除
```

在scanDirTracedLI中会去扫描,扫描成功后会在parallelPackageParser进行解析，从此方法开始开始真正开启扫描流程

我们先来看下扫描阶段的整体时序图:

![](scanDIr时序图.png)

在scanDirTracedLI()中，首先判断被扫描目录下各个安装包路径的合法性，它必须满足如下的两个条件：

1：首先各个安装包路径必须是apk文件或者是一个文件夹

2：然后各个安装包文件名称不能是应用安装过程的临时存储类型的文件

文件名称不可以是:
 1.不能以vmdl开头且不以 .tmp结尾；
 2.不能以smdl开头且不以 .tmp结尾；
 3.不能以smdl2tmp开头；

这一块流程比较复杂，只简单介绍一下，下面是整个扫描APP的流程

![](pkms逻辑.png)



#### 阶段3：BOOT_PROGRESS_PMS_DATA_SCAN_START

**主要工作有：**对于不仅仅解析核心应用的情况下，还处理data目录的应用信息，及时更新，祛除不必要的数据。

扫描非系统应用分区目录下的应用，主要包括如下几个目录:

    /data/app
    /data/app-asec
    /data/app-ephemeral
    /data/app-private

在系统应用和非系统应用扫描完成之后，会最后来统一处理前面一次扫描的系统App不存在的情况，或者前面一次扫描系统App存在覆盖升级安装在data目录下的应用，但是这次扫描没有存在则需要重新解析system分区的package

- 更新所有应用的动态库路径，保证他们有正确的共享库路径
- 调整所有共享uid 的package的指令集
- 系统中所有的package都被扫描刀了，最后是更新上一次的扫描的相关信息，即将最新的扫描结果写入packages.xml中

``` JAVA
			if (!mOnlyCore) {
                EventLog.writeEvent(EventLogTags.BOOT_PROGRESS_PMS_DATA_SCAN_START,
                        SystemClock.uptimeMillis());
                scanDirTracedLI(sAppInstallDir, 0, scanFlags | SCAN_REQUIRE_KNOWN, 0,
                        packageParser, executorService);

            }
    
            packageParser.close();
    
            List<Runnable> unfinishedTasks = executorService.shutdownNow();
            if (!unfinishedTasks.isEmpty()) {
                throw new IllegalStateException("Not all tasks finished before calling close: "
                        + unfinishedTasks);
            }
    
            if (!mOnlyCore) {
                // Remove disable package settings for updated system apps that were
                // removed via an OTA. If the update is no longer present, remove the
                // app completely. Otherwise, revoke their system privileges.
                // 移除通过OTA删除的更新系统应用程序的禁用package设置
                // 如果更新不再存在，则完全删除该应用。否则，撤消其系统权限
                for (int i = possiblyDeletedUpdatedSystemApps.size() - 1; i >= 0; --i) {
                    final String packageName = possiblyDeletedUpdatedSystemApps.get(i);
                    final AndroidPackage pkg = mPackages.get(packageName);
                    final String msg;
    
                    // remove from the disabled system list; do this first so any future
                    // scans of this package are performed without this state
                 	//从禁用系统列表中删除;先做这个，以后会怎么样
					//在没有此状态的情况下执行该包的扫描
                    mSettings.removeDisabledSystemPackageLPw(packageName);
    
                    if (pkg == null) {
                        // should have found an update, but, we didn't; remove everything
                        msg = "Updated system package " + packageName
                                + " no longer exists; removing its data";
                        // Actual deletion of code and data will be handled by later
                        // reconciliation step
                    } else {
                        // found an update; revoke system privileges
                        msg = "Updated system package " + packageName
                                + " no longer exists; rescanning package on data";
    
                        // NOTE: We don't do anything special if a stub is removed from the
                        // system image. But, if we were [like removing the uncompressed
                        // version from the /data partition], this is where it'd be done.
    
                        // remove the package from the system and re-scan it without any
                        // special privileges
                        //从系统中删除该包并重新扫描
                        //特殊权限
                        removePackageLI(pkg, true);
                        try {
                            final File codePath = new File(pkg.getCodePath());
                            scanPackageTracedLI(codePath, 0, scanFlags, 0, null);
                        } catch (PackageManagerException e) {
                            Slog.e(TAG, "Failed to parse updated, ex-system package: "
                                    + e.getMessage());
                        }
                    }
    
                    // one final check. if we still have a package setting [ie. it was
                    // previously scanned and known to the system], but, we don't have
                    // a package [ie. there was an error scanning it from the /data
                    // partition], completely remove the package data.
                    final PackageSetting ps = mSettings.mPackages.get(packageName);
                    if (ps != null && mPackages.get(packageName) == null) {
                        removePackageDataLIF(ps, null, null, 0, false);
    
                    }
                    logCriticalInfo(Log.WARN, msg);
                }
    
                /*
                 * Make sure all system apps that we expected to appear on
                 * the userdata partition actually showed up. If they never
                 * appeared, crawl back and revive the system version.
                 */
                // 确保期望在userdata分区上显示的所有系统应用程序实际显示
                // 如果从未出现过，需要回滚以恢复系统版本
                for (int i = 0; i < mExpectingBetter.size(); i++) {
                    final String packageName = mExpectingBetter.keyAt(i);
                    if (!mPackages.containsKey(packageName)) {
                        final File scanFile = mExpectingBetter.valueAt(i);
    
                        logCriticalInfo(Log.WARN, "Expected better " + packageName
                                + " but never showed up; reverting to system");
    
                        @ParseFlags int reparseFlags = 0;
                        @ScanFlags int rescanFlags = 0;
                        for (int i1 = mDirsToScanAsSystem.size() - 1; i1 >= 0; i1--) {
                            final ScanPartition partition = mDirsToScanAsSystem.get(i1);
                            if (partition.containsPrivApp(scanFile)) {
                                reparseFlags = systemParseFlags;
                                rescanFlags = systemScanFlags | SCAN_AS_PRIVILEGED
                                        | partition.scanFlag;
                                break;
                            }
                            if (partition.containsApp(scanFile)) {
                                reparseFlags = systemParseFlags;
                                rescanFlags = systemScanFlags | partition.scanFlag;
                                break;
                            }
                        }
                        if (rescanFlags == 0) {
                            Slog.e(TAG, "Ignoring unexpected fallback path " + scanFile);
                            continue;
                        }
                        //判断package是否有效
                        mSettings.enableSystemPackageLPw(packageName);
    
                        try {
                            //扫描APK
                            scanPackageTracedLI(scanFile, reparseFlags, rescanFlags, 0, null);
                        } catch (PackageManagerException e) {
                            Slog.e(TAG, "Failed to parse original system package: "
                                    + e.getMessage());
                        }
                    }
                }
    
                // Uncompress and install any stubbed system applications.
                // This must be done last to ensure all stubs are replaced or disabled.
                // 解压缩并安装任何存根系统应用程序。必须最后执行此操作以确保替换或禁用所有存根
                installSystemStubPackages(stubSystemApps, scanFlags);
    
                final int cachedNonSystemApps = PackageCacher.sCachedPackageReadCount.get()
                                - cachedSystemApps;
    
                final long dataScanTime = SystemClock.uptimeMillis() - systemScanTime - startTime;
                final int dataPackagesCount = mPackages.size() - systemPackagesCount;
                Slog.i(TAG, "Finished scanning non-system apps. Time: " + dataScanTime
                        + " ms, packageCount: " + dataPackagesCount
                        + " , timePerPackage: "
                        + (dataPackagesCount == 0 ? 0 : dataScanTime / dataPackagesCount)
                        + " , cached: " + cachedNonSystemApps);
                if (mIsUpgrade && dataPackagesCount > 0) {
                    //CHECKSTYLE:OFF IndentationCheck
                    FrameworkStatsLog.write(
                        FrameworkStatsLog.BOOT_TIME_EVENT_DURATION_REPORTED,
                        BOOT_TIME_EVENT_DURATION__EVENT__OTA_PACKAGE_MANAGER_DATA_APP_AVG_SCAN_TIME,
                        dataScanTime / dataPackagesCount);
                    //CHECKSTYLE:OFF IndentationCheck
                }
            }
            mExpectingBetter.clear();
    
            // Resolve the storage manager.
            // 获取storage manager包名
            mStorageManagerPackage = getStorageManagerPackageName();
    
            // Resolve protected action filters. Only the setup wizard is allowed to
            // have a high priority filter for these actions.
            // 解决受保护的action过滤器。只允许setup wizard（开机向导）为这些action设置高优先级过滤器
            mSetupWizardPackage = getSetupWizardPackageNameImpl();
            mComponentResolver.fixProtectedFilterPriorities();
    
            mDefaultTextClassifierPackage = getDefaultTextClassifierPackageName();
            mSystemTextClassifierPackageName = getSystemTextClassifierPackageName();
            mWellbeingPackage = getWellbeingPackageName();
            mDocumenterPackage = getDocumenterPackageName();
            mConfiguratorPackage = getDeviceConfiguratorPackageName();
            mAppPredictionServicePackage = getAppPredictionServicePackageName();
            mIncidentReportApproverPackage = getIncidentReportApproverPackageName();
            mRetailDemoPackage = getRetailDemoPackageName();
    
            // Now that we know all of the shared libraries, update all clients to have
            // the correct library paths.
            // 更新客户端以确保持有正确的共享库路径
            updateAllSharedLibrariesLocked(null, null, Collections.unmodifiableMap(mPackages));
    
            for (SharedUserSetting setting : mSettings.getAllSharedUsersLPw()) {
                // NOTE: We ignore potential failures here during a system scan (like
                // the rest of the commands above) because there's precious little we
                // can do about it. A settings error is reported, though.
                final List<String> changedAbiCodePath =
                        applyAdjustedAbiToSharedUser(setting, null /*scannedPackage*/,
                        mInjector.getAbiHelper().getAdjustedAbiForSharedUser(
                                setting.packages, null /*scannedPackage*/));
                if (changedAbiCodePath != null && changedAbiCodePath.size() > 0) {
                    for (int i = changedAbiCodePath.size() - 1; i >= 0; --i) {
                        final String codePathString = changedAbiCodePath.get(i);
                        try {
                            mInstaller.rmdex(codePathString,
                                    getDexCodeInstructionSet(getPreferredInstructionSet()));
                        } catch (InstallerException ignored) {
                        }
                    }
                }
                // Adjust seInfo to ensure apps which share a sharedUserId are placed in the same
                // SELinux domain.
                setting.fixSeInfoLocked();
                setting.updateProcesses();
            }
    
            // Now that we know all the packages we are keeping,
            // read and update their last usage times.
            // 读取并更新要保留的package的上次使用时间
            mPackageUsage.read(mSettings.mPackages);
            mCompilerStats.read();
```

#### 阶段4：BOOT_PROGRESS_PMS_SCAN_END

**主要工作：**

1：如果当前的Android版本是通过OTA升级上来的，需要对相关的应用的权限做一些动态调整

2：做一些相关的清理工作，并把最新的Settings的内容保存到packages.xml中去

3：调用reconcileAppsDataLI()方法处理应用数据目录，假如被扫描的应用没有对应的应用数据目录，则会进行创建和处理

4：如果当前的Android终端是第一次开机，对Android核心的应用做odex的优化处理

```java
		EventLog.writeEvent(EventLogTags.BOOT_PROGRESS_PMS_SCAN_END,
                    SystemClock.uptimeMillis());
            /// M: Add for Mtprof tool
            sMtkSystemServerIns.addBootEvent("Android:PMS_scan_END");
            Slog.i(TAG, "Time to scan packages: "
  		 + ((SystemClock.uptimeMillis()-startTime)/1000f)

            // If the platform SDK has changed since the last time we booted,
            // we need to re-grant app permission to catch any new ones that
            // appear.  This is really a hack, and means that apps can in some
            // cases get permissions that the user didn't initially explicitly
            // allow...  it would be nice to have some better way to handle
            // this situation.
            // 如果自上次启动以来，平台SDK已改变，则需要重新授予应用程序权限以捕获出现的任何新权限
            final boolean sdkUpdated = (ver.sdkVersion != mSdkVersion);
            if (sdkUpdated) {
                Slog.i(TAG, "Platform changed from " + ver.sdkVersion + " to "
                        + mSdkVersion + "; regranting permissions for internal storage");
            }
            mPermissionManager.updateAllPermissions(
                    StorageManager.UUID_PRIVATE_INTERNAL, sdkUpdated);
            ver.sdkVersion = mSdkVersion;
    
            // If this is the first boot or an update from pre-M, and it is a normal
            // boot, then we need to initialize the default preferred apps across
            // all defined users.
            // 如果这是第一次启动或来自Android M之前的版本的升级，并且它是正常启动，那需要在所有已定义的用户中初始化默认的首选应用程序
            if (!mOnlyCore && (mPromoteSystemApps || mFirstBoot)) {
                for (UserInfo user : mInjector.getUserManagerInternal().getUsers(true)) {
                    mSettings.applyDefaultPreferredAppsLPw(user.id);
                    primeDomainVerificationsLPw(user.id);
                }
            }
    
            // Prepare storage for system user really early during boot,
            // since core system apps like SettingsProvider and SystemUI
            // can't wait for user to start
            // 在启动期间确实为系统用户准备存储，因为像SettingsProvider和SystemUI这样的核心系统应用程序无法等待用户启动
            final int storageFlags;
            if (StorageManager.isFileEncryptedNativeOrEmulated()) {
                storageFlags = StorageManager.FLAG_STORAGE_DE;
            } else {
                storageFlags = StorageManager.FLAG_STORAGE_DE | StorageManager.FLAG_STORAGE_CE;
            }
            List<String> deferPackages = reconcileAppsDataLI(StorageManager.UUID_PRIVATE_INTERNAL,
                    UserHandle.USER_SYSTEM, storageFlags, true /* migrateAppData */,
                    true /* onlyCoreApps */);
            mPrepareAppDataFuture = SystemServerInitThreadPool.submit(() -> {
                TimingsTraceLog traceLog = new TimingsTraceLog("SystemServerTimingAsync",
                        Trace.TRACE_TAG_PACKAGE_MANAGER);
                traceLog.traceBegin("AppDataFixup");
                try {
                    mInstaller.fixupAppData(StorageManager.UUID_PRIVATE_INTERNAL,
                            StorageManager.FLAG_STORAGE_DE | StorageManager.FLAG_STORAGE_CE);
                } catch (InstallerException e) {
                    Slog.w(TAG, "Trouble fixing GIDs", e);
                }
                traceLog.traceEnd();
    
                traceLog.traceBegin("AppDataPrepare");
                if (deferPackages == null || deferPackages.isEmpty()) {
                    return;
                }
                int count = 0;
                for (String pkgName : deferPackages) {
                    AndroidPackage pkg = null;
                    synchronized (mLock) {
                        PackageSetting ps = mSettings.getPackageLPr(pkgName);
                        if (ps != null && ps.getInstalled(UserHandle.USER_SYSTEM)) {
                            pkg = ps.pkg;
                        }
                    }
                    if (pkg != null) {
                        synchronized (mInstallLock) {
                            prepareAppDataAndMigrateLIF(pkg, UserHandle.USER_SYSTEM, storageFlags,
                                    true /* maybeMigrateAppData */);
                        }
                        count++;
                    }
                }
                traceLog.traceEnd();
                Slog.i(TAG, "Deferred reconcileAppsData finished " + count + " packages");
            }, "prepareAppData");
    
            // If this is first boot after an OTA, and a normal boot, then
            // we need to clear code cache directories.
            // Note that we do *not* clear the application profiles. These remain valid
            // across OTAs and are used to drive profile verification (post OTA) and
            // profile compilation (without waiting to collect a fresh set of profiles).
            if (mIsUpgrade && !mOnlyCore) {
                Slog.i(TAG, "Build fingerprint changed; clearing code caches");
                for (int i = 0; i < mSettings.mPackages.size(); i++) {
                    final PackageSetting ps = mSettings.mPackages.valueAt(i);
                    if (Objects.equals(StorageManager.UUID_PRIVATE_INTERNAL, ps.volumeUuid)) {
                        // No apps are running this early, so no need to freeze
                        clearAppDataLIF(ps.pkg, UserHandle.USER_ALL,
                                FLAG_STORAGE_DE | FLAG_STORAGE_CE | FLAG_STORAGE_EXTERNAL
                                        | Installer.FLAG_CLEAR_CODE_CACHE_ONLY
                                        | Installer.FLAG_CLEAR_APP_DATA_KEEP_ART_PROFILES);
                    }
                }
                ver.fingerprint = Build.FINGERPRINT;
            }
    
            // Grandfather existing (installed before Q) non-system apps to hide
            // their icons in launcher.
            //安装Android-Q前的非系统应用程序在Launcher中隐藏他们的图标
            if (!mOnlyCore && mIsPreQUpgrade) {
                Slog.i(TAG, "Whitelisting all existing apps to hide their icons");
                int size = mSettings.mPackages.size();
                for (int i = 0; i < size; i++) {
                    final PackageSetting ps = mSettings.mPackages.valueAt(i);
                    if ((ps.pkgFlags & ApplicationInfo.FLAG_SYSTEM) != 0) {
                        continue;
                    }
                    ps.disableComponentLPw(PackageManager.APP_DETAILS_ACTIVITY_CLASS_NAME,
                            UserHandle.USER_SYSTEM);
                }
            }
    
            // clear only after permissions and other defaults have been updated
            // 仅在权限或其它默认配置更新后清除
            mPromoteSystemApps = false;
    
            // All the changes are done during package scanning.
            // 所有变更均在扫描过程中完成
            ver.databaseVersion = Settings.CURRENT_DATABASE_VERSION;
    
            // can downgrade to reader
            //降级去读取
            t.traceBegin("write settings");
            mSettings.writeLPr();
            t.traceEnd();
```

在prepareAppDataAndMigrateLIF()中会执行maybeMigrateAppDataLIF()方法，那么对于非fbe设备上的系统应用程序，此方法迁移任何现有的CE/DE数据匹配{@code defaultToDeviceProtectedStorage}标志，也就是说在设备为FDE加密或者其他加密方式时，会将匹配的数据进行迁移。

从android10开始，MTK的默认加密方式为FDE，也就是说现在的版本都会进行数据的迁移。同时，对于想要开启FBE加密，可以通过关闭宏控来达到。

```
ProjectConifg.mk

1. FDE:default FDE

  MTK_ENCRYPTION_DEFAULT_OFF = no
  MTK_ENCRYPTION_FDE_TO_FBE = no
  MTK_ENCRYPTION_TYPE_FILE = no

2. FBE:default FBE(from android Q,it is mandatory)

  MTK_ENCRYPTION_DEFAULT_OFF = no
  MTK_ENCRYPTION_FDE_TO_FBE = no
  MTK_ENCRYPTION_TYPE_FILE = yes

3. FDE to FBE:default FDE,and you can transfer to FBE in settings.

  MTK_ENCRYPTION_DEFAULT_OFF = no
  MTK_ENCRYPTION_FDE_TO_FBE = yes
  MTK_ENCRYPTION_TYPE_FILE = yes

4. uncrypt:

  MTK_ENCRYPTION_DEFAULT_OFF = yes
  MTK_ENCRYPTION_FDE_TO_FBE = no
  MTK_ENCRYPTION_TYPE_FILE = no
```

#### 阶段5：BOOT_PROGRESS_PMS_READY

**主要工作有：**

(1)创建PackageInstallerService对象

(2)GC回收内存

```java
 
public PackageManagerService(Context context, Installer installer,
            boolean factoryTest, boolean onlyCore) {
    synchronized (mInstallLock) {
        synchronized (mPackages) {
            ...
            EventLog.writeEvent(EventLogTags.BOOT_PROGRESS_PMS_READY,
                    SystemClock.uptimeMillis());
            ...
            //PermissionController 主持 缺陷许可证的授予和角色管理，所以这是核心系统的一个关键部分。
            mRequiredPermissionControllerPackage = getRequiredPermissionControllerLPr();
            ...
            updateInstantAppInstallerLocked(null);
            // 阅读并更新dex文件的用法
            // 在PM init结束时执行此操作，以便所有程序包都已协调其数据目录
            // 此时知道了包的代码路径，因此可以验证磁盘文件并构建内部缓存
            // 使用文件预计很小，因此与其他活动（例如包扫描）相比，加载和验证它应该花费相当小的时间
            final Map<Integer, List<PackageInfo>> userPackages = new HashMap<>();
            for (int userId : userIds) {
                userPackages.put(userId, getInstalledPackages(/*flags*/ 0, userId).getList());
            }
            mDexManager.load(userPackages);
            if (mIsUpgrade) {
                MetricsLogger.histogram(null, "ota_package_manager_init_time",
                        (int) (SystemClock.uptimeMillis() - startTime));
            }
        }
    }
    ...
    // 打开应用之后，及时回收处理
    Runtime.getRuntime().gc();
    // 上面的初始扫描在持有mPackage锁的同时对installd进行了多次调用
    mInstaller.setWarnIfHeld(mPackages);
    ...
}
```