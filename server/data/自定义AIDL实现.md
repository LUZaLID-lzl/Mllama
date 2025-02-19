## 自定义AIDL

AIDL（Android Interface Definition Language）是一种 IDL 语言，用于生成可以在 Android 设备上两个进程之间进行进程间通信（IPC）的代码。 通过 AIDL，可以在一个进程中获取另一个进程的数据和调用其暴露出来的方法，从而满足进程间通信的需求。通常，暴露方法给其他应用进行调用的应用称为服务端，调用其他应用的方法的应用称为客户端，客户端通过绑定服务端的 Service 来进行交互。



根据需求，我们可以得到两种Services的方式:

1：创建系统服务来调用系统方法

2：作为service应用启动，成为系统应用，能够实现数据存储

目前根据需求，我们需要允许来自不同的客户端访问我的服务，并能够存储/取出数据，所以这里选择第二种实现方式

![image-20240103160548293](image-20240103160548293.png)

自定义AIDL架构：

AppOpsCtaDisplay为客户端应用，通过getservices获取系统服务同时调用系统方法

com/aidl放置AIDL的文件：IPermissionRecordService.aidl

PermissionDisplayServices为服务端应用，通过实现IPermissionRecordService的stub，调用addService将自己加入到系统服务中

整个架构通过android.bp文件进行管理，分别编译AppOpsCtaDisplay、PermissionDisplayServices两个应用，再通过filegroup让其他mk/bp文件可以调用到我们的AIDL文件

```bash
android_app {
    name: "PermissionDisplayServices",

    aidl: {
        local_include_dirs: ["com/cta/permissiondisplayservices/"],
        export_include_dirs: [
            "com/cta/permissiondisplayservices/",
        ],
    },
    srcs: [
        "PermissionDisplayServices/src/**/*.java",
        "com/cta/permissiondisplayservices/**/*.aidl",
        "com/cta/permissiondisplayservices/**/*.java",
        "PermissionDisplayServices/src/com/cta/permissiondisplayservices/PermissionRecordService.java"
    ],

    resource_dirs: [
        "PermissionDisplayServices/res",
    ],

    static_libs: [
        "android-support-v4",
        "android-support-v7-appcompat",
        "vendor.mediatek.hardware.netdagent-V1.0-java",
    ],

    libs: [
        "mediatek-framework",
        "mediatek-cta",
        "android-support-annotations",
        "mediatek-framework",
    ],
    manifest: "PermissionDisplayServices/AndroidManifest.xml",

    certificate: "platform",
    privileged: true,

    optimize: {
        proguard_flags_files: ["PermissionDisplayServices/proguard.flags"],
    },

    platform_apis: true,
    min_sdk_version: "21",
}

android_app {
    name: "AppOpsCtaDisplay",

    srcs: [
        "AppOpsCtaDisplay/src/**/*.java",
        "com/cta/permissiondisplayservices/**/*.aidl",
        "com/cta/permissiondisplayservices/**/*.java",
    ],

    aidl: {
        local_include_dirs: ["com/cta/permissiondisplayservices/"],
        export_include_dirs: [
            "com/cta/permissiondisplayservices/",
        ],
    },
    resource_dirs: [
        "AppOpsCtaDisplay/res",
    ],

    static_libs: [
        "android-support-v4",
        "android-support-v7-appcompat",
        "vendor.mediatek.hardware.netdagent-V1.0-java",
        "androidx-constraintlayout_constraintlayout",
    ],

    manifest: "AppOpsCtaDisplay/AndroidManifest.xml",
    certificate: "platform",

    system_ext_specific: true,
    privileged: true,


    optimize: {
        proguard_flags_files: ["AppOpsCtaDisplay/proguard.flags"],
    },

    platform_apis: true,

    min_sdk_version: "21",
}

filegroup {
    name: "cta_permission_service",
    srcs: [
        "com/cta/permissiondisplayservices/**/*.aidl",
        "com/cta/permissiondisplayservices/**/*.java",
    ],
}

```



#### 1：首先创建我们的AIDL文件

创建AIDL文件后放到com目录下，上述的bp文件中引用了aidl的目录

AIDL 文件可以分为两类。一类用来声明实现了 Parcelable 接口的数据类型，以供其他 AIDL 文件使用那些非默认支持的数据类型。还有一类是用来定义接口方法，声明要暴露哪些接口给客户端调用。

声明实现了 Parcelable 接口的数据类型的AIDL文件：
首先创建对应的java文件并实现Parcelable接口
AppOpsRecordData.java:

```java
package com.cta.permissiondisplayservices;

import android.os.Parcel;
import android.os.Parcelable;

public class AppOpsRecordData implements Parcelable{
    private String packageName;
    private String opsName;
    private String time;

    public AppOpsRecordData(String packageName, String opsName, String time) {
        this.packageName = packageName;
        this.opsName = opsName;
        this.time = time;
    }

    protected AppOpsRecordData(Parcel in) {
        packageName = in.readString();
        opsName = in.readString();
        time = in.readString();
    }

    public static final Creator<AppOpsRecordData> CREATOR = new Creator<AppOpsRecordData>() {
        @Override
        public AppOpsRecordData createFromParcel(Parcel in) {
            return new AppOpsRecordData(in);
        }

        @Override
        public AppOpsRecordData[] newArray(int size) {
            return new AppOpsRecordData[size];
        }
    };

    public String getPackageName() {
        return packageName;
    }

    public void setPackageName(String packageName) {
        this.packageName = packageName;
    }

    public String getOpsName() {
        return opsName;
    }

    public void setOpsName(String opsName) {
        this.opsName = opsName;
    }

    public String getTime() {
        return time;
    }

    public void setTime(String time) {
        this.time = time;
    }

    @Override
    public String toString() {
        return "AppOpsRecordData{" +
                "packageName='" + packageName + '\'' +
                ", opsName='" + opsName + '\'' +
                ", time='" + time + '\'' +
                '}';
    }

    @Override
    public int describeContents() {
        return 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeString(packageName);
        dest.writeString(opsName);
        dest.writeString(time);
    }
}

```

再创建对应的aidl文件：
AppOpsRecordData.aidl：

```aidl
package com.cta.permissiondisplayservices;

parcelable AppOpsRecordData;
```

创建完实现了 Parcelable 接口的文件，在后续我们可以直接调用

还需要创建定义接口方法的aidl：
IPermissionRecordService.aidl

```aidl
package com.cta.permissiondisplayservices;

import java.util.List;
import java.util.Map;
import com.cta.permissiondisplayservices.AppOpsRecordData;

// Declare any non-default types here with import statements

interface IPermissionRecordService {
    /**
     * Demonstrates some basic types that you can use as parameters
     * and return values in AIDL.
     */
    List<AppOpsRecordData> getPermissionRecord();

    boolean addPermissionRecord(String pkgName,String permissionName,String time);

}
```



### 2：实现对应接口

在系统编译时，会生成以 .aidl 文件命名的 .java 接口文件（例如，IPermissionRecordService.aidl 生成的文件名是 IPermissionRecordService.java），在进程间通信中真正起作用的就是该文件。
如要实现 AIDL 生成的接口，请实例化生成的 Binder 子类（例如，IPermissionRecordService.Stub），并实现继承自 AIDL 文件的方法。
以下是使用匿名内部类实现 IPermissionRecordService 接口的示例：
PermissionRecordService.java:

```java
    class PermissionRecordBinder extends IPermissionRecordService.Stub{
        @Override
        public List<AppOpsRecordData> getPermissionRecord() throws RemoteException {
            if (dataBaseManager == null) {
                initDataBase();
            }
            return dataBaseManager.getPermissionRecord();
        }

        @Override
        public boolean addPermissionRecord(String pkgName,String permissionName,String time) throws RemoteException {
            if (dataBaseManager == null) {
                initDataBase();
            }
            return dataBaseManager.addPermissionRecord(pkgName,permissionName,time);
        }
    }
```



### 3：成为系统服务

由于我们是作为APP成为系统服务，所以需要在AndroidManifest.xml中定义为系统应用，否则无法调用getservices等方法：

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
          xmlns:tools="http://schemas.android.com/tools"
          coreApp="true"
          android:sharedUserId="android.uid.system"
          package="com.cta.permissiondisplayservices">
```

通过指定android:sharedUserId="android.uid.system"可以将应用识别为系统应用，需要源码编译，编译过程中有签名验证，否则不会生效

然后在我们的服务启动时，将自己加入到系统服务中：
PermissionRecordService.java:

```java
import android.os.ServiceManager;

public class PermissionRecordService extends Service {
	private static final String TAG = "PermissionRecordService";
    private static final String CTA_PERMISSION_SERVICE = "cta_permission_service";
	
	public void initServices(){
        android.util.Log.d(TAG,"initServices: ");
        try{
            //ServiceManager.addService(CTA_PERMISSION_SERVICE,new ControlRecordBinder(),true);
            ServiceManager.addService(CTA_PERMISSION_SERVICE,new PermissionRecordBinder(),true);
        }catch(Exception e){
            android.util.Log.d(TAG,"Exception: " + e);
        }
        initDataBase();
    }
    
    ...
        
    class PermissionRecordBinder extends IPermissionRecordService.Stub{
        @Override
        public List<AppOpsRecordData> getPermissionRecord() throws RemoteException {
            if (dataBaseManager == null) {
                initDataBase();
            }
            return dataBaseManager.getPermissionRecord();
        }

        @Override
        public boolean addPermissionRecord(String pkgName,String permissionName,String time) throws RemoteException {
            if (dataBaseManager == null) {
                initDataBase();
            }
            return dataBaseManager.addPermissionRecord(pkgName,permissionName,time);
        }
    }
}
```

通过ServiceManager.addService将已经实现stub的PermissionRecordBinder加入到系统服务中，通过CTA_PERMISSION_SERVICE作为我们这个服务的tag，当其他应用需要调用这个服务时，也要将这个tag作为参数来调用（需要为CTA_PERMISSION_SERVICE加相关的selinux权限，否则会报错）。
到目前为止，我们已经实现了aidl文件，并在我们的app启动时，将自己加入到系统服务中，但是我们的应用不会自己启动，所以需要在开机过程中通过Intent将我们的APP启动

frameworks/base/services/java/com/android/server/SystemServer.java

```java
    mActivityManagerService.systemReady(() -> {
        Slog.i(TAG, "Making services ready");
        t.traceBegin("StartActivityManagerReadyPhase");
        mSystemServiceManager.startBootPhase(t, SystemService.PHASE_ACTIVITY_MANAGER_READY);

        ....

        /// add for cta PermissionDisplayService start
        t.traceBegin("PermissionDisplayService");
        try {
        startPermissionDisplayService(context);
        } catch (Throwable e) {
        reportWtf("starting PermissionDisplayService:", e);
        }
        t.traceEnd();
        /// add for cta  PermissionDisplayService end

        ...

    }

    /// add for cta PermissionDisplayService start
    private final void startPermissionDisplayService(Context context) {
        if ((SystemProperties.getInt("persist.vendor.sys.disable.moms", 0) != 1) &&
            (SystemProperties.getInt("ro.vendor.mtk_mobile_management", 0) == 1)) {
            Intent serviceIntent = new Intent("com.cta.permissiondisplayservices.START_SERVICE");
            serviceIntent.setClassName("com.cta.permissiondisplayservices",
                "com.cta.permissiondisplayservices.PermissionRecordService");
            context.startServiceAsUser(serviceIntent, UserHandle.SYSTEM);
        }
    }
    /// add for cta PermissionDisplayService end
```

在SystemServer.java中，当其他系统服务在被初始化时，将我们的服务也启动，这里是通过Intent的方式指定了我们的包名直接启动，然后APP启动后会在第一时间将自己addservices
到此我们的服务就已经成为系统服务了



### 4：客户端调用

现在我需要在AppOpsService.java中调用我们的服务

首先在frameworks/base的bp文件中引入我们的aidl文件：
frameworks/base/Android.bp

```java
java_defaults {
    name: "framework-minus-apex-defaults",
    defaults: ["framework-aidl-export-defaults"],
    srcs: [
        ":framework-non-updatable-sources",
        "core/java/**/*.logtags",
        ":mobiiot_system_service_src", // 208302 add by mawenyi for MobiIot System Service 20230726
  ++++++":cta_permission_service", 
    ],
    aidl: {
        generate_get_transaction_name: true,
        local_include_dirs: [
            "media/aidl",
        ],
        include_dirs: [
            "frameworks/av/aidl",
            "frameworks/native/libs/permission/aidl",
            "packages/modules/Connectivity/framework/aidl-export",
            "vendor/mobiiot/service/java", // 208302 add by mawenyi for MobiIot System Service 20230726
      ++++++":vendor/mediatek/proprietary/packages/apps/PermissionDisplay/com/cta/permissiondisplayservices",
        ],
    },
}
```

这样就可以在AppOpsService中直接import我们的IPermissionRecordService

然后获取binder对象后就可以直接调用aidl中方法了
frameworks/base/services/core/java/com/android/server/appop/AppOpsService.java

```java
import com.cta.permissiondisplayservices.IPermissionRecordService;

public class AppOpsService extends IAppOpsService.Stub {
    static final String TAG = "AppOps";
    
    //add for cta
    private static final String CTA_PERMISSION_SERVICE = "cta_permission_service";
    
    //add for cta
    private boolean addOpsCtaDisplay(String packageName,int code){
        boolean isAdd = false;
        String opsName = codeTrance(code);

        if (!opsName.equals("")) {
            android.util.Log.d("CTA_Permission","opsName: " + opsName + "   code:" + code);
            try{
            	//在这里获取自定义服务的binder对象
                IBinder ctaBinder = ServiceManager.getService(CTA_PERMISSION_SERVICE);
                IPermissionRecordService iPermissionRecordService = IPermissionRecordService.Stub.asInterface(ctaBinder);
                if (iPermissionRecordService == null) {
                    android.util.Log.d("CTA_Permission","iPermissionRecordService is null");
                }else{
                    Date currentDate = new Date();
                    // 使用 SimpleDateFormat 格式化时间
                    SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
                    String time = dateFormat.format(currentDate);
                    iPermissionRecordService.addPermissionRecord(packageName,opsName,time);
                }
            }catch(Exception e){
                isAdd = false;
            }
        }

        return isAdd;
    }
    //add for cta
}
```

参考文件：
resource/PermissionDisplay.zip


