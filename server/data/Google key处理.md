### 1.客户提供TAC码
项目初期，由SPL向客户申请TAC码
大致内容如图所示(TAC: 35153293)：
![[../../../resource/Pasted image 20241202192257.png]]
### 2.TAC码生成Device_id.txt
拿到TAC码之后，根据内容生成device_id.txt文件
Device IDs不能重復 用於區分各設備，諮詢過3PL，此ID不必须是IMEI，也可以是SN，确保唯一性，我們一般使用TAC（8位）+（中間六位，和申請數量相關）+校驗位（1位）用工具生成
工具位置：[http://192.168.4.2:8090/pages/viewpage.action?pageId=27297341]()
![[../../../resource/屏幕截图 2024-12-02 193104.png]]
全部填写完成后，生成即可

### 3.提交Device_id.txt以及项目信息向3PL申请GoogleKey
![[../../../resource/Pasted image 20241202193302.png]]

### 4.拿到gpg文件进行解密
申请下来后，我们会得到一个pgp后缀的文件，需要进行解密才能进行下一步
![[../../../resource/Pasted image 20241202193358.png]]


### 5.解密后的压缩包上传至瓶卜OSS网站

### 6.GoogleKey写入及验证
