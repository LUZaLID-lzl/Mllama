### 概述
launcher3、systemui(此应用在frameworks/base/packages下)、setttings
- packages/apps 目录是google原生的应用
- vendor/mediatek/proprietary/packages/apps 目录是mediatek从google的应用分支拉的一个新分支，进行额外功能的开发，或是根据芯片平台进行适配

**针对google patch的情况**，packages/apps下的应用是可以直接进行合入的，而vendor/mediatek下的应用，mtk在收到google patch后会自己整合，然后释放mtk patch给我们进行合入

### 应用差异
launcher3，mtk修改了部分逻辑文件以及资源文件，另外两个应用不仅改动了逻辑，还有新功能的添加
#### Launcher3:
![[../../../resource/Pasted image 20241225100611.png]]
#### SystemUI:
![[../../../resource/Pasted image 20241225101121.png]]

#### Settings:
![[../../../resource/Pasted image 20241225101235.png]]