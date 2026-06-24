# app/libs — HERE SDK 放置處

此資料夾原本提交了 HERE Mobile SDK 的二進位檔（`HERE-sdk.aar`、`HERE-sdk-javadoc.jar`、
`MSDKUILib-release.aar`、`obj-0.3.0.jar`，合計約 100 MB）。基於下列原因已從版控移除：

1. **授權**：HERE SDK 不可重新散布，不應放進公開 repo。
2. **體積**：百 MB 的二進位讓 clone 變慢、repo 臃腫。

## 如何取得

1. 到 [HERE Developer Portal](https://developer.here.com/?create=Evaluation&keepState=true&step=terms)
   註冊 Premium SDK evaluation，下載並解壓 HERE Mobile SDK for Android。
2. 將下列檔案放回本資料夾：
   - `HERE-sdk.aar`
   - `MSDKUILib-release.aar`（如有使用 MSDKUI）
   - 其他相依 `.jar`
3. 在專案根目錄的 `local.properties` 設定你自己的 HERE 憑證（不會進版控）：

   ```properties
   here.app.id=YOUR_HERE_APP_ID
   here.app.code=YOUR_HERE_APP_CODE
   here.license.key=YOUR_HERE_LICENSE_KEY
   here.xyz.token=YOUR_HERE_XYZ_HUB_TOKEN
   ```

   這些值會在編譯時透過 `BuildConfig` 注入，原始碼不再出現任何明文金鑰。

> ⚠️ 若你 fork 自舊版本：舊 commit 曾包含明文金鑰，請務必到 HERE 後台 **revoke** 那些舊金鑰。
