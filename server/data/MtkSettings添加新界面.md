
首先确定好需要添加的界面位置，并找到对应的xml文件，以MtkSettings/res/xml/network_provider_internet.xml为例：

#### 普通Preference

1：创建preference文件，在xml中添加

```java
package com.android.settings.network.ethernet;

import android.content.Context;
import android.util.AttributeSet;
import androidx.preference.Preference;
import com.android.settings.R;
import android.util.Log;

/**
 * EthernetSettingsPreference
 * [280597]There is no detailed setting menu after the device is connected to the Ethernet
 * add by liziluo
 * */
public class EthernetSettingsPreference extends Preference {

    public EthernetSettingsPreference(Context context, AttributeSet attrs) {
        super(context, attrs);
    }

    @Override
    public void onAttached() {
        super.onAttached();
    }

    @Override
    public void onDetached() {
        super.onDetached();
    }

}
```

```xml
    <com.android.settings.network.ethernet.EthernetSettingsPreference
        android:key="ethernet_settings"
        android:title="@string/provider_ethernet_settings"
        android:icon="@drawable/ic_ethernet_settings"
        settings:useAdminDisabledSummary="true"
        android:order="-6"
        android:fragment="com.android.settings.network.ethernet.EthernetSettings"/>
```

key是唯一标识符，后续逻辑处理部分会通过key获取到preference对象

fragment指向的文件即为逻辑处理部分



2：创建fragment文件，并在Androidmanifist中声明

```java
package com.android.settings.network.ethernet;

import android.app.Application;
import android.app.settings.SettingsEnums;
import android.content.Context;
import android.os.Bundle;
import android.telephony.SubscriptionManager;
import android.widget.Switch;
import androidx.preference.Preference;
import com.android.settings.R;
/**
 * Ethernet settings
 * [280597]There is no detailed setting menu after the device is connected to the Ethernet
 * add by liziluo
 * */
public class EthernetSettings extends SettingsPreferenceFragment
        implements OnMainSwitchChangeListener {

    @Override
    public void onCreate(Bundle bundle) {
        super.onCreate(bundle);
    }

    @Override
    public void onActivityCreated(Bundle savedInstanceState) {
        super.onActivityCreated(savedInstanceState);
        addPreferencesFromResource(R.xml.ethernet_settings);
    }

    @Override
    public void onResume() {
        super.onResume();
    }

    @Override
    public void onPause() {
        super.onPause();
    }

    @Override
    public void onSwitchChanged(Switch switchView, boolean isChecked) {
    }

    @Override
    public int getMetricsCategory() {
        return SettingsEnums.ETHERNET_SETTINGS;
    }

}

```

```xml
        <activity
            android:name="Settings$EthernetSettings"
            android:label="@string/provider_ethernet_settings"
            android:exported="true"
            android:icon="@drawable/ic_ethernet_settings">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.VOICE_LAUNCH" />
                <category android:name="com.android.settings.SHORTCUT" />
            </intent-filter>
        </activity>
```

fragment创建好后，通过addPreferencesFromResource来加载layout



3:创建layout文件

```xml
<PreferenceScreen
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:settings="http://schemas.android.com/apk/res-auto"
    android:title="@string/provider_ethernet_settings">

    <com.android.settings.network.ethernet.EthernetConfigPreference
        android:key="ethernet_config"
        android:title="@string/provider_ethernet"
        android:order="1"
        settings:controller="com.android.settings.network.ethernet.EthernetConfigPreferenceController"
        android:dialogTitle="@string/provider_ethernet"
        android:dialogLayout="@layout/ethernet_config_dialog"
        android:positiveButtonText="@string/provider_ethernet_confirm"
        android:negativeButtonText="@string/provider_ethernet_cancle"/>  

    <com.android.settings.network.ethernet.EthernetInformationPreference
        android:key="ethernet_information"
        android:title="@string/provider_ethernet_information"
        android:order="2"
        settings:controller="com.android.settings.network.ethernet.EthernetInformationPreferenceController"
        android:dialogTitle="@string/provider_ethernet_information"
        android:dialogLayout="@layout/ethernet_information_dialog" 
        android:positiveButtonText="@string/provider_ethernet_confirm"
        android:negativeButtonText="@string/provider_ethernet_cancle"/>   
</PreferenceScreen>
```

上图中添加了两个preference作为显示对象，并且作为弹出的界面：

#### 弹框Preference