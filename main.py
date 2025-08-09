import time
import os
import schedule
import shutil
import logging
from logging import handlers  # 新增导入
from datetime import datetime
from ocr import OCRProcessor
from ai_excel_generater import ExcelGenerator

class InvoiceProcessor:
    def __init__(self):
        self.ocr_processor = OCRProcessor("input")
        self.excel_generator = ExcelGenerator()
        self.archive_root = "archives"
        
    def process_hourly_task(self):
        logger = logging.getLogger(__name__)
        logger.info("开始每小时处理流程")
        
        # OCR处理
        try:
            pages_info = self.ocr_processor.pdfprocess("input")
            self.ocr_processor.ocr(pages_info, "output")
            logger.debug("OCR处理完成")
        except Exception as e:
            logger.error(f"OCR处理失败: {str(e)}", exc_info=True)
            return
        
        # 生成Excel报表
        self.excel_generator.generate_excel(
            input_folder="output",
            output_path=f"output/report_{datetime.now().strftime('%Y%m%d%H%M')}.xlsx"
        )
        
        # 文件归档（仅在input目录有文件时执行）
        input_files = os.listdir("input")
        if len(input_files) > 0:
            archive_folder = self._create_archive_folder()
            self._archive_input_files(archive_folder)
            logger.info(f"处理完成，文件已归档至 {archive_folder}")
        else:
            logger.info("处理完成，本次无待处理文件")

    def _archive_input_files(self, target_folder):
        self._delete_txt_files()
        moved_files = 0
        for item in os.listdir("input"):
            s = os.path.join("input", item)
            d = os.path.join(target_folder, item)
            shutil.move(s, d)
            moved_files += 1
        
        # 删除空目录（如果没有移动任何文件）
        if moved_files == 0:
            os.rmdir(target_folder)

    def _create_archive_folder(self):
        timestamp = datetime.now().strftime("%Y-%m-%d/%H-%M-%S")
        archive_path = f"{self.archive_root}/{timestamp}"
        os.makedirs(archive_path, exist_ok=True)
        return archive_path
    
    def _delete_txt_files(self):
        # 遍历目录中的所有文件和子目录
        for filename in os.listdir("output"):
            # 获取文件的完整路径
            file_path = os.path.join("output", filename)
            # 检查是否是文件以及文件扩展名是否为 .txt
            if os.path.isfile(file_path) and filename.endswith('.txt'):
                # 删除 txt 文件
                os.remove(file_path)
                print(f"已删除: {file_path}")

def main():
    # 初始化日志配置
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # 清空之前的handler
    logging.getLogger().handlers.clear()
    
    # 修复文件handler配置
    file_handler = handlers.TimedRotatingFileHandler(
        filename=os.path.join(log_dir, 'app.log'),
        when='midnight',
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.suffix = "%Y%m%d.log"
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    logging.basicConfig(
        level=logging.DEBUG,  # 全局最低级别
        encoding = 'gbk',
        format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        handlers=[file_handler, console_handler]
    )
    
    # 新增第三方库日志过滤
    logging.getLogger('ppocr').setLevel(logging.WARNING)
    logging.getLogger('paddle').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    
    processor = InvoiceProcessor()
    
    # 定时任务设置
    def safe_hourly_task():
        try:
            processor.process_hourly_task()
        except Exception as e:
            logger.error(f"定时任务执行失败: {str(e)}", exc_info=True)
    
    schedule.every().hour.at(":00").do(safe_hourly_task)
    
    # 每分钟状态输出
    def print_status():
        logger = logging.getLogger(__name__)
        pending_files = len(os.listdir('input'))
        logger.info(f"服务运行正常 | 待处理文件数: {pending_files}")
    schedule.every(1).minutes.do(print_status)

    print("服务已启动，开始监控...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    if not os.path.exists("archives"):
        os.makedirs("archives")
    main()