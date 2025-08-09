import os
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
from paddleocr import PaddleOCR


def extract_ocr_text(result):
    texts = []
    for item in result:
        if isinstance(item, list):
            texts.extend(extract_ocr_text(item))
        # 如果当前元素是包含文字信息的元组（文本，置信度）
        elif isinstance(item, tuple) and len(item) >= 2:
            if isinstance(item[0], str):  # 确保第一个元素是文本
                texts.append(item[0])
        elif isinstance(item, list) and len(item) >= 2:
            if isinstance(item[1], tuple):
                texts.append(item[1][0])
    return texts


class OCRProcessor:
    def __init__(self, input_folder):
        self.input_folder = input_folder
        self.ocr_engine = PaddleOCR(
            use_angle_cls=True,
            lang="ch",
            use_gpu=False,
            enable_mkldnn=True,
            cpu_threads=8
        )

    def pdfprocess(self, folder_path):
        """
        处理指定文件夹中的 PDF 文件，将每页转换为灰度图像的 numpy 数组
        :param folder_path: 文件夹路径
        :return: 包含所有页面图像数组和对应 PDF 文件名的列表
        """
        pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        all_pages_info = []
        for pdf_path in pdf_files:
            try:
                with fitz.open(pdf_path) as pdf:
                    for page_num in range(len(pdf)):
                        page = pdf.load_page(page_num)
                        pix = page.get_pixmap()
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        gray_img = img.convert("L")
                        img_array = np.array(gray_img)
                        base_name = os.path.basename(pdf_path).rsplit('.', 1)[0]
                        all_pages_info.append((img_array, base_name))
            except Exception as e:
                print(f"处理文件 {pdf_path} 时出错: {str(e)}")
        return all_pages_info

    def ocr(self, pages_info, output_folder):
        """
        对输入的图像数组进行 OCR 处理，并生成对应的 txt 文件
        :param pages_info: 包含所有页面图像数组和对应 PDF 文件名的列表
        :param output_folder: 输出文件夹路径
        """
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        result_dict = {}
        for img_array, base_name in pages_info:
            result = self.ocr_engine.ocr(img_array, cls=True)
            all_texts = extract_ocr_text(result)
            if base_name not in result_dict:
                result_dict[base_name] = []
            result_dict[base_name].extend(all_texts)

        for base_name, texts in result_dict.items():
            output_path = os.path.join(output_folder, f"{base_name}_result.txt")
            self.write_to_txt(texts, output_path)

    def write_to_txt(self, text_content, output_path):
        """
        将文本内容写入 txt 文件
        :param text_content: 文本内容列表
        :param output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(text_content))


if __name__ == "__main__":
    input_dir = r"input"
    output_dir = r"output"
    processor = OCRProcessor(input_dir)
    pages_info = processor.pdfprocess(input_dir)
    processor.ocr(pages_info, output_dir)