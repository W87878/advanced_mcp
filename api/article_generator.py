import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import time
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback
from langchain_core.prompts import ChatPromptTemplate

class ArticleGenerator:
    def __init__(self):
        self.user_data_dir: str = os.getenv('USER_DATA_DIR')
        self.profile_directory: str = os.getenv('PROFILE_DIRECTORY')
        self.MODEL = os.getenv('MODEL', 'gpt-4o')
        self.driver = None
        self.OPEN_API_KEY: str = os.getenv('OPEN_API_KEY')
        self.DIR = os.getenv('DIR')
        self.TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))
        self.MAX_TOKENS = int(os.getenv('MAX_TOKENS', 4096))

    def get_webdriver(self):
        for attempt in range(3):  # 嘗試最多 3 次
            try:
                options = uc.ChromeOptions()
                options.add_argument('--ignore-certificate-errors')
                options.add_argument("--disable-gpu")
                options.add_argument("--disable-dev-shm-usage")
                # options.add_argument("headless")
                options.add_argument(f"--user-data-dir={self.user_data_dir}")
                options.add_argument(f'--profile-directory={self.profile_directory}')
                self.driver=uc.Chrome(options=options, version_main=136, use_subprocess=True)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                return self.driver
            except Exception as e:
                print(f'Error: {e}')
                print(f"WebDriver 啟動失敗，第 {attempt + 1} 次嘗試...")
                if attempt == 2:
                    raise e
                time.sleep(2)  # 等待 2 秒後重試

    def summarize_meeting(self, text):
        for attempt in range(3):
            try:
                driver = self.get_webdriver()
                url = "https://notebooklm.google.com/"
                driver.get(url)
                time.sleep(15)
                # 新建專案 
                new_created = driver.find_element(By.XPATH, '/html/body/labs-tailwind-root/div/welcome-page/div/div[2]/div[1]/div/button/span[2]')
                while not new_created:
                    time.sleep(0.1)
                    new_created = driver.find_element(By.XPATH, '/html/body/labs-tailwind-root/div/welcome-page/div/div[2]/div[1]/div/button/span[2]')
                new_created.click()
                time.sleep(2)

                # 找文字區塊按鈕
                text_click = driver.find_element(By.XPATH, '//*[@id="mat-mdc-chip-4"]/span[2]/span')
                driver.execute_script("arguments[0].scrollIntoView(true);", text_click)
                while not text_click:
                    time.sleep(0.1)
                    text_click = driver.find_element(By.XPATH, '//*[@id="mat-mdc-chip-4"]/span[2]/span')
                    driver.execute_script("arguments[0].scrollIntoView(true);", text_click)
                text_click.click()
                time.sleep(1)
                # 找到 textarea 並輸入網址
                text_input = driver.find_element(By.ID, 'mat-input-0')
                while not text_input:
                    time.sleep(0.1)
                    text_input = driver.find_element(By.ID, 'mat-input-0')
                text_input.send_keys(text)
                text_button = driver.find_element(By.XPATH, '//button//span[contains(text(), " Insert ")]')
                while not text_button:
                    time.sleep(0.1)
                    text_button = driver.find_element(By.XPATH, '//button//span[contains(text(), " Insert ")]')
                text_button.click()
                print(f'成功輸入文字: {text}')
                time.sleep(7)


                # 上面幾層
                omnibar = driver.find_element(By.TAG_NAME, 'chat-panel').find_element(By.TAG_NAME, 'omnibar')
                box = omnibar.find_element(By.TAG_NAME, 'query-box')
                prompt_input = box.find_element(By.TAG_NAME, 'textarea')
                while not prompt_input.is_displayed() or not prompt_input.is_enabled():
                    time.sleep(0.1)
                    prompt_input = box.find_element(By.TAG_NAME, 'textarea')
                
                j = 1
                complete_prompt = "你是一位專業的技術會議紀錄助理，負責從系統開發、AI應用與Chatbot專案的會議逐字稿中，萃取並彙整出條理分明、專業且精煉的繁體中文會議摘要。請依據以下分類，並以Markdown格式、標題、條列式、加粗重點等方式，產出結構化的紀錄：一、技術討論要點 - 條列本次會議針對系統架構設計、Chatbot流程、AI模型選型與整合的核心技術討論（如API設計、資料流程、LLM/RAG部署邏輯、模型微調策略、第三方服務串接等）。如有提及API參數、資料結構、模型設定、流程圖或關鍵邏輯，請具體條列。若逐字稿資訊不足，請根據上下文合理推測，並以（推估）標註。二、系統與應用層決策 - 明確列出拍板定案的技術與應用方案（如：模型類型、開發框架、服務部署平台、前後端整合方式），並簡要補充決策依據或選型理由（如效能、成本、可擴展性等）。三、後續待辦與執行排程 - 條列尚待完成的具體項目，包含模型訓練、資料清洗、API建置、前端串接、測試/驗證流程等，並標明預計完成時程及預期產出。若有KPI或驗收標準（如自動化覆蓋率、流程時效等），請明確列出。四、任務負責人 / 技術角色 - 對應每項待辦，標註負責人或職能角色（如：後端工程師、ML Engineer、PM、QA、AI團隊）。五、技術風險與挑戰（如有）- 條列本次會議討論到的技術風險、挑戰，或需跨部門協作事項，並簡述應對策略。⚠️ 僅聚焦於技術與專案相關資訊，刪除非技術性閒聊與會議雜訊。請用專業術語、條列式、精煉描述，提升可讀性與專業度。如逐字稿資訊不足，請主動合理推估並標註（推估）。⚠️ 請勿在摘要中包含任何引用來源、段落標註或原文引文，僅呈現整理後的內容。"
                try:
                    prompt_input.send_keys(complete_prompt)
                    prompt_input.send_keys(Keys.RETURN)
                except Exception as e:
                    print(f'Error: {e}')
                    # 使用 JavaScript 強制發送鍵盤事件
                    driver.execute_script("arguments[0].value = arguments[1];", prompt_input, complete_prompt)  # 將文字輸入到 input
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", prompt_input)  # 觸發 input 事件


                print('等候答案')
                time.sleep(40)  # 等待答案生成
                message = driver.find_element(By.TAG_NAME, 'chat-panel').find_elements(By.TAG_NAME, 'chat-message')[j]
                while not message.is_displayed() or not message.is_enabled():
                    time.sleep(0.1)
                    message = driver.find_element(By.TAG_NAME, 'chat-panel').find_elements(By.TAG_NAME, 'chat-message')[j]
            
                is_succesed = self.save_article_as_txt(message.text)
                if is_succesed:
                    return 'summary.txt 生成成功'
                else:
                    return '存檔失敗'
            except Exception as e:
                print("出現錯誤: ", str(e))
                self.driver.quit()
                self.driver = None

        if self.driver:
            time.sleep(5)
            self.driver.quit()
            return False

    def convert_to_markdown_from_openai(self, language="繁體中文"):
        system_prompt = f"""
你是一位專業的技術會議校稿助理，負責從系統開發、AI 應用與 Chatbot 專案的概況中，萃取並彙整出條理分明、專業且精煉的繁體中文會議摘要。請依據以下分類，並以Markdown格式、標題、條列式、加粗重點等方式，再次產出結構化的紀錄，並轉為{language}：

1. 技術討論要點
條列本次會議針對系統架構設計、Chatbot流程、AI模型選型與整合的核心技術討論
（如API設計、資料流程、LLM/RAG部署邏輯、模型微調策略（如 LoRA / prompt tuning / RAG）、第三方服務串接等）。
如有提及API參數、資料結構、模型設定、流程圖或關鍵邏輯，請具體條列。
若逐字稿資訊不足，請根據上下文合理推測，並以（推估）標註。

2. 系統與應用層決策
明確列出拍板定案的技術與應用方案（如：模型類型、開發框架、服務部署平台、前後端整合方式），
並簡要補充決策依據或選型理由，例如：模型類型（GPT-4o、Claude、Gemini）、開發框架、服務部署平台（如 AWS / GCP / Azure / 自架），或前後端整合方式。

3. 後續待辦與執行排程
條列尚待完成的具體項目，包含模型訓練、資料清洗、API建置、前端串接、測試/驗證流程等，並標明預計完成時程及預期產出。
若有KPI或驗收標準（如自動化覆蓋率、流程時效等），請明確列出。
如有時程討論，請標明預計完成時間。

4. 任務負責人 / 技術角色
對應每項待辦，標註負責人或職能角色（如：後端工程師、ML Engineer、PM、QA、AI團隊）。

5. 技術風險與挑戰（如有）
條列本次會議討論到的技術風險、挑戰，或需跨部門協作事項，並簡述應對策略。

⚠️ 僅聚焦於技術與專案相關資訊，刪除非技術性閒聊與會議雜訊。
請用專業術語、條列式、精煉描述，提升可讀性與專業度。
如逐字稿資訊不足，請主動合理推估並標註（推估）。
⚠️ 請勿在摘要中包含任何引用來源、段落標註或原文引文，僅呈現整理後的內容。
"""
        # 將內容轉換為 Markdown 格式
        with open(self.DIR + '/summary.txt', 'r', encoding='utf-8-sig') as file:
            content = file.read()
        with get_openai_callback() as cb:
            model_name = self.MODEL
            llm = ChatOpenAI(
                model_name=model_name, 
                temperature=self.TEMPERATURE, 
                api_key=self.OPEN_API_KEY, 
                max_tokens=self.MAX_TOKENS)

            qa_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{content}"),
                ]
            )

            rag_chain = (
                qa_prompt
                | llm
                | StrOutputParser()
            )

            result = rag_chain.invoke(
                {"content": content}
            )


        print(f"Total Tokens: {cb.total_tokens}")
        print(f"Prompt Tokens: {cb.prompt_tokens}")
        print(f"Completion Tokens: {cb.completion_tokens}")
        print(f"Total Cost (USD): ${cb.total_cost}")
        # 將結果保存為 Markdown 文件
        is_success = self.save_article_as_md(result, filename=self.DIR + '/summary.md')
        return is_success

    def save_article_as_md(self, content):
        # 打開或創建一個 .md 文件
        try:
            filename = self.DIR + '/summary.md'
            with open(filename, 'w+', encoding='utf-8-sig') as file:
                # 將文章內容寫入文件
                file.write(content)
                print(f"文章已成功保存為 {filename}")
            return True
        except Exception as e:
            print(f"保存文章時發生錯誤: {str(e)}")
            return False

    def save_article_as_txt(self, content):
        # 打開或創建一個 .txt 文件
        try:
            filename = self.DIR + '/summary.txt'
            with open(filename, 'w+', encoding='utf-8-sig') as file:
                # 將文章內容寫入文件
                file.write(content)
                print(f"文章已成功保存為 {filename}")
            return True
        except Exception as e:
            print(f"保存文章時發生錯誤: {str(e)}")
            return False
