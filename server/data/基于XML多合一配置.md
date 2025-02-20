
XML文件详情
vendor/odm/maidu/mobiiot/service/java/com/mobiiot/service/xml/sku_config.xml
```xml
eg:
    <!--XML中添加SKU后请在MobiiotManagerService中同样添加 -->
    <!--各模块返回值的对应关系 -->
    <!--nfc -->
        <!-- 0 -> 不支持 -->
        <!-- 1 -> 支持（屏下） 前NFC1 -->
        <!-- 2 -> 支持（双面） 前NFC1+后NFC1 -->
    <!--pogo-pin -->
        <!-- 1 -> 底部6pin -->
        <!-- 2 -> 底部6pin 背部8pin -->
    <!--各模块返回值的对应关系 -->
    <!-- SKU1A Conif -->
    <sku **id=**"SKU1A" pcb-**version=**"00000000" **type=**"WLAN" **gms=**"false" **memory=**"3+32">
        <hardware>
            <gps **supported=**"true"/><!-- GPS -->
            <bluetooth **supported=**"true"/><!-- 蓝牙 -->
            <esim **supported=**"false"/><!-- eSIM -->
            <sim **supported=**"false"/><!-- SIM -->
            <headphone-jack **supported=**"false"/><!-- 模拟耳机 -->
            <pogo-pin **model=**"1"/><!-- POGO PIN -->
            <wifi **supported=**"false"/><!-- Hyper WI-FI -->
            <nfc **supported=**"false" **model=**"0"/><!-- NFC（天线） -->
            <cpu **model=**"MT8781"/><!-- CPU -->
            <screen **model=**"6.745"/><!-- 主屏 -->
            <scanner **supported=**"false" **model=**""/><!-- 扫码头 -->
            <camera>
                <front>2M FF</front><!-- 前摄像头 -->
                <back>2M FF</back><!-- 后摄像头 -->
            </camera>
            <fingerprint **supported=**"false"/><!-- 指纹 -->
            <battery **capacity=**"5000mAh"/><!-- 电池 -->
            <speaker **model=**"2516"/><!-- 喇叭 -->
            <receiver **supported=**"false"/><!-- 听筒 -->
            <motor **supported=**"false"/><!-- 马达 -->
            <led **supported=**"true"/><!-- LED -->
            <sub-mic **supported=**"true"/><!-- SUB MIC -->
            <flashlight **supported=**"true"/><!-- 后闪光灯 -->
            <pl-sensor **supported=**"true"/><!-- P+L Sensor -->
            <g-sensor **supported=**"false"/><!-- G-Sensor -->
            <geomagnetic **supported=**"false"/><!-- 地磁 -->
            <hall-sensor **supported=**"false"/><!-- Hall- sensor -->
            <barometer **supported=**"false"/><!-- 气压计 -->
            <rfid **supported=**"false"/><!-- RFID模块 -->
            <beidou **supported=**"false"/><!-- 北斗模块 -->
            <button-battery-mcu-anti-tamper **supported=**"false"/><!-- 纽扣电池+MCU+防拆点 -->
            <psam-mcu **supported=**"false"/><!-- PSAM+MCU -->
            <super-capacitor **supported=**"false"/><!-- 超级电容 （电池切换） -->
            <rtc **supported=**"false"/><!-- RTC -->
        </hardware>

        <buttons>
            <power-button **supported=**"true"/><!-- 电源按键 -->
            <custom-button **supported=**"true"/><!-- 自定义按键 -->
            <volume-buttons **supported=**"false"/><!-- 音量加减键 -->
            <scan-buttons **supported=**"false"/><!-- 扫码键 -->
        </buttons>
    </sku>
```

开机时将XML文件push到/[system](http://192.168.4.31:8080/source/s?path=/system/&project=xlt671_u_sys_dev)/[etc](http://192.168.4.31:8080/source/s?path=/system/etc/&project=xlt671_u_sys_dev)/目录下
```
PRODUCT_COPY_FILES += $(VENDOR_MOBIIOT_HOME)/service/java/com/mobiiot/service/xml/sku_config.xml:$(TARGET_COPY_OUT_SYSTEM)/etc/sku_config.xml
```

开机后通过定制系统服务读取XML文件，并提供对应接口
vendor/odm/maidu/mobiiot/service/java/com/mobiiot/service/utils/SkuInfoConfiguration.java
vendor/odm/maidu/mobiiot/service/java/com/mobiiot/service/utils/SkuInfo.java
读取XML文件，根据tag获取信息：
```java
 public void readConfiguration() {
        try {
            File xmlFile = new File(configFileName);
            InputStream is = new FileInputStream(xmlFile);

            DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
            DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
            Document doc = dBuilder.parse(is);

            doc.getDocumentElement().normalize();

            NodeList skuNodes = doc.getElementsByTagName("sku");
            for (int i = 0; i < skuNodes.getLength(); i++) {
                Node node = skuNodes.item(i);
                if (node.getNodeType() == Node.ELEMENT_NODE) {
                    Element skuElement = (Element) node;
                    SkuInfo skuInfo = parseSkuInfo(skuElement);
                    skuInfoList.add(skuInfo);
                }
            }
            is.close();
        } catch (Exception e) {
            Log.e(TAG, "Error reading XML configuration from system/etc: " + e.getMessage());
        }
    }
    private SkuInfo parseSkuInfo(Element skuElement) {
        SkuInfo skuInfo = new SkuInfo();

        // 解析基本信息
        skuInfo.setId(getAttributeOrDefault(skuElement, "id", "none"));
        skuInfo.setPcbVersion(getAttributeOrDefault(skuElement, "pcb-version", "none"));
        skuInfo.setType(getAttributeOrDefault(skuElement, "type", "none"));
        skuInfo.setGms(Boolean.parseBoolean(skuElement.getAttribute("gms")));
        skuInfo.setMemory(getAttributeOrDefault(skuElement, "memory", "none"));

        // 解析hardware部分
        Element hardwareElement = (Element) skuElement.getElementsByTagName("hardware").item(0);
        if (hardwareElement != null) {
            parseHardwareInfo(hardwareElement, skuInfo);
        }

        // 解析buttons部分
        Element buttonsElement = (Element) skuElement.getElementsByTagName("buttons").item(0);
        if (buttonsElement != null) {
            parseButtonsInfo(buttonsElement, skuInfo);
        }

        return skuInfo;
    }
```

