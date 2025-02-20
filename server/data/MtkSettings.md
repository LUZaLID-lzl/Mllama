#### 修改WIFI MAC ADDRESS
AbstractWifiMacAddressPreferenceController
updateConnectivity()中mWifiMacAddress.setSummary

#### 修改BLUETOOTH ADDRESS
AbstractBluetoothAddressPreferenceController
updateConnectivity()中mBtAddress.setSummary

#### 修改IMEI信息
1：IMEI显示信息
ImeiInfoPreferenceController
```
    private CharSequence getSummary(int simSlot) {
        final int phoneType = getPhoneType(simSlot);
        return phoneType == PHONE_TYPE_CDMA ? mTelephonyManager.getMeid(simSlot)
                : mTelephonyManager.getImei(simSlot);
    }
```

2：IMEI弹框中显示的值
ImeiInfoDialogFragment
```
ublic void setText(int viewId, CharSequence text) {
        final TextView textView = mRootView.findViewById(viewId);
        if (textView == null) {
            return;
        }
        if (TextUtils.isEmpty(text)) {
            text = getResources().getString(R.string.device_info_default);
        }
        else if (Arrays.binarySearch(sViewIdsInDigitFormat, viewId) >= 0) {
            text = PhoneNumberUtil.expandByTts(text);
        }
        textView.setText("111111");
    }
```

#### 修改指纹重命名字数限制
src/com/android/settings/biometrics/fingerprint/FingerprintSettings.java
```java
private static InputFilter[] getFilters() {
            InputFilter filter = new InputFilter() {
                @Override
                public CharSequence filter(CharSequence source, int start, int end,
                        Spanned dest, int dstart, int dend) {
                    for (int index = start; index < end; index++) {
                        final char c = source.charAt(index);
                        // KXMLSerializer does not allow these characters,
                        // see KXmlSerializer.java:162.
                        if (c < 0x20) {
                            return "";
                        }
                    }
                    return null;
                }
            };
            // [312464]Renames the set fingerprint limit 50 chars
            InputFilter numFilters = new InputFilter.LengthFilter(50);
            return new InputFilter[]{filter,numFilters};
```
