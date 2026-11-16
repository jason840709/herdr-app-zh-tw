# Herdr App（macOS 桌面版）繁體中文化 v0.1.16

本版本對應 Herdr App 0.1.16，將桌面版的設定、選單、對話框、工作區與當版更新說明中文化（臺灣繁體中文）。

## 適用範圍

- 僅限 macOS Apple Silicon 版 Herdr.app（上游專案：herdrdev/herdr-app）。
- 不適用終端機版 herdr、herdr-core／hc CLI、Windows、Linux 或 Intel Mac。
- 版本號直接對應 Herdr App 版本；v0.1.16 僅支援 Herdr App 0.1.16。

## 使用方式

1. 下載並解壓縮附件中的 ZIP。
2. 確認環境已安裝 Python 3.9+ 與可用的 macOS 簽署工具。
3. 按 ⌘Q 完全結束 Herdr App，雙擊執行「一鍵安裝繁體中文.command」。
4. 顯示完成訊息後，重新開啟 Herdr App。

若需還原，請先結束 App，再雙擊執行「還原英文版.command」。請保留安裝過程產生的備份與安裝紀錄；若先前安裝過其他中文化套件，請先以原工具還原回英文版。

## 注意事項

本套件為非官方中文化包，不含完整 Herdr App 主程式。工具採離線執行，安裝時會先核對版本與 SHA-256、保留原版備份，再對修改後的副本重新簽署並驗證，不會停用 macOS 全域安全保護。上游官方更新後，需另外確認對應的相容版本。

隨附檔案包含 ZIP 壓縮檔與 SHA-256 校驗檔。詳細環境需求、授權條款與操作說明請參閱 README。
