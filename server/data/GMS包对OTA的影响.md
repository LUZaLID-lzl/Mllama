**GMS核心应用程序包版本大小对比：**

| 序号 | GMS core application packages    | A11  | A12  | A13      |
| :--: | -------------------------------- | ---- | ---- | -------- |
|  1   | AndroidPlatformServices          |      |      | 14.3 MB  |
|  2   | ConfigUpdater                    |      |      | 8.4 MB   |
|  3   | FamilyLinkParentalControls       |      |      | 41.5 kB  |
|  4   | GoogleExtShared                  |      |      | 16.9 kB  |
|  5   | GoogleFeedback                   |      |      | 650.4 kB |
|  6   | GoogleLocationHistory            |      |      | 49.9 kB  |
|  7   | GoogleOneTimeInitializer         |      |      | 192.9 kB |
|  8   | GooglePackageInstaller           |      |      | 3.2 MB   |
|  9   | GooglePartnerSetup               |      |      | 726.1 kB |
|  10  | GooglePrintRecommendationService |      |      | 135.2 kB |
|  11  | GoogleRestore                    |      |      | 11.9 MB  |
|  12  | GoogleServicesFramework          |      |      | 7.3 MB   |
|  13  | GoogleCalendarSyncAdapter        |      |      | 2.5 MB   |
|  14  | SpeechServicesByGoogle           |      |      | 74.6 MB  |
|  15  | GmsCore                          |      |      | 147.5 MB |
|  16  | Phonesky                         |      |      | 71.5 MB  |
|  17  | SetupWizard                      |      |      | 10.9 MB  |
|  18  | WebViewGoogle                    |      |      | 114.6 MB |
|  19  | Wellbeing                        |      |      | 20.6 MB  |
|      | Total                            |      |      | 489.3MB  |

**GMS强制应用程序包版本大小对比：**

| 序号 | GMS mandatory application packages | A11      | A12      | A13      |
| :--: | ---------------------------------- | -------- | -------- | -------- |
|  1   | Gmail2                             | 79.9 MB  | 96.0 MB  | 104.6 MB |
|  2   | GoogleContacts                     | 14.1 MB  | 16.8 MB  | 19.1 MB  |
|  3   | Maps                               | 84.6 MB  | 89.6 MB  | 98.3 MB  |
|  4   | Photos                             | 92.7 MB  | 95.8 MB  | 116.3 MB |
|  5   | YouTube                            | 81.7 MB  | 82.1 MB  | 99.4 MB  |
|  6   | YTMusic                            | 44.2 MB  | 48.9 MB  | 50.5 MB  |
|  7   | Velvet                             | 252.4 MB | 271.4 MB | 269.6 MB |
|  8   | Drive                              | 40.6 MB  | 47.5 MB  | 49.7 MB  |
|  9   | Chrome                             | 35.6 MB  | 34.9 MB  | 36.3 MB  |
|  10  | Duo  (only a11 a12)                | 72.4 MB  | 68.2 MB  | /        |
|  11  | Meet  (only a13)                   | /        | /        | 76.1 MB  |
|      | Total                              | 798.2MB  | 851.2MB  | 919.9MB  |

**GMS可选应用程序包版本大小对比：**

| 序号 | GMS optional application packages                    | A11      | A12      | A13      | override                                                  |      |
| :--: | ---------------------------------------------------- | -------- | -------- | -------- | --------------------------------------------------------- | ---- |
|  1   | AndroidSystemIntelligence_Features    (only a12 a13) | /        | 34.4 MB  | 38.9 MB  | /                                                         |      |
|  2   | CalendarGoogle                                       | 26.6 MB  | 28.5 MB  | 28.7 MB  | Calendar <br />GoogleCalendarSyncAdapter<br />MtkCalendar |      |
|  3   | DeskClockGoogle                                      | 9.1 MB   | 10.3 MB  | 11.2 MB  | /                                                         |      |
|  4   | LatinImeGoogle                                       | 74.7 MB  | 79.0 MB  | 70.5 MB  | LatinIME                                                  |      |
|  5   | TagGoogle                                            | 694.8 kB | 715.7 kB | 683.8 kB | Tag                                                       |      |
|  6   | talkback                                             | 27.1 MB  | 34.3 MB  | 35.6 MB  | /                                                         |      |
|  7   | Keep                                                 | 15.9 MB  | 17.2 MB  | 18.6 MB  | /                                                         |      |
|  8   | CalculatorGoogle                                     | 2.9 MB   | 3.2 MB   | 3.3 MB   | Calculator <br />ExactCalculator                          |      |
|      | Total                                                | 157MB    | 207.6MB  | 207.5MB  |                                                           |      |

[[../../系统问题梳理/A11->A13跨版本升级|A11->A13跨版本升级]]

**A11 A13android版本各分区对比（刷机后通过df -h查看,开机后运行时大小）：**

| TEST TYPE       | product | system | vendor |
| --------------- | ------- | ------ | ------ |
| A11 + GMS       | 1.7G    | 1.2G   | 310M   |
| A13 driver only | 43M     | 1.5G   | 366M   |
| A13 + GMS       | 2.2G    | 1.6G   | 349M   |

**各情况下super分区编译时的大小（编译时大小）**：

| TEST TYPE                                             | product    | system     | vendor    | super(product + system + vendor)    |
| ----------------------------------------------------- | ---------- | ---------- | --------- | ----------------------------------- |
| A13完整GMS包                                          | 2406494208 | 1760481280 | 424755200 | 4591730688--(4484112KB)--(4379.1MB) |
| A13GMS包去除可选应用                                  | 2199326720 | 1767440384 | 424755200 | 4391522304--(4288596KB)--(4189MB)   |
| A13GMS包去除可选应用，<br />并将强制应用程序替换成A12 | 2152914944 | 1776119808 | 424755200 | 4353789952--(4251748KB)--(4152.1MB) |

当前A13 super分区需要定义的大小为(与A11保持一致)：4294967296--(4194304KB)--(4096MB)

也就是说当前A13 super分区想要对齐A11，不仅需要去除GMS包中的可选应用，同时将强制应用程序替换成A12，这时离对齐A11super分区还差

4152.1 - 4096 = 56.1MB



综上所诉，目前a11想要通过ota升级到a13，且a13需要通过GMS认证，当前情况无法满足。



后续措施：

1：精简应用，去已经预制的system应用下删除一些资源文件

2：看看能否将system下的应用放到data分区下，减少super的大小

3：问google是否有对这方面的豁免，由于GMS过大导致无法OTA升级，是否可以少预制某些应用？

4：裁剪系统，去除不需要的feature和功能