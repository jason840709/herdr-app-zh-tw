# GitHub 發布準備

專案顯示名稱與壓縮包名稱：**Herdr App（macOS 桌面版）繁體中文化**。

GitHub 的 repository name 只接受 ASCII 字母、數字及 `. - _`，因此倉庫技術名稱可用 `herdr-app-zh-tw`；README 標題與專案說明維持中文名稱。

官方規則：https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository

## 上傳內容

將本發布資料夾中的檔案作為倉庫內容。不要將外層工作專案、下載項目、安裝後的備份或紀錄一併上傳。

- Repository name：`herdr-app-zh-tw`
- Description：`Herdr App（macOS 桌面版）繁體中文化（herdr-app-zh-tw）：對應上游 herdrdev/herdr-app 的非官方臺灣繁體中文套件，僅支援 macOS Apple Silicon 版 Herdr.app，不適用終端機版、CLI 或其他平台。`
- 版本標籤（對應 Herdr App 版本）：`v0.1.16`
- Release 標題：`Herdr App（macOS 桌面版）繁體中文化 v0.1.16`

## 發布附件

執行 `python3 -B release.py`，將產生的 `Herdr App（macOS 桌面版）繁體中文化-v0.1.16.zip` 與 `.zip.sha256` 放到 GitHub Release 附件。

ZIP 內的 `SHA256SUMS` 可驗證各發布檔案。打包器只收錄明確列出的檔案，安裝後新增的 `backups/`、`work/`、`安裝紀錄.json` 或其他檔案不會被收入。

若之後更新文字、安裝程式或 payload，請重新執行打包器，並為新版本更新 README 與 Release 說明。不要直接沿用其他 Herdr 版本的位址修補。

打包工具只產生本機壓縮包，不會建立 GitHub 倉庫或自動上傳內容。
