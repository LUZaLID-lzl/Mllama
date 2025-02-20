### (OTA降级)使用新P-Sensor机器 OTA降级失败

[操作步骤]: 使用ECN后的新P-sensor机器OTA降级	"（OTA包使用的是1.01.08.20210506 版本）"
[问题背景]: 需求ECNOTA降级提示	" "

``` 
#### 由 [LiNanyang李南洋](http://192.168.3.78:8078/users/504) 更新于 [超过一年](http://192.168.3.78:8078/projects/memor-xk/activity?from=2021-02-25) 之前
- **状态** 从 *New* 变更为 *OnGoing*
- **指派给** 从 *LiNanyang李南洋* 变更为 *huangzhangbin黄章斌*
- **% 完成** 从 *0* 变更为 *50*
- **Reopen次数** 被设置为 *0*

hi,黄工:
目前mk的psensor信息存储在./sys/devices/virtual/sensor/m_als_misc/ps_info
当无psensor工作为空(字符串\0);
当为一供为:stk3311_p
二供为:ltr559_p
麻烦安排上层的同事帮忙加一下弹框,谢谢
```

获取不同P-sensor的物料信息，传给上层，用于判断机器是否ECN。ECN会提示降级后psensor不可以用，非ECN不会有提示



**当前代码逻辑 (部分)：**

在dl的systemupdate中选择文件后，会执行onstartcommond方法，当action不为空，根据action进行不同的操作。这个时候intent中的action = 4 = case SystemUpgradeUtils.CHECK_CONDTION_1ST，这时进行第一次 的安装包校验

**SystemUpgradeServices.java**
```java
switch(action) {
				case SystemUpgradeUtils.CHECK_CONDTION_1ST:   //Not available for DXU
					LogUtils.debugLog(SUB_TAG, "action = CHECK_CONDTION_1ST");
					checkPackageContent(mFile);
					break;
				case SystemUpgradeUtils.CHECK_CONDTION_2ND:   //Not available for DXU
					LogUtils.debugLog(SUB_TAG, "action = CHECK_CONDTION_2ND");
					

					/* Get the unzipped metadata temporary file (we don't want to unzip the file again */
					if(intent.hasExtra("metadata_tmp_filename")) {
						metadataFilename = intent.getExtras().getString("metadata_tmp_filename");
					} else {
						LogUtils.errorLog(SUB_TAG, "metadata_tmp_filename extra not present...");
					}						
					checkCondition2nd(mFile);
					break;
				case SystemUpgradeUtils.INSTALL:              //Not available for DXU
					LogUtils.debugLog(SUB_TAG, "action = INSTALL");
					LogUtils.debugLog(SUB_TAG, "Install File Path: " + mFile);
					install(mFile);
					break;
```

在ota升降级之前，会在CheckPackageContentTask对ota包进行各种校验，在校验metadata文件的时候获取psensor信息并进行判断 ,当v1 > v2 ,shouldUpdate = false，-> mErrorCode = 12

**CheckPackageContentTask.java**  

``` java
   String ps_info = readFile(PS_INFO_FILE);
   android.util.Log.i(SUB_TAG, "CheckPackageContentTask checkMetadataFile ps_info = " + ps_info);
   try {
   		Class<?> c = Class.forName("android.os.SystemProperties");
   		Method get = c.getMethod("get", String.class);
   		String incremental = (String) get.invoke(c,"ro.build.version.incremental"); 
   		android.util.Log.i(SUB_TAG, "CheckPackageContentTask checkMetadataFile incremental = " + incremental + ", value = " + value);
   		if ("ltr559_p".equals(ps_info)){//stk3311_p   二供ltr559_p
   			Long v1 = Long.parseLong(incremental);
   			Long v2 = Long.parseLong(value);
   			android.util.Log.i(SUB_TAG, "CheckPackageContentTask checkMetadataFile v1 = " + v1 + ", v2 = " + v2);
   			if (v1 > v2) {
   				shouldUpdate = false;
   			}
   		}
	}
	......
	if (!shouldUpdate) {
			mErrorCode = SystemUpgradeUtils.CheckConditionErrorIntent.ErrorCodes.ECN_DOWN_ERROR;
			return false;
	}
```

在onPostExecute中 ，进行mErrorCode的判断，当1100< mErrorCode < 1200,发送广播，并给intent携带参数。注释的地方是我加上去的，ota降级的时候的报错就是因为fail这个intent没有携带参数，导致接收的地方参数为空 ，后续创建File file = new File(filename)的时候报出空指针问题

```java
if (mErrorCode > SystemUpgradeUtils.CheckVersionWarningIntent.ErrorCodes.FIRST_WARNING_CODE &&
				mErrorCode < SystemUpgradeUtils.CheckVersionWarningIntent.ErrorCodes.LAST_WARNING_CODE) {
				if(mApplicationData.getThirdPartyUpdate() == true) {
					/* External updaters have to continue automatically */
					LogUtils.infoLog(SUB_TAG, "CheckVersionWarning, Third party update");
					Intent intent = new Intent(mContext, SystemUpgradeService.class);
					intent.putExtra("action", SystemUpgradeUtils.CHECK_CONDTION_2ND);
					intent.putExtra("path", mFile.getAbsolutePath());
					intent.putExtra("metadata_tmp_filename", mTxtFile.getAbsolutePath());
					mContext.startService(intent);
				} else {
					LogUtils.infoLog(SUB_TAG, "CheckVersionWarning");
					Intent versionWarning = new Intent(SystemUpgradeUtils.CheckVersionWarningIntent.Intent);
					versionWarning.putExtra("metadata_tmp_filename", mTxtFile.getAbsolutePath());
					versionWarning.putExtra(SystemUpgradeUtils.CheckVersionWarningIntent.ExtraErrorCode,mErrorCode);
					versionWarning.putExtra("isVersionWarning",true);
					mContext.sendBroadcast(versionWarning);
				}
			} else {
				LogUtils.errorLog(SUB_TAG, "CheckPackageContentTask Failed!");
				Intent fail = new Intent(SystemUpgradeUtils.CheckConditionErrorIntent.Intent);
	//             fail.putExtra("action", SystemUpgradeUtils.CHECK_CONDTION_2ND);
    //             fail.putExtra("path", mFile.getAbsolutePath());
    //             fail.putExtra("metadata_tmp_filename", mTxtFile.getAbsolutePath());
				fail.putExtra(SystemUpgradeUtils.CheckConditionErrorIntent.ExtraErrorCode,mErrorCode);
				mContext.sendBroadcast(fail);
			}
```

发出广播之后，接下来就是接收广播，这时errorCode = 12 ,并且触发showEcnDialogWarning 进行弹框警示,在点击弹框的确定按钮后，触发doUpdate，进行升降级

**UpdateActivity.java**

```java
				errorCode = intent.getExtras().getInt(SystemUpgradeUtils.CheckConditionErrorIntent.ExtraErrorCode);
                /*[70421][Check if is ECN psensor when in ota]huangzhangbin 20210301 begin*/
                if (errorCode == SystemUpgradeUtils.CheckConditionErrorIntent.ErrorCodes.ECN_DOWN_ERROR) {
                    int action_int = 0;
                    String mFile = null;
                    String metadataFilename = null;
                    if(intent.hasExtra("action")) 
                        action_int = intent.getExtras().getInt("action");
                    if(intent.hasExtra("path")) 
                        mFile = intent.getExtras().getString("path");
                    if(intent.hasExtra("metadata_tmp_filename")) 
                        metadataFilename = intent.getExtras().getString("metadata_tmp_filename");

                    showEcnDialogWarning(UpdateActivity.this, action_int, mFile, metadataFilename);
                    return;
                }
                /*[70421][Check if is ECN psensor when in ota]huangzhangbin 20210301 end*/
                
                ......
           
                private void showEcnDialogWarning(Context context, int action, String path, String metadata) {
                    new AlertDialog.Builder(context)
                    .setTitle(context.getResources().getString(R.string.system_update_check_warning))
                    .setMessage(context.getResources().getString(R.string.system_update_check_error_ecn_down_error))
                    .setPositiveButton(R.string.system_update_check_ok, new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialog, int which) {
                            doUpdate(action, path, metadata);
                            mStateMachine.processEvent(SmEvent.SERVICE_CHECK_OK);
                        }
                    })
                    .setNegativeButton(R.string.system_update_check_nok, new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialog, int whichButton) {
                            mStateMachine.processEvent(SmEvent.CHECK_FAILURE);
                            mStateMachine.processEvent(SmEvent.USER_CHOICE_OK);
                        }
                    })
                    .show();
        		}
        		
        		......
        		
        		private void doUpdate(int action, String path, String metadata) {
                    android.util.Log.i(SUB_TAG, "doUpdate action = " + action + ", path = " + path 
                + ", metadata = " + metadata + ", getThirdPartyUpdate = " + 		((ApplicationData)getApplicationContext()).getThirdPartyUpdate());
                    if(((ApplicationData)getApplicationContext()).getThirdPartyUpdate() == true) {
                        /* External updaters have to continue automatically */
                        LogUtils.infoLog(SUB_TAG, "Third party update");
                        Intent intent = new Intent(getApplicationContext(), SystemUpgradeService.class);
                        intent.putExtra("action", action);
                        intent.putExtra("path", path);
                        intent.putExtra("metadata_tmp_filename", metadata);
                        getApplicationContext().startService(intent);
                    } else {
                        /* The internal local update UI will proceed step by step */
                        LogUtils.infoLog(SUB_TAG, "Local update");
                        Intent verifyFinish = new Intent(SystemUpgradeUtils.CHECK_CONDITION_FINISH);
                        verifyFinish.putExtra("metadata_tmp_filename", metadata);
                        getApplicationContext().sendBroadcast(verifyFinish);
                    }
                }
```

