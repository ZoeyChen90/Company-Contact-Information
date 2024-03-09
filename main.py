import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time

# 從網頁中提取內容
def extract_info(url, page_text):
    # 搜尋公司名稱並限制字數不超過 50，同時排除含有「本公司」的內容
    company_match = re.search(r'(?!.*本公司).*(有限公司|工作室|公司).*', page_text)
    if company_match:
        company_name = company_match.group(0).strip()  
        if len(company_name) > 50:  
            company_name = "None"
    else:
        company_name = "None"
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:com|tw)\b', page_text)
    LINE_match = re.search(r'LINE.*@.*', page_text, re.IGNORECASE)
    # 排除「詐騙」的內容
    phone_match = re.search(r'(?!.*詐騙).*電話.*\d+.*|.*來電.*\d+.*|.*客服專線.*\d+.*', page_text)

    # 將匹配到的內容存儲到對應的變量中，如果未找到則設為「None」
    email_address = email_match.group(0).strip() if email_match else "None"
    LINE = LINE_match.group(0).strip() if LINE_match else "None"
    phone = phone_match.group(0).strip() if phone_match else "None"

    return {'URL': url, 'Company': company_name, 'Email': email_address, 'LINE': LINE, '電話': phone}

# 主函數：從 CSV 文件中讀取網址，逐一訪問網站並提取信息，然後匯出到 CSV 文件
def main():
    csv_file_path = '/Users/zoey/Company-Contact-Information/Group_Buying_URLs.csv'
    df = pd.read_csv(csv_file_path)

    # 創建一個空的 DataFrame
    result_df = pd.DataFrame(columns=['URL', 'Company', 'Email', 'LINE', '電話'])

    for index, row in df.iterrows():
        url = row['url']
        try:
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')
            page_text = soup.get_text()

            # 透過函數 extract_info 提取網頁資訊
            info_dict = extract_info(url, page_text)

            # 將結果轉換成 df_result，並添加到大的 DataFrame (result_df) 中
            df_result = pd.DataFrame(info_dict, index=[0])
            result_df = pd.concat([result_df, df_result], ignore_index=True)

            print("URL:", url)
            print("Company:", info_dict['Company'])
            print("Email:", info_dict['Email'])
            print("LINE:", info_dict['LINE'])
            print("電話:", info_dict['電話'])
            print()  

        except requests.exceptions.RequestException as e:
            print(f"Error accessing URL: {url}")
            print(f"Error details: {e}")

        time.sleep(1)

    # 匯出成 CSV 檔案
    result_df.to_csv('Company_Information.csv', index=False)

if __name__ == "__main__":
    main()
