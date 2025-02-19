# 进入Gmail、play store和maps闪退问题分析和解决方案

## 问题分析

1：复现步骤：恢复出厂设置或者刷机后，英文模式下开机-设置屏幕锁-连接翻墙网-直接扣电池后开机，进入以上谷歌应用概率性出现闪退现象，重启机器可恢复。

2：截取相关LOG

```log
02-16 15:31:10.385721 22079 22079 E AndroidRuntime: Caused by:  java.lang.IllegalStateException: Call to getInstalledModules before  metadata loaded
02-16 15:31:10.385721 22079 22079 E AndroidRuntime:     at android.os.Parcel.createException(Parcel.java:2079)
02-16 15:31:10.385721 22079 22079 E AndroidRuntime:     at android.os.Parcel.readException(Parcel.java:2039)
02-16 15:31:10.385721 22079 22079 E AndroidRuntime:     at android.os.Parcel.readException(Parcel.java:1987)
02-16 15:31:10.385721 22079 22079 E AndroidRuntime:     at  android.content.pm.IPackageManager$Stub$Proxy.getInstalledModules(IPackageManager.java:9964)
02-16 15:31:10.385721 22079 22079 E AndroidRuntime:     at  android.app.ApplicationPackageManager.getInstalledModules(ApplicationPackageManager.java:852)
```

3：分析LOG

从log可知，在加载metadata之前调用了 getInstalledModules(), 在ApplicationPackageManager.java触发最后调用在了ModuleInfoProvider.java.通过追踪代

码，发现是pkms加载报错导致加载systemReady失败.

在异常断电重启的时候，需要对metadata进行加密，而加密方式的转变以及异常关机没有走完正常shutdown的流程，可能会导致分区出现异常，重启时

data加密出现问题

```log
05-04 09:05:36.577  1060  1084 I pm_critical_info: Failed to migrate  com.google.android.overlay.modules.modulemetadata.forframework:  android.os.ServiceSpecificException: Failed to mark default storage  /data/data/com.google.android.overlay.modules.modulemetadata.forframework (code 95)
05-04 09:06:12.145  2222  2222 W /system/bin/idmap2:  failed to create idmap for overlay apk path  "/product/overlay/ModuleMetadataGoogleOverlay.apk": uid 0 does not have  write access to /data/resource-cache/product@[overlay@ModuleMetadataGoogleOverlay.apk](mailto:overlay@ModuleMetadataGoogleOverlay.apk)@idmap
05-04 09:06:23.129  2224  2224 I SystemServer: chengqianlog12
```

从log看数据迁移时发生了错误

具体到代码中是:在ModuleInfoProvider中执行systemReady时发生crash 


```java
final Resources packageResources;
final PackageInfo pi;
try {
    pi = mPackageManager.getPackageInfo(mPackageName,
        PackageManager.GET_META_DATA, UserHandle.USER_SYSTEM);

    Context packageContext = mContext.createPackageContext(mPackageName, 0);
    packageResources = packageContext.getResources();
} catch (RemoteException | NameNotFoundException e) {
    Slog.w(TAG, "Unable to discover metadata package: " + mPackageName, e);
    return;
}`
```

当给pi进行赋值的时候，mPackageName找不到 ，而mPackageName找的是R.string.config_defaultModuleMetadataProvider ，这个变量在config.xml中显示的是com.android.modulemetadata ，但是mainline将com.google.android.modulemetadata覆盖了
在重启之后，首先会找到com.google，然后输入开机密码，重新启动系统，这个时候会调用两次，第一次正常找到com.google，但是在第二次复调的时候它会去找com.android，这个时候在catch中抛出NameNotFoundException异常，提示无法找到com.android.metadata

原因是加密方式的转变导致在开机重启时会发生数据迁移，当数据迁移未完成时就进行overlay的动作，导致overlay失效


## 解决方案

1: 当抛出异常的时候，指定mPackageName为com.google.android.modulemetadata，但是因为CN版本是com,android.modulemetadata，所以在指定之前进行版本的判断，当不为CN版本时（没有GMS），指定为com.google.android.modulemetadata -> 后续使用此方案时，发现还是有概率会导致闪退

2：根据ModuleInfoProvider中mPackageName来判断当前的metadata是否被正确加载，当未加载时返回false，在PKMS中重新准备包信息
使用此方案时，当机器的metadata未正确加载，那么设备会等待数据迁移，一直执行reconcileAppsData，直到metadata加载完毕，开机时间会比较久

**ModuleInfoProvider.java**

```java
public void systemReady() {
        mPackageName = mContext.getResources().getString(
                R.string.config_defaultModuleMetadataProvider);
        //add by liziluo
        Slog.d("liziluo11" , " mPackageName : " + mPackageName);
        if (!mPackageName.equals("com.google.android.modulemetadata")) {
            numOfMetadata = 0;
        }
        //add by liziluo
   		...
            
        } catch (XmlPullParserException | IOException e) {
            Slog.w(TAG, "Error parsing module metadata", e);
            mModuleInfo.clear();
        } finally {
            parser.close();
            mMetadataLoaded = true;
    		//add by liziluo
            numOfMetadata = 1;
   			//add by liziluo
        }
    }
```




**PackageManagerService.java**

```java
private void prepareAppDataAndMigrateLIF(PackageParser.Package pkg, int userId, int flags,
        boolean maybeMigrateAppData) {
    prepareAppDataLIF(pkg, userId, flags);
    
    //add by liziluo
    if(mModuleInfoProvider.getMetadata() == 0){
        Slog.d("liziluo", "<<  reconcileAppsData >>");
        reconcileAppsData(userId, flags, maybeMigrateAppData);
    }
    /add by liziluo

    //Slog.v("chengqianlog123", "pkg:"+pkg.packageName+"--maybeMigrateAppData:"+maybeMigrateAppData);
    if (maybeMigrateAppData && maybeMigrateAppDataLIF(pkg, userId)) {
        // We may have just shuffled around app data directories, so
        // prepare them one more time
        prepareAppDataLIF(pkg, userId, flags);
    }
}
```
