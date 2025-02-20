### CTA  ChangeList

当前changelist是基于MTK原生AOSP代码，打开CTA宏控

以下是必须满足的条件(此前送测时遇到的问题)：

1：所有应用程序的中文汉化和文本需求

2：当用户第一次连接到WLAN/蓝牙时，会弹出特殊的数据使用提示

3：针对CTA测试的分支代码需要打开对应的宏控

4：预制应用申请权限需明示



以下是送测时反馈的问题具体解决方案：

**1：WLAN，无相关权限配置，调用无提示WLAN开关可直接开启。**

Problem statement: 

需要在第三方apk调用打开WIFI时进行弹框提示

```
From 867a2a18d9cea04cd3236a67329ed39f6766fcfb Mon Sep 17 00:00:00 2001
From: liziluo <ziluo.li@mobiiot.com.cn>
Date: Thu, 02 Feb 2023 09:52:28 +0800
Subject: [PATCH] [177334][dl36]: for add wifi switch option

[Scope]:
frameworks/opt/net/wifi/service/java/com/android/server/wifi/WifiServiceImpl.java

[Cause Description]:

[Total Solution]:

[Testing Proposal]:

Change-Id: I135ce10acac66592956ce0befd7db25c0de10911
---

diff --git a/service/java/com/android/server/wifi/WifiServiceImpl.java b/service/java/com/android/server/wifi/WifiServiceImpl.java
index 20e82d8..4edd477 100644
--- a/service/java/com/android/server/wifi/WifiServiceImpl.java
+++ b/service/java/com/android/server/wifi/WifiServiceImpl.java
@@ -146,6 +146,7 @@
 import java.util.concurrent.CountDownLatch;
 import java.util.concurrent.Executor;
 import java.util.concurrent.TimeUnit;
+import android.os.SystemProperties;
 
 /**
  * WifiService handles remote WiFi operation requests by implementing
@@ -792,6 +793,26 @@
 
         mLog.info("setWifiEnabled package=% uid=% enable=%").c(packageName)
                 .c(Binder.getCallingUid()).c(enable).flush();
+        //[177334] CTA for add wifi switch option
+        if (isCtaSupported() && isPrivileged) {
+            final int wiFiEnabledState = getWifiEnabledState();
+            if (enable) {
+                if (wiFiEnabledState == WifiManager.WIFI_STATE_DISABLING
+                        || wiFiEnabledState == WifiManager.WIFI_STATE_DISABLED) {
+                    if (startConsentUi(packageName, Binder.getCallingUid(),
+                            WifiManager.ACTION_REQUEST_ENABLE)) {
+                        return true;
+                    }
+                }
+            } else if (wiFiEnabledState == WifiManager.WIFI_STATE_ENABLING
+                    || wiFiEnabledState == WifiManager.WIFI_STATE_ENABLED) {
+                if (startConsentUi(packageName, Binder.getCallingUid(),
+                    WifiManager.ACTION_REQUEST_DISABLE)) {
+                        return true;
+                }
+            }
+        }
+        //[177334] CTA for add wifi switch option
         long ident = Binder.clearCallingIdentity();
         try {
             if (!mSettingsStore.handleWifiToggled(enable)) {
@@ -810,6 +831,50 @@
         return true;
     }
 
+    //[177334] CTA for add wifi switch option start
+     private boolean isCtaSupported() {
+        final boolean featureSupported = 
+                SystemProperties.getInt("ro.vendor.mtk_mobile_management", 0) == 1;
+        final boolean disabled =
+                SystemProperties.getInt("persist.vendor.sys.disable.moms", 0) == 1;
+        return featureSupported && !disabled;
+    }
+
+
+    private boolean startConsentUi(String packageName, int callingUid, String intentAction) {
+        if (UserHandle.getAppId(callingUid) == Process.SYSTEM_UID) {
+            return false;
+        }
+        try {
+            // Validate the package only if we are going to use it
+            ApplicationInfo applicationInfo = mContext.getPackageManager()
+                    .getApplicationInfoAsUser(packageName,
+                            PackageManager.MATCH_DIRECT_BOOT_AUTO,
+                            UserHandle.getUserHandleForUid(callingUid));
+            if (applicationInfo.uid != callingUid) {
+                throw new SecurityException("Package " + packageName
+                        + " not in uid " + callingUid);
+            }
+
+
+            // Permission review mode, trigger a user prompt
+            long ident = Binder.clearCallingIdentity();
+            try {
+                Intent intent = new Intent(intentAction);
+                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK
+                        | Intent.FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS);
+                intent.putExtra(Intent.EXTRA_PACKAGE_NAME, packageName);
+                mContext.startActivity(intent);
+            } finally {
+                Binder.restoreCallingIdentity(ident);
+            }
+            return true;
+        } catch (PackageManager.NameNotFoundException e) {
+            throw new RemoteException(e.getMessage()).rethrowFromSystemServer();
+        }
+    }
+    //[177334] CTA for add wifi switch option end
+
     /**
      * see {@link WifiManager#getWifiState()}
      * @return One of {@link WifiManager#WIFI_STATE_DISABLED},

```

```
From 9d51b8ffd060b09d2c3bdea79daa2e86aa67e17a Mon Sep 17 00:00:00 2001
From: liziluo <ziluo.li@mobiiot.com.cn>
Date: Fri, 17 Feb 2023 14:36:00 +0800
Subject: [PATCH] [177334][dl36]: add wifi controller

[Scope]:
service/java/com/android/server/wifi/WifiServiceImpl.java

[Cause Description]:

[Total Solution]:

[Testing Proposal]:

Change-Id: Id035a922d02b767a758c661d9b511a9b3fa6a827
---

diff --git a/service/java/com/android/server/wifi/WifiServiceImpl.java b/service/java/com/android/server/wifi/WifiServiceImpl.java
index 4edd477..cd015d5 100644
--- a/service/java/com/android/server/wifi/WifiServiceImpl.java
+++ b/service/java/com/android/server/wifi/WifiServiceImpl.java
@@ -794,7 +794,7 @@
         mLog.info("setWifiEnabled package=% uid=% enable=%").c(packageName)
                 .c(Binder.getCallingUid()).c(enable).flush();
         //[177334] CTA for add wifi switch option
-        if (isCtaSupported() && isPrivileged) {
+        if (isCtaSupported() && !isPrivileged) {
             final int wiFiEnabledState = getWifiEnabledState();
             if (enable) {
                 if (wiFiEnabledState == WifiManager.WIFI_STATE_DISABLING

```



**2：6.0接口：定位、本地录音、拍照/摄像：提示选项有“仅限这一次”，对应的配置为“每次都询问”配置和提示描述有误，选择后再次调用短时间会记住**

Problem statement: 

实验室提供修改说明：“仅限这一次”改成“仅本次使用时允许”，“每次都询问”改成"每次使用时询问"

```
From b9f8a9559d5f98c5626a34f5e458c23414fb4e44 Mon Sep 17 00:00:00 2001
From: liziluo <ziluo.li@mobiiot.com.cn>
Date: Fri, 17 Feb 2023 13:59:20 +0800
Subject: [PATCH] [177334][dl36]: Change the character specification translation

[Scope]:

modified:   res/values-zh-rCN/strings.xml
	modified:   res/values-zh-rHK/strings.xml
	modified:   res/values-zh-rTW/strings.xml
	modified:   res/values/strings.xml

[Cause Description]:

[Total Solution]:

[Testing Proposal]:

Change-Id: Id04babdac47a7cea5ac0c0b91ff82de90a41eea7
---

diff --git a/res/values-zh-rCN/strings.xml b/res/values-zh-rCN/strings.xml
index b674f9f..def7d2b 100644
--- a/res/values-zh-rCN/strings.xml
+++ b/res/values-zh-rCN/strings.xml
@@ -111,7 +111,7 @@
     <string name="app_permission_button_allow_media_only" msgid="4093190111622941620">"仅允许访问媒体文件"</string>
     <string name="app_permission_button_allow_always" msgid="4313513946865105788">"始终允许"</string>
     <string name="app_permission_button_allow_foreground" msgid="2303741829613210541">"仅在使用该应用时允许"</string>
-    <string name="app_permission_button_ask" msgid="2757216269887794205">"每次都询问(请参考细分权限详情)"</string>
+    <string name="app_permission_button_ask" msgid="2757216269887794205">"每次使用时询问"</string>
     <string name="app_permission_button_deny" msgid="5716368368650638408">"拒绝"</string>
     <string name="app_permission_title" msgid="2453000050669052385">"<xliff:g id="PERM">%1$s</xliff:g>权限"</string>
     <string name="app_permission_header" msgid="228974007660007656">"是否允许这个应用访问<xliff:g id="PERM">%1$s</xliff:g>"</string>
diff --git a/res/values-zh-rHK/strings.xml b/res/values-zh-rHK/strings.xml
index 0c280b9..5f4c45d 100644
--- a/res/values-zh-rHK/strings.xml
+++ b/res/values-zh-rHK/strings.xml
@@ -42,7 +42,7 @@
     <string name="grant_dialog_button_allow" msgid="2137542756625939532">"允許"</string>
     <string name="grant_dialog_button_allow_always" msgid="4201473810650722162">"一律允許"</string>
     <string name="grant_dialog_button_allow_foreground" msgid="3921023528122697550">"使用應用程式時"</string>
-    <string name="grant_dialog_button_allow_one_time" msgid="3290372652702487431">"僅限這次(請參攷細分許可權詳情)"</string>
+    <string name="grant_dialog_button_allow_one_time" msgid="3290372652702487431">"僅本次使用時詢問"</string>
     <string name="grant_dialog_button_allow_background" msgid="3190568549032350790">"一律允許"</string>
     <string name="grant_dialog_button_allow_all_files" msgid="1581085085495813735">"允許管理所有檔案"</string>
     <string name="grant_dialog_button_allow_media_only" msgid="3516456055703710144">"允許存取媒體檔案"</string>
diff --git a/res/values-zh-rTW/strings.xml b/res/values-zh-rTW/strings.xml
index 5af246e..bfd613d 100644
--- a/res/values-zh-rTW/strings.xml
+++ b/res/values-zh-rTW/strings.xml
@@ -42,7 +42,7 @@
     <string name="grant_dialog_button_allow" msgid="2137542756625939532">"允許"</string>
     <string name="grant_dialog_button_allow_always" msgid="4201473810650722162">"一律允許"</string>
     <string name="grant_dialog_button_allow_foreground" msgid="3921023528122697550">"使用應用程式時"</string>
-    <string name="grant_dialog_button_allow_one_time" msgid="3290372652702487431">"僅允許這一次(請參攷細分許可權詳情)"</string>
+    <string name="grant_dialog_button_allow_one_time" msgid="3290372652702487431">"僅本次使用時詢問"</string>
     <string name="grant_dialog_button_allow_background" msgid="3190568549032350790">"一律允許"</string>
     <string name="grant_dialog_button_allow_all_files" msgid="1581085085495813735">"允許管理所有檔案"</string>
     <string name="grant_dialog_button_allow_media_only" msgid="3516456055703710144">"允許存取媒體檔案"</string>
diff --git a/res/values/strings.xml b/res/values/strings.xml
index 7339bea..f161506 100644
--- a/res/values/strings.xml
+++ b/res/values/strings.xml
@@ -107,7 +107,7 @@
     <string name="grant_dialog_button_allow_foreground">While using the app</string>
 
     <!-- Title for the dialog button to allow a permission grant temporarily in teh foreground. [CHAR LIMIT=60] -->
-    <string name="grant_dialog_button_allow_one_time">Only this time(Please refer to the details of subdivision authority)</string>
+    <string name="grant_dialog_button_allow_one_time">Ask for this use only</string>
 
     <!-- Title for the dialog button to allow a change from foreground to background permission grant. [CHAR LIMIT=60]  -->
     <string name="grant_dialog_button_allow_background">Allow all the time</string>

```



**3：定位，单项配置开关和总开关之间逻辑关系混乱，请确认配置是否以单项配置开关为准，若是请在总开关每次使用时询问中添加文字描述（文字描述为：请参考细分权限详情）**

Problem statement: 

在xml文件中修改字符串内容，添加"请参考细分权限详情"

```
From c40787f9369699b94dce4aa2a8c2420fee6b961d Mon Sep 17 00:00:00 2001
From: liziluo <ziluo.li@mobiiot.com.cn>
Date: Thu, 02 Feb 2023 14:14:46 +0800
Subject: [PATCH] [177334][dl36]: for Permission text description

[Scope]:
modified:   res/values-zh-rCN/strings.xml
modified:   res/values-zh-rHK/strings.xml
modified:   res/values/strings.xml

[Cause Description]:

[Total Solution]:

[Testing Proposal]:

Change-Id: I56c53da2dee6cdccc87c9a6bcd5bb6005374895e
---

diff --git a/res/values-zh-rCN/strings.xml b/res/values-zh-rCN/strings.xml
index e70337b..0d99ead 100644
--- a/res/values-zh-rCN/strings.xml
+++ b/res/values-zh-rCN/strings.xml
@@ -111,7 +111,7 @@
     <string name="app_permission_button_allow_media_only" msgid="4093190111622941620">"仅允许访问媒体文件"</string>
     <string name="app_permission_button_allow_always" msgid="4313513946865105788">"始终允许"</string>
     <string name="app_permission_button_allow_foreground" msgid="2303741829613210541">"仅在使用该应用时允许"</string>
-    <string name="app_permission_button_ask" msgid="2757216269887794205">"每次都询问"</string>
+    <string name="app_permission_button_ask" msgid="2757216269887794205">"每次都询问(请参考细分权限详情)"</string>
     <string name="app_permission_button_deny" msgid="5716368368650638408">"拒绝"</string>
     <string name="app_permission_title" msgid="2453000050669052385">"<xliff:g id="PERM">%1$s</xliff:g>权限"</string>
     <string name="app_permission_header" msgid="228974007660007656">"是否允许这个应用访问<xliff:g id="PERM">%1$s</xliff:g>"</string>
diff --git a/res/values-zh-rHK/strings.xml b/res/values-zh-rHK/strings.xml
index 7b1452f..63fd11a 100644
--- a/res/values-zh-rHK/strings.xml
+++ b/res/values-zh-rHK/strings.xml
@@ -42,7 +42,7 @@
     <string name="grant_dialog_button_allow" msgid="2137542756625939532">"允許"</string>
     <string name="grant_dialog_button_allow_always" msgid="4201473810650722162">"一律允許"</string>
     <string name="grant_dialog_button_allow_foreground" msgid="3921023528122697550">"使用應用程式時"</string>
-    <string name="grant_dialog_button_allow_one_time" msgid="3290372652702487431">"僅限這次"</string>
+    <string name="grant_dialog_button_allow_one_time" msgid="3290372652702487431">"僅限這次(請參攷細分許可權詳情)"</string>
     <string name="grant_dialog_button_allow_background" msgid="3190568549032350790">"一律允許"</string>
     <string name="grant_dialog_button_allow_all_files" msgid="1581085085495813735">"允許管理所有檔案"</string>
     <string name="grant_dialog_button_allow_media_only" msgid="3516456055703710144">"允許存取媒體檔案"</string>
diff --git a/res/values/strings.xml b/res/values/strings.xml
index bdeeb65..72bdba4 100644
--- a/res/values/strings.xml
+++ b/res/values/strings.xml
@@ -107,7 +107,7 @@
     <string name="grant_dialog_button_allow_foreground">While using the app</string>
 
     <!-- Title for the dialog button to allow a permission grant temporarily in teh foreground. [CHAR LIMIT=60] -->
-    <string name="grant_dialog_button_allow_one_time">Only this time</string>
+    <string name="grant_dialog_button_allow_one_time">Only this time(Please refer to the details of subdivision authority)</string>
 
     <!-- Title for the dialog button to allow a change from foreground to background permission grant. [CHAR LIMIT=60]  -->
     <string name="grant_dialog_button_allow_background">Allow all the time</string>

```



**4：多项内容无受控机制**

**4.3.1.1.7.2 WLAN网络连接开启、关闭的受控机制---无受控机制**
**4.3.1.2.1.1 定位功能受控机制---无受控机制**
**4.3.1.2.2 通话录音功能启动的受控机制---无受控机制**
**4.3.1.2.3 本地录音功能启动的受控机制---无受控机制**
**4.3.1.2.4 拍照/摄像功能启动的受控机制---无受控机制**
**4.3.1.3 操作系统的授权更新或非授权更新---未提供相关说明**
**4.4.1.3.2 NFC接口连接提示---提示有误**

Problem statement: 

开启受控机制的宏控

注意：MSSI编译的项目和非MSSI编译的项目有两套不同的宏控

MTK_WAPI_SUPPORT默认关闭

MSSI编译方式后多了两个属性

MSSI_MTK_CTA_SET = yes

MSSI_MTK_CTA_SUPPORT = yes

MSSI_MTK_MOBILE_MANAGEMENT = yes

MSSI_MTK_PRIVACY_PROTECTION_LOCK = yes

```
From ff456fb4c311b6c8de43c19e93d50ca4bdab9924 Mon Sep 17 00:00:00 2001
From: liziluo <ziluo.li@mobiiot.com.cn>
Date: Fri, 03 Feb 2023 13:57:09 +0800
Subject: [PATCH] [177334][dl36]: open CTA control

[Scope]:
device/mediatek/system/mssi_t_64_cn/SystemConfig.mk

[Cause Description]:

[Total Solution]:

[Testing Proposal]:

Change-Id: Iaca3945a1f4d9c424544b1d4cd0194a1db6c23c8
---

diff --git a/SystemConfig.mk b/SystemConfig.mk
index d2f2f82..ff49808 100644
--- a/SystemConfig.mk
+++ b/SystemConfig.mk
@@ -11,7 +11,7 @@
 MSSI_MTK_CARRIEREXPRESS_PACK = no
 MSSI_MTK_CONSYSLOGGER_SUPPORT = yes
 MSSI_MTK_CTA_SET = yes
-MSSI_MTK_CTA_SUPPORT = no
+MSSI_MTK_CTA_SUPPORT = yes
 MSSI_MTK_CTM_SUPPORT = no
 MSSI_MTK_DMC_SUPPORT = no
 MSSI_MTK_DURASPEED_ML_SUPPORT = no

```



**5：卡机引导明示为英文，需点确认后才能更改语言**

Problem statement: 

更改默认语言为中文

```
From 4f40341d024ca5f8ae3b1f74dffec9132d927b87 Mon Sep 17 00:00:00 2001
From: liziluo <ziluo.li@mobiiot.com.cn>
Date: Wed, 01 Feb 2023 16:59:08 +0800
Subject: [PATCH] [177334][dl36]: for set default language with chinese

[Scope]:
build/make/tools/buildinfo.sh

[Cause Description]:

[Total Solution]:

[Testing Proposal]:

Change-Id: I591cdae173d1bbb092784d65cb81554777778cbc
---

diff --git a/tools/buildinfo.sh b/tools/buildinfo.sh
index 6ca2e25..70c95ff 100755
--- a/tools/buildinfo.sh
+++ b/tools/buildinfo.sh
@@ -55,3 +55,10 @@
 #112025[chengqian] modify for client ID
 echo "ro.com.google.clientidbase=android-mobiwire"
 echo "# end build properties"
+
+#[177334] CTA for set default language with chinese
+echo "persist.sys.language=zh"
+echo "persist.sys.country=CN"
+echo "ro.product.locale.language=zh"
+echo "ro.product.locale.region=CN"
+#[177334] CTA for set default language with chinese
\ No newline at end of file

```



**6：通用业务功能：6.1.1.1.1 语音通话---该设备语音未默认开启免提通话**

Problem statement: 

接收与拨打电话时能够自动开启免提功能

```
From 55431abbf54aa2e277f390f48cd585b1753d38f7 Mon Sep 17 00:00:00 2001
From: liziluo <ziluo.li@mobiiot.com.cn>
Date: Thu, 09 Feb 2023 15:13:29 +0800
Subject: [PATCH] [177334][dl36]: set speaker as default1

[Scope]:

ProjectConfig.mk

[Cause Description]:

[Total Solution]:

[Testing Proposal]:

Change-Id: I4f1a9376ed3b118f1b14004aed62ae2279d7d43c
---

diff --git a/ProjectConfig.mk b/ProjectConfig.mk
index e515e24..8e87ab1 100644
--- a/ProjectConfig.mk
+++ b/ProjectConfig.mk
@@ -596,3 +596,6 @@
 DL_RECOVERY_FSTAB = yes
 #modify by lvjiahao for bsp api(power manage) 136700 2022-7-29
 PROJECT_IS_DL36 = yes
+
+#[177334]add for open speaker as default
+MTK_TB_APP_CALL_FORCE_SPEAKER_ON = yes
\ No newline at end of file

```

```
From 311e3057d61b0bc599fab2f374ba23668ceaa4ca Mon Sep 17 00:00:00 2001
From: liziluo <ziluo.li@mobiiot.com.cn>
Date: Thu, 09 Feb 2023 15:14:20 +0800
Subject: [PATCH] [177334][dl36]: set speaker as default2

[Scope]:
src/com/android/server/telecom/CallsManager.java

[Cause Description]:

[Total Solution]:

[Testing Proposal]:

Change-Id: I72e9d0e1bc37cf662629d0fb4f3d45db7cc7da04
---

diff --git a/src/com/android/server/telecom/CallsManager.java b/src/com/android/server/telecom/CallsManager.java
index ae21470..dd677ed 100755
--- a/src/com/android/server/telecom/CallsManager.java
+++ b/src/com/android/server/telecom/CallsManager.java
@@ -5744,7 +5744,10 @@
                     mCall.answer(mVideoState);
                     Log.w(this, "Duplicate answer request for call %s", mCall.getId());
                 }
-                if (isSpeakerphoneAutoEnabledForVideoCalls(mVideoState)) {
+
+                //[177334]add for open speaker as default
+                final boolean useSpeakerForTablet = isSpeakerphoneEnabledForTablet();
+                if (isSpeakerphoneAutoEnabledForVideoCalls(mVideoState)  || useSpeakerForTablet) {
                     mCall.setStartWithSpeakerphoneOn(true);
                 }
             }

```

