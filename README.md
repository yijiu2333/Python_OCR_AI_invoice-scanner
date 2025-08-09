SPDX-License-Identifier: MIT

# Python_OCR_AI_invoice-scanner

## 📖 写在最前面
> 该项目基于 Python 3.10.8 开发，公司内部相关数据以用虚拟数据代替。
> 该项目使用的本地化测试用 AI 使用 ollama 搭建，在生产环境中推荐使用vllm或
源码部署，请在 ai_excel_generater 中修改具体调用 AI 的IP地址及端口号
> 该项目主要思路是利用ocr读取发票内容，在有AI二次审核确保准确率，最终生成
要求格式的Excel文件用于后续自动化调用。其中本地化AI实测deepseek R1 32b 
效果较为理想，或是使用Qwen系列模型（至少14b比较准确），由于测试用服务器没
有显卡，所以选择对CPU驱动AI有所优化的ollama进行测试。截止上传日期为止，已
有QWQ32等新模型上线，考虑到定时任务的特性和不高的数据量，带有思维链的模型
也可作为AI检测模型使用。

---

## ⚙️ 介绍
> 一个自动化扫描PDF中发票并生成对应格式的Excel文件的程序，用于配合内部后续自动化系统工作

---

## 📌 主要功能
- ✅ 功能 1：定时自动扫描待扫描的文件
- ✅ 功能 2：利用本地 AI 二次审查 OCR 模型的扫描结果
- ✅ 功能 3：为后续自动化系统生成合适格式的 Excel 文件
- ✅ 功能 4：定期生成 logs 文件

---

## 🆕 最近更新
| 日期 | 版本 | 变更摘要 |
|------|------|----------|
| 2025-08-08 | v1.0.0 | 整理代码发送 github |

---

## 🛠️ 技术栈
- Python Openai 
- OCR
- ollama

---

## 🚀 快速开始
1. 克隆仓库  
   ```bash
   git clone https://github.com/yijiu2333/Python_OCR_AI_invoice-scanner.git
   cd Python_OCR_AI_invoice-scanner

   ```

2. 安装依赖
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. 本地启动
   修改 start_ocr_workflow.bat 文件中的文件夹路径
   双击 start_ocr_workflow.bat 文件启动
---

## 🚫 版权说明
   - 整体项目：以 GPL-3.0 许可证发布（详见 LICENSE）
   - 第三方组件：
        - 界面框架 PyQt-Fluent-Widgets 采用 GPL-3.0，其源码已按许可证要求随附于 third_party/ 目录。
        - 其余引用的开源代码均已保留原始版权信息及许可证文件。
   - 使用限制：本项目仅供学习/作品集展示，内部包含的非商用资源（如示例图标、图片、字体。UI组件等）请自行替换后方可用于商业场景。
   - json文件中均为虚拟数据，仅用于程序功能展示，纯属虚构，不代表真实情况。

---

## 📄 许可证
   - [MIT](./LICENSE) © 2025 Yijiu Zhao
