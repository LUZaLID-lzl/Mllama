------

### **overlay**配置

**overlay telephony相关配置** 
在路径vendor/partner_gms/overlay/gms_overlay_comms下 
默认配置的overlay路径为源码⽬录的packages,而通常使⽤的soc⼚商的packages,因此需要将相关的overlay路径重新换成soc⼚商的路径。创建如下⽬录，将默认packages下的资源⽂件copy到soc⼚商路径

```
vendor/partner_gms/overlay/gms_overlay_comms/vendor/mediatek/proprietary/packages
```



**修改默认壁纸**

创建路径

```
vendor/partner_gms/overlay/rvc_beta_overlay/frameworks/base/core/res/res/drawable-nodpi/
```

添加资源:
default_wallpaper.png



**nearby share相关overlay**

规范要求Nearby Share在快速设置中的第⼀或第⼆⻚GMS包中的overlay默认已经配置好了，但是该配置覆盖的是package下apps,而项⽬中默认使⽤的soc
⼚vendor/mediatek/proprietary/packages/下的apps
路径vendor/partner_gms/overlay/gms_overlay下 创建⽬录vendor/mediatek/proprietary/packages
将google默认在vendor/partner_gms/overlay/gms_overlay/packages中的overlay资源copy到新建⽬录下

若使⽤⾮overlay的⽅式修改: 可在systemui下⾃⾏修改

vendor/mediatek/proprietary/packages/apps/SystemUI/res/values/config.xml

```
<!-- The default tiles to display in QuickSettings -->
<string name="quick_settings_tiles_default" translatable="false">
wifi,bt,dnd,flashlight,rotation,battery,cell,airplane,cast,screenrecord,custom(com.google.android.gms/.nearby.sharing.SharingTileService)</string>
```



**配置gms_overlay_personal_safety**

由于使⽤的是MTKSettings而GMS包overlay的对象是原⽣的Settings所以overlay配置不会⽣效. 会导致以下fail

```
【模块】：
GtsPersonalSafetyTestCases  
【case】：
com.google.android.personalsafety.gts.SafetyHubTest#testSafetyHubIsAnEmergencyRoleHolder
com.google.android.personalsafety.gts.SafetyHubTest#testSafetyHubSetAsEmergencyIntentActionInSettings
com.google.android.personalsafety.gts.SafetyHubTest#testSafetyHubIsPreferredEmergencySosPackage
com.google.android.personalsafety.gts.SafetyHubTest#testSafetyHubIsTheEmergencyPackageNameInSettings
com.google.android.personalsafety.gts.SafetyHubTest#testSafetyHubSetAsEmergencyGestureSettingsPackage
```

修改: 在gms_overlay_personal_safety中增加⽬录vendor/mediatek/proprietary/gms_overlay_personal_safety⽬录中的packages复制到新建⽴的proprietary下



**配置aer**

签署aer协议的设备需要集成AER规范要求

```
PRODUCT_COPY_FILES += \$(ANDROID_PARTNER_GMS_HOME)/etc/sysconfig/aer.xml:system/etc/permissions/aer.xml
```

aer.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- AER Feature Flag -->
<config>
<feature name="com.google.android.feature.AER_OPTIMIZED" />
</config>
```



**配置EDLA**

签署edla协议的设备需要集成

```
PRODUCT_COPY_FILES += \$(ANDROID_PARTNER_GMS_HOME)/etc/sysconfig/services.edla.google.xml:system/etc/pe
rmissions/services.edla.google.xml
```

vendor/partner_gms/etc/sysconfig/services.edla.google.xml

```xml
<permissions> 
<!-- Affirm that the current device is an EDLA device. -->
<feature name="com.google.android.feature.ENTERPRISE_DEVICE" />
</permissions>
```



**AER-fully managed模式下的app列表缺少xxx应⽤**

在配置好全托管模式（fully managed）之后，检查默认的apps，缺少了xxx应⽤ 原因是xxx未加⼊⽩名单，全托管模式下被移除了
路径: vendor/partner_gms /overlay/GmsConfigOverlayCommon/res/values/vendor_required_apps_managed_device.xml中加入xxx应用



**Gms app overlay mtk apk**

vendor/partner_gms/apps/CalendarGoogle/Android.mk

```
LOCAL_OVERRIDES_PACKAGES := Calendar GoogleCalendarSyncAdapter MtkCalendar
```

vendor/partner_gms/apps/Messages

```
LOCAL_OVERRIDES_PACKAGES := messaging MtkMms
```

vendor/partner_gms/apps/DeskClockGoogle

```
LOCAL_OVERRIDES_PACKAGES := AlarmClock DeskClock MtkDeskClock
```



**默认Dialer配置**

方法一：如果使⽤MTK的Dailer,则需要覆盖掉Google的Dailer
/home/chengqian/t_dl36/sys/vendor/mediatek/proprietary/packages/apps/Dialer/Android.mk

```
LOCAL_OVERRIDES_PACKAGES := Dialer GoogleDialer
```

同时需要重新配置默认Dailer,否则会有CTS问题,下述CTS问题均为使⽤第三⽅Dailer后未配置默认Dailer导致

```
模块：CtsDevicePolicyManagerTestCases
case：com.android.cts.devicepolicy.MixedDeviceOwnerTest#testLockTask_defaultDialer
	 com.android.cts.devicepolicy.MixedProfileOwnerTest#testLockTask_defaultDialer
```

指定默认的Dailer为第三⽅Dailer:
vendor/partner_gms/overlay/GmsConfigOverlayComms/res/values/config.xml

```
<string name="config_defaultDialer" translatable="false">com.android.dialer</string>
```

vendor/partner_gms/overlay/gms_overlay_comms/vendor/mediatek/proprietary/packages/services/Telephony/res/values/config.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Class name for the default main Dialer activity [DO NOT TRANSLATE] -->
    <!-- <string name="dialer_default_class" translatable="false">com.google.android.dialer.extensions.GoogleDialtactsActivity</string> -->
    <!--指定默认的Dialer活动界⾯-->
    <string name="dialer_default_class" translatable="false">com.android.dialer.DialtactsActivity</string>

    <!-- Package name for the call-based number verification app -->
    <string name="platform_number_verification_package" translatable="false">com.google.android.gms</string>

    <!-- Flag to enable VVM3 visual voicemail -->
    <bool name="vvm3_enabled">true</bool>
</resources>
```

vendor/partner_gms / overlay/gms_overlay_comms/vendor/mediatek/proprietary/packages/services/Telecomm/res/values/config.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Class name for the default main Dialer activity [DO NOT TRANSLATE] -->
    <!-- <string name="dialer_default_class" translatable="false">com.google.android.dialer.extensions.GoogleDialtactsActivity</string> -->
    <string name="dialer_default_class" translatable="false">com.android.dialer.DialtactsActivity</string>
    <string name="incall_default_class" translatable="false">com.android.incallui.InCallServiceImpl</string>

    <!-- Determines if the granting of temporary location permission to the default dialer
         during an emergency call should be allowed. -->
    <bool name="grant_location_permission_enabled">true</bool>
</resources>
```

配置接听电话弹框不被阻⽌，否则会导致CTSV中Telecom Incoming Call Test测试项⽬测试时⽆拨号弹框
vendor/partner_gms / overlay/GmsConfigOverlayCommon/res/values/config.xml

```xml
    <!-- An array of packages for which notifications cannot be blocked. -->
    <string-array name="config_nonBlockableNotificationPackages" translatable="false">
        <item>com.google.android.setupwizard</item>
        <item>com.google.android.apps.restore</item>
        <item>com.google.android.dialer</item>
        <item>com.android.dialer</item>
    </string-array>

    <!-- An array of packages that can make sound on the ringer stream in priority-only DND mode -->
    <string-array name="config_priorityOnlyDndExemptPackages" translatable="false">
        <item>com.google.android.dialer</item>
        <item>com.android.server.telecom</item>
        <item>android</item>
        <item>com.android.systemui</item>
        <item>com.android.dialer</item>
    </string-array>
```

⽅法⼆：若⽆特殊需求直接预制GooglerDialer后将⽆CTS问题

```
PRODUCT_PACKAGES += \
	GoogleDialer\
```



**桌⾯布局**

GMS包提供了默认布局，针对不同的配置EEA等有不同的预制⽅案
vendor/partner_gms/apps/GmsSampleIntegration

```xml

<?xml version="1.0" encoding="utf-8"?>
<!-- Copyright (C) 2017 Google Inc. All Rights Reserved. -->
<favorites>
  <!-- Hotseat (We use the screen as the position of the item in the hotseat) -->
  <!-- Dialer Messaging Calendar Contacts Camera -->
  <favorite container="-101" screen="0" x="0" y="0" packageName="com.android.dialer" className="com.android.dialer.app.DialtactsActivity"/>
  <favorite container="-101" screen="1" x="1" y="0" packageName="com.google.android.apps.messaging" className="com.google.android.apps.messaging.ui.ConversationListActivity"/>
  <favorite container="-101" screen="2" x="2" y="0" packageName="com.google.android.calendar" className="com.android.calendar.event.LaunchInfoActivity"/>
  <favorite container="-101" screen="3" x="3" y="0" packageName="com.google.android.contacts" className="com.android.contacts.activities.PeopleActivity"/>
  <favorite container="-101" screen="4" x="4" y="0" packageName="com.mediatek.camera" className="com.mediatek.camera.CameraActivity"/>
  <!-- In Launcher3, workspaces extend infinitely to the right, incrementing from zero -->
  <!-- Google folder -->
  <!-- Google, Chrome, Gmail, Maps, YouTube, (Drive), (Music), (Movies), Duo, Photos -->
  <folder title="@string/google_folder_title" screen="0" x="0" y="4">
    <favorite packageName="com.google.android.googlequicksearchbox" className="com.google.android.googlequicksearchbox.SearchActivity"/>
    <favorite packageName="com.android.chrome" className="com.google.android.apps.chrome.Main"/>
    <favorite packageName="com.google.android.gm" className="com.google.android.gm.ConversationListActivityGmail"/>
    <favorite packageName="com.google.android.apps.maps" className="com.google.android.maps.MapsActivity"/>
    <favorite packageName="com.google.android.youtube" className="com.google.android.youtube.app.honeycomb.Shell$HomeActivity"/>
    <favorite packageName="com.google.android.apps.docs" className="com.google.android.apps.docs.app.NewMainProxyActivity"/>
    <favorite packageName="com.google.android.apps.youtube.music" className="com.google.android.apps.youtube.music.activities.MusicActivity"/>
    <favorite packageName="com.google.android.videos" className="com.google.android.youtube.videos.EntryPoint"/>
    <favorite packageName="com.google.android.apps.tachyon" className="com.google.android.apps.tachyon.MainActivity"/>
    <favorite packageName="com.google.android.apps.photos" className="com.google.android.apps.photos.home.HomeActivity"/>
  </folder>
  <favorite screen="0" x="4" y="4" packageName="com.android.vending" className="com.android.vending.AssetBrowserActivity"/>
</favorites>
```

若不使⽤GmsSampleIntegration则需要修改Launcher的布局
packages/apps/Launcher3/res/xml/default_workspace_4x4.xml

```
<?xml version="1.0" encoding="utf-8"?>

...
```

packages/apps/Launcher3/res/values/strings.xml

```
<string name="google_folder_title">Google</string>
```



**预制GoogleMessage**

build/make/tools/buildinfo.sh

```
echo "ro.com.google.acsa=true"
```



**配置Google Assistant**

frameworks/base / core/res/res/values/config.xml

```
<integer name="config_longPressOnHomeBehavior">2</integer>
```



**配置AndroidAutoStub**

Android10或者更⾼版本项⽬，如果⽀持TELEPHONY或⾮Low_Ram项⽬必须预置AndroidAuto app， 其他情况不预置 特别地，如果是A13及之后且⽀持AndroidAutoStub
需要定义android.software.activities_on_secondary_displays该feature值
**WLAN产品不可以预制AndroidAutoStub**
会导致下⾯模块case测试失败:

```
【模块】：GtsPlacementTestCases
【case】：com.google.android.placement.gts.InstalledAppsTest#testSystemAppsInstalled
```

在gms.mk中移除AndroidAutoStub预制



**配置personal_safety**

设备为wifionly时不⽀持personal_safety，配置后会导致下⾯case失败

```
【模块】：GtsPersonalSafetyTestCases
【case】：
com.google.android.personalsafety.gts.SafetyHubTest#testSafetyHubIsAnEmergencyRoleHolder
com.google.android.personalsafety.gts.SafetyHubTest#testSafetyHubSetAsEmergencyIntentActionIn
Settings
com.google.android.personalsafety.gts.SafetyHubTest#testSafetyHubIsPreferredEmergencySosPack
age
com.google.android.personalsafety.gts.SafetyHubTest#testSafetyHubIsTheEmergencyPackageName
InSettings
com.google.android.personalsafety.gts.SafetyHubTest#testSafetyHubSetAsEmergencyGestureSettin
gsPackage
```

personal_safety主要配置紧急联系应⽤,路径为vendor/partner_gms/products/personal_safety.mk

当设备为wifionly时，将gms.mk中的personal_sagety.mk的导⼊注释即可

```
# Personal Safety
$(call inherit-product, $(ANDROID_PARTNER_GMS_HOME)/products/personal_safety.mk)
```



**预制Turbo**

未预制会导致以下fail

```
【模块】：CtsDisplayTestCases 
【case】：android.display.cts.BrightnessTest#testSetAndGetPerDisplay
android.display.cts.BrightnessTest#testBrightnessSliderTracking
android.display.cts.BrightnessTest#testNoColorSampleData
android.display.cts.BrightnessTest#testGetDefaultCurve
android.display.cts.BrightnessTest#testSliderEventsReflectCurves
```



**下拉状态栏快速启动栏需要有扫码的⼊口**

GMS规范要求，Android 13起，在下拉状态栏的快速启动菜单，需要有扫码的⼊口，MADA条例详⻅ 附件图⽚
vendor/partner_gms /overlay/gms_overlay/vendor/mediatek/proprietary/packages/apps/SystemUI/res/values/config.xml
在下拉状态⼊口配置⽂件中添加qr_code_scanner

```
<string name="quick_settings_tiles_default" translatable="false"> 
wifi,bt,dnd,flashlight,rotation,battery,cell,airplane,night,screenrecord,custom(
com.google.android.gms/.nearby.sharing.SharingTileService),qr_code_scanner</string>
```

配置Qrcode功能
QrCodeActivity在MTK平台已经实现了,只需要配置包名类名
frameworks/base/core/res/res/values/config.xml

```
<string name="config_defaultQrCodeComponent">com.mediatek.camera/com.mediatek.camera.QrCodeActivity</string>
```

如果是展锐平台需要⾃⾏实现



**检测发现Gboard不是默认输⼊法**

⼀般这种问题是不使⽤LatinImeGoogle导致的.



**A13开始，如ram >= 4GB,强制预制ASI及Private compute此 2个apk，低于4G Ram则不预置（A12为强烈推荐）**

⼀般导致该规范不符合原因为修改了gms.mk中GMS optional application packages导致 需要预制:

```
AndroidSystemIntelligence_Features
```



**GoogleCalendarSyncAdapter**

预制了Google的Calendar⽆需预制该APP