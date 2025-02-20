

最新推荐文章于 2024-12-04 13:35:09 发布

![](https://csdnimg.cn/release/blogv2/dist/pc/img/original.png)

[青春给了狗](https://blog.csdn.net/a546036242 "青春给了狗") ![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCurrentTime2.png)于 2022-05-23 20:11:04 发布

![](https://csdnimg.cn/release/blogv2/dist/pc/img/articleReadEyes2.png)阅读量3.3k ![](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarCollect2.png)![](https://csdnimg.cn/release/blogv2/dist/pc/img/tobarCollectionActive2.png)收藏 11

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newHeart2023Active.png) ![](https://csdnimg.cn/release/blogv2/dist/pc/img/newHeart2023Black.png)点赞数 7

文章标签： [android](https://so.csdn.net/so/search/s.do?q=android&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)

版权声明：本文为博主原创文章，遵循 [CC 4.0 BY-SA](http://creativecommons.org/licenses/by-sa/4.0/) 版权协议，转载请附上原文出处链接和本声明。

本文链接：https://blog.csdn.net/a546036242/article/details/124920865

版权

![](https://img-home.csdnimg.cn/images/20240711042549.png) 这篇博客详细介绍了如何在Android系统中通过ContentProvider和修改系统核心源码实现对应用安装白名单和卸载黑名单的拦截。具体步骤包括创建ContentProvider、查询和操作数据库、在PackageManagerService中拦截安装和卸载过程。此外，还提供了一个工具类用于添加和删除包名到黑白名单。该功能在白名单未填充时不会执行拦截操作。

摘要由CSDN通过智能技术生成

展开 ![](https://img-home.csdnimg.cn/images/20240708095038.png)

 

## 

## **实现思路**

1、提供 [ContentProvider](https://so.csdn.net/so/search?q=ContentProvider&spm=1001.2101.3001.7020) 保存我需要添加安装白名单和卸载黑名单列表

2、找到安装、卸载应用的系统核心源码,

3、查询ContentProvider 获取安装白名单列表和卸载黑名单列表

4、根据列表拦截需要拦截的白名单以及黑名单列表并给出相应提示

说明：a.安装卸载的核心代码都在 PackageManagerService.java 中

b.其中手动点击 apk 调用安装代码在 PackageInstaller 中

## 需要修改的文件清单

> frameworks\\base\\packages\\PackageInstaller\\AndroidManifest.xml  
> frameworks\\base\\packages\\PackageInstaller\\src\\com\\android\\packageinstaller\\wear\\AppPkgListProvider.java  
> frameworks\\base\\packages\\PackageInstaller\\src\\com\\android\\packageinstaller\\wear\\[DBHelper](https://so.csdn.net/so/search?q=DBHelper&spm=1001.2101.3001.7020).java  
> frameworks\\base\\packages\\PackageInstaller\\src\\com\\android\\packageinstaller\\PackageInstallerActivity.java  
> frameworks\\base\\services\\core\\java\\com\\android\\server\\pm\\PackageManagerService.java  
>  

一、在 PackageInstaller 中增加 ContentProvider

**frameworks\\base\\packages\\PackageInstaller\\AndroidManifest.xml**

```XML
   <provider  android:name=".wear.AppPkgListProvider"
	          android:authorities="com.android.packageinstaller.app.provider"
	          android:exported="true" />
```

**frameworks\\base\\packages\\PackageInstaller\\src\\com\\android\\packageinstaller\\wear\\AppPkgListProvider.java**

```java
package com.android.packageinstaller.wear;
 
import android.content.ContentProvider;
import android.content.ContentValues;
import android.content.UriMatcher;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.net.Uri;
 
public class AppPkgListProvider extends ContentProvider {
    static UriMatcher matcher = new UriMatcher(UriMatcher.NO_MATCH);
	static String authorities = "com.android.packageinstaller.app.provider";
 
    static{  
        matcher.addURI(authorities, "install_app_whitelist", 0);  
        matcher.addURI(authorities, "uninstall_app_blacklist", 1);  
     }  
 
    DBHelper mDBHelper;
    SQLiteDatabase db;
 
    @Override
    public boolean onCreate() {
        mDBHelper = new DBHelper(getContext());
        return true;
    }
 
    @Override
    public Cursor query( Uri uri,  String[] projection,  String selection,  String[] selectionArgs,  String sortOrder) {
        String tableName=getTableName(uri);
        db = mDBHelper.getReadableDatabase();
        return db.query(tableName,
                projection,
                selection,
                selectionArgs,
                null,
                null,
                sortOrder);
    }
 
    @Override
    public String getType( Uri uri) {
        return null;
    }
 
    @Override
    public Uri insert( Uri uri,  ContentValues values) {
        String tableName=getTableName(uri);
        db = mDBHelper.getWritableDatabase();
        db.insertWithOnConflict(tableName, null, values,SQLiteDatabase.CONFLICT_REPLACE);
        db.close();
        return null;
    }
 
    @Override
    public int delete( Uri uri,  String selection,  String[] selectionArgs) {
        String tableName=getTableName(uri);
        db = mDBHelper.getWritableDatabase();
        int row = db.delete(tableName, selection, selectionArgs);
        db.close();
        return row;
    }
 
    @Override
    public int update( Uri uri,  ContentValues values,  String selection,  String[] selectionArgs) {
        return 0;
    }
 
    private String getTableName(Uri uri){
        String tableName="installapp_whitelist";
        int match = matcher.match(uri);  
        switch(match){
            case 0:
                tableName="installapp_whitelist";
                break;
            case 1:
                tableName="uninstallapp_blacklist";
                break;
            default:
                break;
        }
 
        return tableName;
    }
}




![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)
```

**frameworks\\base\\packages\\PackageInstaller\\src\\com\\android\\packageinstaller\\wear\\DBHelper.java**

```java
package com.android.packageinstaller.wear;
 
import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
 
public class DBHelper extends SQLiteOpenHelper {
    public DBHelper(Context context){
        super(context, "apppkglist.db", null, 1);
    }
 
 
    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE IF NOT EXISTS installapp_whitelist  ( pkg_name TEXT primary key not null,app_name TEXT  )"
        );
        db.execSQL("CREATE TABLE IF NOT EXISTS uninstallapp_blacklist  ( pkg_name TEXT primary key not null,app_name TEXT  )"
        );
    }
 
    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
    }
}




![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)
```

### 二、在 PackageInstallerActivity 中查询包名列表进行拦截

在包名清单中查询不到，则提示安装失败，不显示安装界面

**frameworks\\base\\packages\\PackageInstaller\\src\\com\\android\\packageinstaller\\PackageInstallerActivity.java**

```java
 /**
     * Check if it is allowed to install the package and initiate install if allowed. If not allowed
     * show the appropriate dialog.
     */
    private void checkIfAllowedAndInitiateInstall() {//
        // Check for install apps user restriction first.
        final int installAppsRestrictionSource = mUserManager.getUserRestrictionSource(
                UserManager.DISALLOW_INSTALL_APPS, Process.myUserHandle());
        if ((installAppsRestrictionSource & UserManager.RESTRICTION_SOURCE_SYSTEM) != 0) {
            showDialogInner(DLG_INSTALL_APPS_RESTRICTED_FOR_USER);
            return;
        } else if (installAppsRestrictionSource != UserManager.RESTRICTION_NOT_SET) {
            startActivity(new Intent(Settings.ACTION_SHOW_ADMIN_SUPPORT_DETAILS));
            finish();
            return;
        }
 
        //add for installer white list start 新增内容
        boolean caninstall =true;
        if(mPkgInfo.applicationInfo.packageName != null 
            && !isInstallerEnable(mPkgInfo.applicationInfo.packageName)){
            caninstall = false;  
        }
        if(!caninstall){
            Log.w(TAG, "caninstall "+caninstall);
            setPmResult(PackageManager.INSTALL_FAILED_INVALID_APK);
            Toast.makeText(this, R.string.install_failed_invalid_apk, Toast.LENGTH_LONG).show();
            finish();
            return;
        }
        //add for installer white list end 新增内容
 
        if (mAllowUnknownSources || !isInstallRequestFromUnknownSource(getIntent())) {
            initiateInstall();
        } else {
            // Check for unknown sources restrictions.
            final int unknownSourcesRestrictionSource = mUserManager.getUserRestrictionSource(
                    UserManager.DISALLOW_INSTALL_UNKNOWN_SOURCES, Process.myUserHandle());
            final int unknownSourcesGlobalRestrictionSource = mUserManager.getUserRestrictionSource(
                    UserManager.DISALLOW_INSTALL_UNKNOWN_SOURCES_GLOBALLY, Process.myUserHandle());
            final int systemRestriction = UserManager.RESTRICTION_SOURCE_SYSTEM
                    & (unknownSourcesRestrictionSource | unknownSourcesGlobalRestrictionSource);
            if (systemRestriction != 0) {
                showDialogInner(DLG_UNKNOWN_SOURCES_RESTRICTED_FOR_USER);
            } else if (unknownSourcesRestrictionSource != UserManager.RESTRICTION_NOT_SET) {
                startAdminSupportDetailsActivity(UserManager.DISALLOW_INSTALL_UNKNOWN_SOURCES);
            } else if (unknownSourcesGlobalRestrictionSource != UserManager.RESTRICTION_NOT_SET) {
                startAdminSupportDetailsActivity(
                        UserManager.DISALLOW_INSTALL_UNKNOWN_SOURCES_GLOBALLY);
            } else {
                handleUnknownSources();
            }
        }
    }
 
    //add for installer white list start  新增方法
    private boolean isInstallerEnable(String packagename){
        Log.i(TAG, "isInstallerEnable packagename  "+packagename);
        boolean flag=true;
        if(TextUtils.isEmpty(packagename)){
            return flag;
        }
       
        try{
 			Uri mUri = Uri.parse("content://com.android.packageinstaller.app.provider/install_app_whitelist");
            Cursor c = getContentResolver().query(mUri, null, null, null, null);
            if(c == null){
                Log.w(TAG, "isInstallerEnable "+mUri+" no exists ");
                return flag;
            }
            if(c.getCount()!=0){
                flag=false;
                while(c.moveToNext()){
                    String pkgname=c.getString(c.getColumnIndex("pkg_name"));
                    Log.i(TAG, "isInstallerEnable c.moveToNext() "+pkgname);
                    if(packagename.equals(pkgname)){
                        flag=true;
                        break;
                    }
                }
           
            }else{
                Log.i(TAG, "isInstallerEnable no whiltelist ");
            }
            c.close();
            }catch(Exception e){
                Log.e(TAG, "isInstallerEnable query  Exception",e);
                flag=true;
            }
        return flag;
    }
    //20180503  add for installer white list end
 


 

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)
```

### 三、在 PackageManagerService 类中拦截安装

[adb](https://so.csdn.net/so/search?q=adb&spm=1001.2101.3001.7020) 安装最终会走到 preparePackageLI()

**frameworks\\base\\services\\core\\java\\com\\android\\server\\pm\\PackageManagerService.java**

```java
    // add for installer white list start
	  private boolean isInstallerEnable(String packagename){
	      Log.i(TAG, "isInstallerEnable packagename  "+packagename);
	      boolean flag=true;
	      if(TextUtils.isEmpty(packagename)){
	          return flag;
	      }
 
	      try{
	      	  Uri mUri = Uri.parse("content://com.android.packageinstaller.app.provider/install_app_whitelist");
	          Cursor c = mContext.getContentResolver().query(mUri, null, null, null, null);
	          if(c == null){
	              Log.w(TAG, "isInstallerEnable "+mUri+" no exists ");
	              return flag;
	          }
	          if(c.getCount()!=0){
	              flag=false;
	              while(c.moveToNext()){
	                  String pkgname=c.getString(c.getColumnIndex("pkg_name"));
	                  Log.i(TAG, "isInstallerEnable c.moveToNext() "+pkgname);
	                  if(packagename.equals(pkgname)){
	                      flag=true;
	                      break;
	                  }
	              }
	         
	          }else{
	              Log.i(TAG, "isInstallerEnable no whiltelist ");
	          }
	          c.close();
	          }catch(Exception e){
	              Log.e(TAG, "isInstallerEnable query  Exception",e);
	              flag=true;
	          }
	      return flag;
	  }
	  // add for installer white list end
 
	@GuardedBy("mInstallLock")
    private PrepareResult preparePackageLI(InstallArgs args, PackageInstalledInfo res)
            throws PrepareFailure {
        final int installFlags = args.installFlags;
        final String installerPackageName = args.installerPackageName;
        final String volumeUuid = args.volumeUuid;
        final File tmpPackageFile = new File(args.getCodePath());
        final boolean onExternal = args.volumeUuid != null;
		......
 
		
          //add for installer white list start
	      boolean caninstall =true;
	      Log.i(TAG, "installPackageLI pkg.packageName "+pkg.packageName);
	      if(pkg.packageName != null && !isInstallerEnable(pkg.packageName)){
	          caninstall = false;
	      }
	      if(!caninstall){
	          // Toast.makeText(mContext, R.string.install_error, Toast.LENGTH_LONG).show();
	          //res.returnCode = PackageManager.INSTALL_FAILED_INVALID_APK;
	          throw new PrepareFailure(PackageManager.INSTALL_FAILED_INVALID_APK,
	                              "Package " + pkg.packageName + " is a forbidden app. "
	                                      + "Forbidden apps are not installs.");
	      }
	      //add for installer white list end
 
        // If package doesn't declare API override, mark that we have an install
        // time CPU ABI override.
        if (TextUtils.isEmpty(pkg.cpuAbiOverride)) {
            pkg.cpuAbiOverride = args.abiOverride;
        }
 
        String pkgName = res.name = pkg.packageName;
        if ((pkg.applicationInfo.flags & ApplicationInfo.FLAG_TEST_ONLY) != 0) {
            if ((installFlags & PackageManager.INSTALL_ALLOW_TEST) == 0) {
                throw new PrepareFailure(INSTALL_FAILED_TEST_ONLY, "installPackageLI");
            }
        }
	
		......
 
}




![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)
```

### 四、在 PackageManagerService 中拦截卸载

不论是 adb 卸载还是通过系统设置拖拽卸载最终都会走 deletePackageX()

```java
  //  add for uninstaller black list start
  private boolean isUnInstallerEnable(String packagename){
      Log.i(TAG, "isUnInstallerEnable packagename  "+packagename);
      boolean flag=true;
      if(TextUtils.isEmpty(packagename)){
          return flag;
      }
 
      try{
      	  Uri mUri = Uri.parse("content://com.android.packageinstaller.app.provider/uninstall_app_blacklist");
          Cursor c = mContext.getContentResolver().query(mUri, null,"pkg_name = ? ", new String[]{packagename}, null);
          if(c == null){
              Log.w(TAG, "isUnInstallerEnable "+mUri+" no exists ");
              return flag;
          }
          if(c.moveToFirst()){
              String pkgname=c.getString(c.getColumnIndex("pkg_name"));
              Log.i(TAG, "isUnInstallerEnable c.moveToFirst() "+pkgname);
              flag=false;
         
          }else{
              Log.i(TAG, "isUnInstallerEnable "+ packagename +" doesn't exists in the blacklist ");
          }
          c.close();
      }catch(Exception e){
          Log.e(TAG, "isUnInstallerEnable query  Exception",e);
          flag=true;
      }
      return flag;
  }
  //  add for uninstaller black list end
 
    /**
     *  This method is an internal method that could be get invoked either
     *  to delete an installed package or to clean up a failed installation.
     *  After deleting an installed package, a broadcast is sent to notify any
     *  listeners that the package has been removed. For cleaning up a failed
     *  installation, the broadcast is not necessary since the package's
     *  installation wouldn't have sent the initial broadcast either
     *  The key steps in deleting a package are
     *  deleting the package information in internal structures like mPackages,
     *  deleting the packages base directories through installd
     *  updating mSettings to reflect current status
     *  persisting settings for later use
     *  sending a broadcast if necessary
     */
    public int deletePackageX(String packageName, long versionCode, int userId, int deleteFlags) {
        final PackageRemovedInfo info = new PackageRemovedInfo(this);
        final boolean res;
 
        final int removeUser = (deleteFlags & PackageManager.DELETE_ALL_USERS) != 0
                ? UserHandle.USER_ALL : userId;
 
        if (isPackageDeviceAdmin(packageName, removeUser)) {
            Slog.w(TAG, "Not removing package " + packageName + ": has active device admin");
            return PackageManager.DELETE_FAILED_DEVICE_POLICY_MANAGER;
        }
 
        //  add for uninstaller black list start
        if(!isUnInstallerEnable(packageName)){
            return PackageManager.DELETE_FAILED_INTERNAL_ERROR;
        }
        //  add for uninstaller black list end
 
        final PackageSetting uninstalledPs;
        final PackageSetting disabledSystemPs;
        final PackageParser.Package pkg;
 
        // for the uninstall-updates case and restricted profiles, remember the per-
        // user handle installed state
        int[] allUsers;
 
 
		......
 
}
 
 


  

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)
```

最后附带一个增、删包名的工具类 AppListHelper.java

```java
package cn.test.app.util;
 
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.text.TextUtils;
 
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
 
 
public class AppListHelper {
 
    private static AppListHelper appListHelper;
  
    private static final Uri INSTALL_APP_WHITELIST_URI=Uri.parse("content://com.android.packageinstaller.app.provider/install_app_whitelist");
    private static final Uri UNINSTALL_APP_BLACKLIST_URI=Uri.parse("content://com.android.packageinstaller.app.provider/uninstall_app_blacklist");
 
    public static AppListHelper getInstance(){
        if (appListHelper == null){
            appListHelper = new AppListHelper();
        }
        return appListHelper;
    }
 
    public void addInstallPackage(Context context, String number){
        ContentResolver contentResolver = context.getContentResolver();
        ContentValues newValues = new ContentValues();
        newValues.put("pkg_name", number);
        contentResolver.insert(INSTALL_APP_WHITELIST_URI, newValues);
    }
 
    public void removeInstallPackages(Context context, String number) {
        ContentResolver contentResolver = context.getContentResolver();
        contentResolver.delete(INSTALL_APP_WHITELIST_URI,
                "pkg_name = ?",
                new String[] {number});
    }
 
    public void addUnInstallPackage(Context context, String number){
        ContentResolver contentResolver = context.getContentResolver();
        ContentValues newValues = new ContentValues();
        newValues.put("pkg_name", number);
        contentResolver.insert(UNINSTALL_APP_BLACKLIST_URI, newValues);
 
    }
 
    public void removeUnInstallPackages(Context context, String number) {
        ContentResolver contentResolver = context.getContentResolver();
        contentResolver.delete(UNINSTALL_APP_BLACKLIST_URI,
                "pkg_name = ?",
                new String[] {number});
    }
 
}
 
 


  

![](https://csdnimg.cn/release/blogv2/dist/pc/img/newCodeMoreWhite.png)
```

说明：当前功能在没有添加一个白名单时 不会做任何拦截 只有当白名单存在至少有一个数据时 白名单才能生效