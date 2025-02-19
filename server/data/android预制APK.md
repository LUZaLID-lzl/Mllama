# Android系统预制APK(不可卸载)

1. 第一步：在 “/vendor/.../packages/apps” 目录下创建一个对应名称的文件夹。

2. 将所需apk放入文件夹中

3. 编辑 Android.mk ：
	
``` 
   LOCAL_PATH := $(call my-dir)
        include $(CLEAR_VARS)
         \# Module name should match apk name to be installed.

   ​     \#设置apk的名字,XXX为apk名称
   ​      LOCAL_MODULE := XXX
   ​      LOCAL_SRC_FILES := $(LOCAL_MODULE).apk   
   ​      LOCAL_MODULE_TAGS := optional
   ​      LOCAL_MODULE_CLASS := APPS
   ​      LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)

   ​     \#签名方式，如果是platform，代表签名成系统软件, 如果还是PRESIGND，表示用的是apk原本的签名。
   ​      LOCAL_CERTIFICATE := platform
   
		 \#关闭应用的dex优化
		 LOCAL_DEX_PREOPT := false
   ​     \#将apk编进“/system/priv-app/目录”，如果为false，或者不加这句话，就会编进“/system/app” 目录, 二者区别在于前者的权限要高于  后者
   ​     LOCAL_PRIVILEGED_MODULE := true

   ​    \#（如果 LOCAL_MULTILIB 是32，意思是编译出32位的lib库，64异曲同工，如果是both，代表编译出两种库文件， 当然，首先要解压  apk，看看lib库是32的还是64的。 另外，如果手机系统是64位的，而lib库是32位的，则需要在  “/frameworks/base/services/core/java/com/android/serve/pm/PackageManagerService.java”  中进行配置， lineNumber ： 6221）
   ​     LOCAL_MULTILIB := 32  
   ​     include $(BUILD_PREBUILT)

     补充：　LOCAL_OVERRIDES_PACKAGES := Calculator　  #覆盖掉之前有的一个apk，名字叫Calculator
```

4. 在 /device/平台/.../项目目录下找到相应的版本，打开其中的 “项目名.mk” 文件， 添加：PRODUCT_PACKAGES += XXX





LOCAL_MODULE_PATH := $(TARGET_OUT_DATA_APPS)

// Android.bp

android_app {
    name: "your_module_name",
    srcs: ["your_source_files"],
    installable: true,
    dir: "data/app",  // 安装路径
}
