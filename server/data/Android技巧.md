### 反射
#android
通过反射可以调用无法获取到的对象方法eg：
```java
    /*
     * 通过反射调用EthernetManager
     * getAvailableInterfaces
     */
    public String[] getAvailableInterfaces(){
        String[] ifaces = null;
        try{
            Class<? extends EthernetManager> c = mEthManager.getClass();

            Method method = c.getMethod("getAvailableInterfaces");
            EthernetManager tempManager = mEthManager;
            method.setAccessible(true);

            Log.e(TAG,"get getAvailableInterfaces Method: " + (method != null));
            Object Values = method.invoke(tempManager);
            ifaces = (String[])Values;

        } catch (IllegalAccessException | InvocationTargetException | NoSuchMethodException e) {
            Log.e(TAG,"getDeclaredMethod: " + e.getMessage());
        }
        return ifaces;
    }
```

### 读写Settings Grobal
#android
```java
import android.provider.Settings;

private static final String SETTINGS_SATELLITE_NUM = "satellite_num";

//读：
Settings.Global.getInt(getContentResolver(),SETTINGS_SATELLITE_NUM)
//写：
Settings.Global.putInt(mContext.getContentResolver(),SETTINGS_SATELLITE_NUM,satelliteNum);
```

### 发送广播与广播接收器
#android
发送广播：
```java
    import android.content.Intent;

    private static final String FACTORY_SATELLITE_NUM = "com.mbw.testcase.satellite.num";

	Intent mobiiotIntent = new Intent(FACTORY_SATELLITE_NUM);
    context.sendBroadcast(mobiiotIntent);
```
接收广播：
```java
    import android.content.BroadcastReceiver;
    import android.content.Intent;
    import android.content.IntentFilter;
	import android.content.Context;

    private static final String FACTORY_SATELLITE_NUM = "com.mbw.testcase.satellite.num";
	private IntentFilter factoryFilter;

	factoryFilter = new IntentFilter(FACTORY_SATELLITE_NUM);
	mContext.registerReceiver(factoryReceiver, factoryFilter);

    BroadcastReceiver factoryReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            // 处理广播事件
            if (FACTORY_SATELLITE_NUM.equals(intent.getAction())) {
                Log.d(TAG, "GNSS FACTORY_SATELLITE_NUM GET");
                startGnssProvider();
            }
        }
    };
```
匿名广播，加Intentfilter
```java
        Context.registerReceiver(new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
				 //TODO
            }
        }, new IntentFilter(Intent.ACTION_BOOT_COMPLETED));
```

### 读取节点通用方法
#java
```java
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

public static String ReadFile(String sys_path) {
    String prop = "waiting";
    BufferedReader reader = null;
    try {
        reader = new BufferedReader(new FileReader(sys_path));
        prop = reader.readLine();
    } catch (IOException e) {
        e.printStackTrace();
    } finally {
        if(reader != null){
            try {
                reader.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    return prop;
}


public static boolean WriteFile(String sys_path,String value){
    try {
        BufferedWriter bufWriter = null;
        bufWriter = new BufferedWriter(new FileWriter(sys_path));
        bufWriter.write(value);
        bufWriter.close();
        return true;
    } catch (IOException e) {
        e.printStackTrace();
        android.util.Log.e(TAG, " writeFile error : " + sys_path+"  "+e.getMessage());
    }
    return false;

}
```

### 读写属性值
#android

```java
import android.os.SystemProperties;

//读：
SystemProperties.get("ro.debuggable")
//写：
SystemProperties.set("ro.debuggable", "1");
```

### Handle的详细用法
#android
**方式一： post(Runnable)**

创建一个工作线程，实现 Runnable 接口，实现 run 方法，处理耗时操作。
创建一个 handler，通过 handler.post/postDelay，投递创建的 Runnable，在 run 方法中进行更新 UI 操作。
```java
new Thread(new Runnable() {
   @Override
   public void run() {
       /**
          耗时操作
        */
      handler.post(new Runnable() {
          @Override
          public void run() {
              /**
                更新UI
               */
          }
      });
   }
 }).start();
```
**方式二： sendMessage(Message)**

创建一个工作线程，继承 Thread，重新 run 方法，处理耗时操作
创建一个 Message 对象，设置 what 标志及数据
通过 sendMessage 进行投递消息
创建一个handler，重写 handleMessage 方法，根据 msg.what 信息判断，接收对应的信息，再在这里更新 UI。
```java
private Handler handler = new Handler(){
    @Override
    public void handleMessage(Message msg) {
        super.handleMessage(msg);
        switch (msg.what) {      //判断标志位
            case 1:
                /**
                 获取数据，更新UI
                */
                break;
        }
    }
};
   
public class WorkThread extends Thread {
 
    @Override
    public void run() {
        super.run();
       /**
         耗时操作
        */
		//从全局池中返回一个message实例，避免多次创建message（如new Message）
        Message msg =Message.obtain();  
        msg.obj = data;
        msg.what=1;   //标志消息的标志
        handler.sendMessage(msg);
    }
    
}
   new WorkThread().start();
```

### 定时任务
#java
```
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public void test(){  
    ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);  
    AtomicInteger i = new AtomicInteger();  
  
    // 定义定时任务  
    Runnable task = () -> {  
        i.getAndIncrement();  
        if (i.get() > 5){  
            scheduler.shutdown();  
        }  
    };  
    // 延迟 2 秒后开始，每隔 3 秒执行一次  
    scheduler.scheduleAtFixedRate(task, 2, 3, TimeUnit.SECONDS);  
}
```


### 从Nvram中读值
#android
1.确定该值在meta工具中的目录位置
2.在CFG_file_info_custom.h 中确定该目录挂载的位置
```java
import vendor.mediatek.hardware.nvram.V1_0.INvram;
import com.android.internal.util.HexDump;

public void getDataFromNvram(String backCode, Context context){
    int i = 0;
    final int NVRAM_FLAG_OFFSET = 64;	//获取数据长度
    final int NVRAM_FLAG_DIGITS = 1;
    final String NVRAM_PRODUCT_INFO = "/vendor/nvdata/APCFG/APRDEB/WIFI";	//数据目录挂载的位置

    try{
        INvram agent = INvram.getService(); //get Nvram服务
        if(agent!=null){
            try{
                byte[] device_Code = backCode.getBytes("utf-8");
                String buff = agent.readFileByName(NVRAM_PRODUCT_INFO, NVRAM_FLAG_OFFSET+NVRAM_FLAG_DIGITS);

                Log.d("lzltest","buff : " + buff);
                // Remove \0 in the end
                byte[] pro_info = HexDump.hexStringToByteArray(buff.substring(0, buff.length() - 1));
                for (i = 0; i < NVRAM_FLAG_DIGITS; i++) {
                    pro_info[NVRAM_FLAG_OFFSET+i] = device_Code[i];
                }

                Log.d("lzltest","pro_info : " + pro_info);
                ArrayList<Byte> dataArray = new ArrayList<Byte>(NVRAM_FLAG_OFFSET+NVRAM_FLAG_DIGITS);
                for (i = 0; i < NVRAM_FLAG_OFFSET+NVRAM_FLAG_DIGITS; i++) {
                    dataArray.add(i, new Byte(pro_info[i]));
                }
                Log.d("lzltest","dataArray : " + dataArray); // 国家码下标[10][11]
                //err = agent.writeFileByNamevec(NVRAM_PRODUCT_INFO, NVRAM_FLAG_OFFSET+NVRAM_FLAG_DIGITS, dataArray); //data写入Nvram
            }catch (java.io.UnsupportedEncodingException e1) {
                android.util.Log.e("panhaoda1234", "e1 = "+e1);
            } catch (android.os.RemoteException e2) {
                android.util.Log.e("panhaoda1234", "e2 = "+e2);
            }
        }
    }catch(android.os.RemoteException e3){
        android.util.Log.e("panhaoda1234", "e3 = "+e3);
    }
}
```

### 获取字符串
#android
```java
 getString(R.string.settings)
 @string/appbar_scrolling_view_behavior
```
中文通过string.xml来获取，你只需要改动中文字符串的内容即可

### Toast提示
#toast
```java
import android.widget.Toast;

Toast.makeText(context, "Hello, this is a Toast!", Toast.LENGTH_SHORT).show();

自定义位置：
Toast toast = Toast.makeText(this, "Hello, centered Toast!", Toast.LENGTH_SHORT); 
toast.setGravity(Gravity.CENTER, 0, 0); // 居中显示 
toast.show();
```
- `context`：上下文，通常是 `this`（Activity）或 `getApplicationContext()`。
- `message`：要显示的文本内容。
- `duration`：显示时长，常用的有两种：
    - `Toast.LENGTH_SHORT`：短时间显示（约 2 秒）。
    - `Toast.LENGTH_LONG`：长时间显示（约 3.5 秒）。

