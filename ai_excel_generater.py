import requests
import pandas as pd
import os
import json
from typing import List, Tuple
from openai import OpenAI  # 替换旧版导入

class ExcelGenerator:
    def __init__(self, api_key: str = ""):
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",  # 官方API端点
            api_key="ollama"  # 优先使用传入的密钥
        )
        self.system_prompt = """
        严格按以下要求处理发票文本：
        1. 提取以下字段（全部保留，缺失用NULL）：
           - 发票号（11位仅数字）
           - 发票代码（发票号下方，19位）
           - 购买方名称，税号，地址，电话，开户行，银行账号（按顺序提取，以英文逗号分隔）
           - 具体交易内容（按顺序提取，包含规格，数量，单位，价格等，以英文逗号分隔）
           - 销售方名称，税号，地址，电话，开户行，银行账号（按顺序提取，以英文逗号分隔）
           - 不含税金额（保留两位小数）
           - 税额（保留两位小数）
           - 价税合计（保留两位小数）
           - 备注（严格提取ocr后的备注内容，无论内容，不可变动）
        2. 输出格式严格遵循：
           发票号,发票代码,购买方名称,购买方税号,购买方地址，购买方电话，购买方开户行，购买方银行账号，销售方名称,销售方税号,销售方地址，销售方电话，销售方开户行，销售方银行账号,不含税金额,税额,价税合计,交易内容,备注
        示例："123456,12345678901234567890,XX公司,91320211MA1MAKE1X1,北京朝阳区,010-66668888,工商银行北京分行,6222020200045678901,YY公司,91440300MA5DFLY123,深圳福田区,0755-88889999,招商银行深圳分行,6226098765432100,1200.00,156.00,1356.00,商品A|标准|个|2|50.00|100.00|13%;服务费|技术咨询|次|1|200.00|200.00|6%,纸质发票"
        """

    def ask_ollama(self, text: str, max_retry=3) -> list:
        for _ in range(max_retry):
            try:
                response = self.client.chat.completions.create(
                    model="qwen2.5:14b",  # 官方模型名称
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3
                )
                # 新增调试输出
                result = response.choices[0].message.content
                print("[DEBUG] AI原始响应:", result)  # 打印原始响应
                
                processed = []
                fields = result.split(",")
                if len(fields) != 19:  # 验证字段数量
                    print(f"[WARNING] 字段数量异常: 预期19，实际{len(fields)}")
                    continue
                
                # 按字段索引处理数据
                for idx in range(19):
                    value = fields[idx].strip()
                    
                    # 处理数值字段（索引14-16：不含税/税额/价税合计）
                    if idx in [14, 15, 16]:
                        try:
                            processed.append(float(value) if value else 0.0)
                        except:
                            processed.append(0.0)
                    # 处理交易内容和备注（索引17-18）
                    elif idx in [17, 18]:
                        processed.append(value if value != 'NULL' else '')
                    # 处理其他文本字段
                    else:
                        processed.append(value if value != 'NULL' else None)

                print("[DEBUG] 处理后数据:", processed)
                return processed
            except Exception as e:
                print(f"API请求异常: {str(e)}")
        return []

    def process_txt_files(self, folder_path: str) -> List[List[float]]:
        data = []
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        print(f"[DEBUG] 正在处理文件: {filename}") 
                        print(f"[DEBUG] 文件内容: {content[:100]}...") 
                        result = self.ask_ollama(content)
                        # 根据实际输出字段数调整验证
                        if len(result) == 19:  # 匹配系统提示词中的19个字段
                            data.append(result)
        return data

    def generate_excel(self, input_folder: str, output_path: str):
        raw_data = self.process_txt_files(input_folder)
        df = pd.DataFrame(
            raw_data,
            columns=[
                # 完整字段结构（共19列）
                "发票号", "发票代码",
                "购买方名称", "购买方税号", "购买方地址", "购买方电话", "购买方开户行", "购买方账号",
                "销售方名称", "销售方税号", "销售方地址", "销售方电话", "销售方开户行", "销售方账号",
                "不含税金额", "税额", "价税合计", 
                "交易内容", "备注"
            ]
        )
        if raw_data:
            df.to_excel(output_path, index=False)


if __name__ == "__main__":
    generator = ExcelGenerator()
    generator.generate_excel(
        input_folder="output",
        output_path="output/invoice_report.xlsx"
    )