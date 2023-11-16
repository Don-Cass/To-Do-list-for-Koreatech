from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from bs4 import BeautifulSoup
import csv
import time

# 남은 기한에 따라 과제를 정렬하는 함수
def sort_tasks_by_remaining_days(tasks):
    def get_remaining_days(task):
        return float(task[-1].replace("일", "")) if task[-1] != "-" else float('inf')
    return sorted(tasks, key=get_remaining_days)

# 각 리스트를 CSV 파일로 저장하는 함수
def save_to_csv(file_name, tasks):
    with open(file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['과제 종류', '과목명', '과제명', '일정', '남은 기한'])
        for task in tasks:
            writer.writerow(task)

# Selenium을 사용하여 웹 페이지에서 데이터 추출
print("=" * 100)
print("To Do List for Koreatech ver 0.0")
print("=" * 100)
id_txt = input('ID: ')
print("\n")
pw_txt = input('PASSWORD: ')
print("\n")

s = Service("c:/To-Do-list-for-Koreatech/chromedriver.exe")
driver = webdriver.Chrome(service=s)

url = 'https://el2.koreatech.ac.kr/login/guestlogin.php?ssologin=1'
driver.get(url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'username')))
driver.maximize_window()

element = driver.find_element(By.ID,'username')
element.send_keys(id_txt)
element = driver.find_element(By.ID,'password')
element.send_keys(pw_txt)
element.send_keys("\n")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="page-site-index"]/div[1]/div/div/div[1]/a[3]')))
driver.find_element(By.XPATH, '//*[@id="page-site-index"]/div[1]/div/div/div[1]/a[3]').click( )
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="region-main"]/ul/li[2]/a')))
driver.find_element(By.XPATH, '//*[@id="region-main"]/ul/li[2]/a').click( )
time.sleep(5)

# BeautifulSoup를 사용하여 HTML 파싱 및 데이터 추출
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

tasks_0_7 = []  # 기한이 0~7일인 과제
tasks_8_14 = [] # 기한이 8~14일인 과제

# 모든 'activity-card' 클래스의 div 태그 찾기
for div in soup.find_all('div', class_='activity-card'):
    # D-n 또는 D DAY 추출 및 처리
    d_day_text = div.find('div', class_='head').find_all('div')[1].text.strip()
    days_remaining = -1  # 기본값 설정

    if 'D-' in d_day_text:
        days_remaining = int(d_day_text.split('D-')[1])
    elif d_day_text == 'D DAY':
        days_remaining = 0
    elif d_day_text == '-':  # 기한이 지정되지 않음
        days_remaining = float('inf')  # 무한대로 설정

    # 과제 종류, 과목명, 과제명, 일정 추출
    assignment_type = div.find('div', class_='head').find_all('div')[0].text.strip()
    body_div = div.find('div', class_='body')
    if body_div and len(body_div.find_all('div')) > 1:
        subject_div = body_div.find_all('div', class_='p-2')[0]
        subject = subject_div.find('div', class_='red').text.split(": ")[1].strip() if subject_div.find('div', class_='red') else "과목명 미상"
        assignment = subject_div.find_all('div')[1].text.strip() if len(subject_div.find_all('div')) > 1 else "과제명 미상"
    else:
        subject = "과목명 미상"
        assignment = "과제명 미상"
    schedule = div.find('div', class_='foot').text.strip().split(":")[1].strip() if div.find('div', class_='foot') and ":" in div.find('div', class_='foot').text else "일정 미상"

    # 과제 분류 및 리스트에 추가
    task_info = [assignment_type, subject, assignment, schedule, str(days_remaining) + "일" if days_remaining != float('inf') else "-"]
    if 0 <= days_remaining <= 7:
        tasks_0_7.append(task_info)
    elif 8 <= days_remaining <= 14:
        tasks_8_14.append(task_info)


# 과제 목록을 남은 기한에 따라 정렬
tasks_0_7_sorted = sort_tasks_by_remaining_days(tasks_0_7)
tasks_8_14_sorted = sort_tasks_by_remaining_days(tasks_8_14)

# 정렬된 리스트를 CSV 파일로 저장
save_to_csv('tasks_0_7_sorted.csv', tasks_0_7_sorted)
save_to_csv('tasks_8_14_sorted.csv', tasks_8_14_sorted)

print("과제 목록이 정렬되어 tasks_0_7_sorted.csv와 tasks_8_14_sorted.csv 파일로 저장되었습니다.")

# WebDriver 종료
driver.quit()


