# Herdr App（macOS 桌面版）繁體中文化

本包適用於 [Herdr App](https://github.com/herdrdev/herdr-app)（`herdr-app`）的 **macOS 桌面程式 `Herdr.app`**，將設定、原生選單、內建對話框、工作區與更新說明改為臺灣繁體中文。

**不是終端機版 `herdr` 或 `herdr-core`／`hc` CLI 的中文化，也不支援 Windows、Linux 或 Intel Mac。**

這是非官方中文化工具，只修改桌面 App 的介面；不修改 herdr-core 執行檔或終端機內其他程式的輸出。

**版本：v0.1.16，直接對應 Herdr App 0.1.16；僅適用 macOS Apple Silicon 桌面版。**

## 使用前

- 已安裝 macOS Apple Silicon 版 Herdr App 0.1.16（`Herdr.app`）。本包不包含完整 Herdr App，也不會自動下載程式。
- 已有原生 Apple Silicon Python 3.9 或更新版本，終端機可執行 `python3`；不需另外安裝 Python 套件。
- macOS 的 `codesign` 與 `codesign_allocate` 可用。部分電腦需要先備妥 Apple Command Line Tools。
- 工具與 Herdr App 放在同一個本機磁碟；目前帳號對兩個所在資料夾有寫入權限。

程式會核對版本與完整執行檔 SHA-256。檔案不符、程式仍在執行或驗證失敗時，會停止，不會套用到其他版本。

## 安裝

1. 解壓縮整個資料夾到 Mac 的本機磁碟。
2. 用 **⌘Q 結束 Herdr**。
3. 雙擊 **一鍵安裝繁體中文.command**。
4. 出現「已套用繁體中文」後，正常開啟 Herdr。

若使用 GitHub 的來源碼下載，而 command 檔沒有執行權限，也可在這個資料夾的終端機執行：

```sh
python3 -B 中文化工具.py install
```

請保留整個工具資料夾。安裝後產生的 `backups/` 與 `安裝紀錄.json` 是還原所需資料，不要刪除或公開上傳。

若使用其他中文化工具，請先透過原工具還原英文版，再套用本包。

## 還原英文版

先用 ⌘Q 結束 Herdr，再雙擊 **還原英文版.command**，或執行：

```sh
python3 -B 中文化工具.py restore
```

還原會核對備份與目前安裝的版本。若 App 已被官方更新或其他工具修改，會停止，以免覆蓋新的程式。

## 涵蓋內容

- 設定六個分頁與字型、佈景主題、電腦、通知、更新、隱私權說明。
- macOS 原生選單、命令面板、快捷鍵、歡迎導覽與意見回饋。
- 確認、重新命名、工作樹、檔案、變更、代理程式與通知介面。
- 終端機版面、Herdr 98、搜尋與桌面 App 核心設定頁面的固定介面文字。
- 0.1.16 當版內建更新說明，以及相機、麥克風與 AppleScript 權限說明。

產品與字型名稱、命令、快捷鍵、設定鍵、使用者自己輸入的文字，以及終端機內其他程式的輸出會保留原值。遠端系統錯誤與堆疊追蹤也會保留原文。自行安裝的第三方模組與自訂介面文字不在本包範圍內。

## 簽章與後續更新

工具先在本機建立副本、套用修補、沿用原版權限宣告進行 ad-hoc 簽署，再驗證簽章；完成後才保留原版並置換。這不是 Herdr 開發者的官方簽章或公證，工具不會停用 macOS 的全域安全保護。

Herdr 官方更新可能換回英文。新版必須另行核對，不能直接沿用本包的修補位置。

支援的原版執行檔 SHA-256：

```text
985e70ce4d78c58ceb1e5e6ea2ccb03231d46fef18a0e04ec6ca5380a4099805
```

## 隱私與發布

發布包僅包含安裝器、修補資料、說明、授權與打包工具。沒有完整 App、使用者設定、安裝紀錄、備份、工作區、對話或本機測試紀錄。

工具離線執行，沒有遙測或資料上傳。只有實際安裝後，才會在工具資料夾產生該台電腦自己的還原資料；這些檔案已列入 `.gitignore`，也不在 `release.py` 的發布白名單內。

重新產生可分享的壓縮包：

```sh
python3 -B release.py
```

打包器使用固定白名單，排除執行後產生的資料，並移除 ZIP 的檔案時間、擁有者與延伸屬性等本機中繼資料。詳見 [PUBLISHING.md](PUBLISHING.md)。

## 原始專案與授權

[Herdr 原始專案](https://github.com/herdrdev/herdr-app) 使用 Apache License 2.0。本包保留其授權與上游第三方署名；詳見 [LICENSE](LICENSE)、[NOTICE.md](NOTICE.md) 與 [上游第三方授權聲明](licenses/THIRD-PARTY-NOTICES.txt)。
