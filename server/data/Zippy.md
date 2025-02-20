### TODO LIST
> [!NOTE] TODO
> - 新增- 公历 / 农历日历，并可以添加日程提示

### FIX LIST

> [!NOTE] FIX
> - 更换背景颜色 渐变颜色背景新增4种主题样式 pikachu - bulbasaur - squirtle - mew

### 开发规范
#### 侧边栏添加新条目
1：drawer_menu.xml中加入新的item
```xml
<item  
    android:id="@+id/nav_calorie"  
    android:icon="@drawable/ic_calorie"  
    android:title="@string/menu_calorie"/>
```

2：MainActivity的onNavigationItemSelected中加入对id的判断，点击后有哪些动作
```java
if (id == R.id.nav_subscriptions) {  
    loadFragment(new DeviceInfoFragment());  
}
```

3：在sidebarList目录下创建对应的文件夹，添加相应的Fragment文件
![[../resource/Pasted image 20241217150521.png]]

#### 新增其他主题
1：创建主题卡片背景颜色
参考drawable/bg_setting_card_background_pikaqiu.xml

2：提供至少4张透明背景的主题动画
参考：drawable/pikaqiu_1.png    默认256x256 px
并将这些图片扩展至drawable/home_display.png
添加完成后，修改ImageProcess的maxWidthNum和maxHeightNum

3：提供主题基准颜色
utils/ColorCalibration

4 ：在SparkView增加新粒子效果，粒子文件参考drawable/ic_spark.xml
com/luza/zippy/ui/views/SparkView.java
```java
switch (shardPerfenceSetting.getHomeTheme()){  
    case "pikachu":  
        setImageDrawable(ContextCompat.getDrawable(context, R.drawable.ic_spark));  
        break;  
    case "bulbasaur":  
        setImageDrawable(ContextCompat.getDrawable(context, R.drawable.ic_water_drop));  
        break;  
    default:  
        setImageDrawable(ContextCompat.getDrawable(context, R.drawable.ic_spark));  
        break;  
}
```

5：添加对应主题
values/themes.xml
一个是首页主题，一个是开机动画主题

PikachuTheme中的statusBarColor和navigationBarColor颜色在mainactivity中添加完毕后，从log中获取颜色  log-tag:"Captured colors"
```xml
<style name="PikachuTheme" parent="AppTheme">  
	<item name="android:statusBarColor">#EAE9E7</item>  
	<item name="android:navigationBarColor">#EAD58E</item>
    <item name="android:windowBackground">@drawable/home_gradient_background_pikaqiu</item>  
</style>  
  
<style name="PikachuSplashTheme" parent="Theme.AppCompat.Light.NoActionBar">  
    <item name="android:statusBarColor">#C8D127</item>  
    <item name="android:navigationBarColor">#969C38</item>  
    <item name="android:windowBackground">@drawable/bg_splash_background_pikaqiu</item>  
</style>
```

6：添加切换主题卡片：
com/luza/zippy/ui/sidebarList/settings/SettingsFragment.java
```java
private List<ThemeItem> getThemeList() {  
    return Arrays.asList(  
            new ThemeItem("Pokemon", "pikachu",  R.drawable.pikaqiu_2, R.drawable.bg_setting_card_background_pikaqiu),  
            new ThemeItem("Pokemon", "bulbasaur", R.drawable.bulbasaur_1, R.drawable.bg_setting_card_background_bulbasaur)  
    );  
}
```

7：在MainActivity中根据主题名字设置theme
com/luza/zippy/MainActivity.java
```java
// 根据保存的主题设置当前主题  
String currentTheme = shardPerfenceSetting.getHomeTheme();  
if ("pikachu".equals(currentTheme)) {  
    setTheme(R.style.PikachuTheme);  
} else if ("bulbasaur".equals(currentTheme)) {  
    setTheme(R.style.BulbasaurTheme);  
}
```

8：在HomeFragment中设置主题图片
com/luza/zippy/ui/fragments/HomeFragment.java
参考：
```java
int[] currentImages;  
shardPerfenceSetting.update();  
switch (shardPerfenceSetting.getHomeTheme()){  
    case "pikachu":  
        currentImages = pikachuImages;  
        break;  
    case "bulbasaur":  
        currentImages = bulbasaurImages;  
        break;  
    default:  
        currentImages = pikachuImages;  
        break;  
}
```

9：在Util中做好兼容
com/luza/zippy/ui/sidebarList/settings/Util.java
```java
public void updateTheme(Activity activity) {  
    ShardPerfenceSetting shardPerfenceSetting = new ShardPerfenceSetting(activity.getBaseContext());  
    String theme = shardPerfenceSetting.getHomeTheme();  
    Log.d("liziluo","activity.getComponentName() : " + activity.getComponentName());  
    if (activity.getComponentName().toString().contains("SplashActivity")){  
        switch (theme) {  
            case "pikachu":  
                activity.setTheme(R.style.PikachuSplashTheme);  
                break;  
            case "bulbasaur":  
                activity.setTheme(R.style.BulbasaurSplashTheme);  
                break;  
            default:  
        }  
    }  
}
```

10：在com/luza/zippy/setting/ShardPerfenceSetting.java中做好注释，主题的名字等

#### 新增ShardPerfence条目
1：setting/ShardPerfenceSetting中添加对应的参数
```java
private String language;
public String getLanguage() {  
    return this.language;  
}  
  
public void setLanguage(String language) {  
    this.language = language;  
}

public void getSharedPreferences(){  
    sharedPreferences = mContext.getSharedPreferences(PREF_NAME, mContext.MODE_PRIVATE);  
    setLanguage(sharedPreferences.getString("language", "en"));  
}

public void logToString() {  
    String log =  "ShardPerfenceSetting{" +  
            "language='" + language + '\'' 
            '}';  
    android.util.Log.d(TAG,log);  
}
```

2：读写ShardPerfence通过获取ShardPerfenceSetting对象

### 其他信息
#### 待办导入格式
| 标题   | 待办事项   |
| ---- | ------ |
| 111  | 2222   |
| ewrz | asdd   |
| sdsa | gfgdfg |
| fdg  | asdasd |
#### 主题颜色对应
| 主题        | 颜色     |
| --------- | ------ |
| pikachu   | FFC603 |
| bulbasaur | 13B4FC |
| squirtle  | 5CB860 |
| mew       | FBA7BD |
| karsa     | CE5CE4 |
| capoo     | 21FAD7 |
| maple     | D8420C |
| winter    | C6DEDD |
|           |        |



### 附件
![[../resource/Pasted image 20241223142443.png]]