# NutriGuide Mobile Appium Automation Framework (Node.js) 📱

This is a dedicated **Node.js WebdriverIO & Appium Mobile Testing Project** located in its own separate directory (`mobile_appium_nodejs/`).

---

## 📁 Directory Structure
```text
mobile_appium_nodejs/
├── package.json               # Node.js dependencies & scripts
├── wdio.conf.js               # WebdriverIO Appium configuration
├── generate_excel_report.js   # ExcelJS analysis report generator
├── specs/
│   └── mobile_e2e.spec.js     # Appium Mobile E2E test cases
└── README.md                  # Execution guide
```

---

## 🛠️ Prerequisites
- Node.js v18+
- Appium Server v2+ (`npm install -g appium`)
- Appium UiAutomator2 driver (`appium driver install uiautomator2`)

---

## 🚀 Running Mobile Tests & Generating Reports

### 1. Install Node.js Dependencies:
```bash
cd mobile_appium_nodejs
npm install
```

### 2. Run Appium E2E Mobile Tests:
```bash
npm run test:mobile
```

### 3. Generate Mobile Excel Analysis Report:
```bash
npm run report:excel
```

The output Excel analysis report will be saved to:
`Test Results/Excel/Automation_Mobile_Appium_Report.xlsx`
