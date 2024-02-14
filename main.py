"""
面向用户的完善版本
开始于2024.1.16
实现功能如下：
1.查询到目的地的车次
2.进行登录购票
"""
# ----------------------------------------------------------------------------------------------------------------------
# 导入请求模块
import requests
# 导入json
import json
# 导入表格输出模块
import prettytable as pt

# ----------------------------------------------------------------------------------------------------------------------
# 实例化对象
tb = pt.PrettyTable()
# 添加表头
tb.field_names = [
    "序号", "车次", "出发日期", '出发时间', '耗时', '到达时间', '始发站', '终点站', '出发站', '到达站',
    '商务座', '一等座', '二等座', '硬座', '无座', '软卧', '硬卧'
]

# 读取城市json文件
f = open("city_plus.json", "r", encoding="utf-8")

# f.read()是字符串,然后用json转换成字典
city_json = json.load(f)
f.close()

# ----------------------------------------------------------------------------------------------------------------------
# 查询功能

# 查票输入 出发城市/目的城市/出发时间
start_city = input("输入出发城市：")
from_city = city_json[start_city]

end_city = input("输入目的城市：")
to_city = city_json[end_city]

data = input("输入出发时间<如2024-01-18>：")
print(f"你输入的城市代码是：{from_city}与{to_city}")


# 确定请求url
url = (f"https://kyfw.12306.cn/otn/leftTicket/queryE?leftTicketDTO.train_date={data}&leftTicketDTO.from_station="
       f"{from_city}&leftTicketDTO.to_station={to_city}&purpose_codes=ADULT")
url2 = (f"https://kyfw.12306.cn/lcquery/query?train_date={data}&from_station_telecode={from_city}&to_station_telecode="
        f"{to_city}&middle_station=&result_index=0&can_query=Y&isShowWZ=N&purpose_codes=00&channel=E")

# 模拟浏览器
headers = {
    "Cookie": "_uab_collina=170540287826811371192297; JSESSIONID=8E45823A95D273CC06D6718BFC0B08F2; guidesStatus=off;" +
              " highContrastMode=defaltMode; cursorStatus=off; BIGipServerpassport=854065418.50215.0000; route=90363" +
              "59bb8a8a461c164a04f8f50b252; BIGipServerotn=2045247754.24610.0000; _jc_save_wfdc_flag=dc; _jc_save_fr" +
              "omStation=%u957F%u6C99%u5357%2CCWQ; _jc_save_toStation=%u4E0A%u6D77%u8679%u6865%2CAOH; _jc_save_toDat" +
              "e=2024-01-17; _jc_save_fromDate=2024-01-17",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0" +
                  " Safari/537.36 Edg/118.0.2088.57"
}
# 发送请求 <Response [200]> 表示请求成功
response = requests.get(url=url, headers=headers)

page = 0
# index是某次车次的信息，是一个字符串
for index in response.json()["data"]["result"]:

    info_list = index.split('|')
    TrainNumber = info_list[3]   # 车次,经过上面的循环下标已经确定
    star_day = info_list[13]  # 发车日期
    star_time = info_list[8]     # 发车时间
    end_time = info_list[9]      # 到达时间
    use_time = info_list[10]  # 耗时

    StarStation = info_list[4]    # 始发站
    EndStation = info_list[5]     # 终点站
    star_station = info_list[6]  # 发车站
    end_station = info_list[7]   # 到达站
    # 把车站代码转换成中文
    for key in city_json.keys():
        if city_json[key] == StarStation:
            StarStation = key
        if city_json[key] == EndStation:
            EndStation = key
    star_station = response.json()["data"]["map"][star_station]
    end_station = response.json()["data"]["map"][end_station]

    business_class = info_list[32]  # 商务座
    first_class = info_list[31]  # 一等座
    second_class = info_list[30]  # 二等座
    hard_seat = info_list[29]    # 硬座
    no_seat = info_list[26]      # 无座
    soft_sleeper = info_list[23]  # 软卧
    hard_sleeper = info_list[28]     # 硬卧

    # 添加行信息
    tb.add_row([
        page, TrainNumber, star_day, star_time, use_time, end_time, StarStation, EndStation, star_station, end_station,
        business_class, first_class, second_class, hard_seat, no_seat, soft_sleeper, hard_sleeper,
    ])
    page += 1

print("---------------------------------------------------------------------------------------------------------------")
if page == 0:
    url3 = "https://kyfw.12306.cn/otn/lcQuery/init"
    print("恭喜你找到了隐藏界面（懒得开发）\n")
    response = requests.get(url=url2, headers=headers)
    if response.json()["status"]:
        print(f"非常抱歉，没有找到直达车次，经查询，有以下中转信息：")
        page = 0
        # index是某次车次的信息，是一个字符串
        for index in response.json()["data"]["middleList"]:
            print(index)
            page += 1
        print(f"您查询的日期：{data} 一共有{page}种中转方法，祝您旅途愉快")
        print(f"中转购票功能尚未开发，可以访问以下网站自行购票:{url3}")
    else:
        print(f"""抱歉，您查询的日期：{data}  没有直达与中转车次匹配
您可以把日期往后一天，或者更换其他交通方式""")
    exit(0)  # 退出程序，返回状态码0
else:
    print(f"您查询的日期：{data} 一共有{page}种直达方案，祝您旅途愉快")
    print(tb)


# ----------------------------------------------------------------------------------------------------------------------
"""
开始于2024.1.16
实现功能如下：
1.根据查询信息自动购票
"""
# ----------------------------------------------------------------------------------------------------------------------
# 导入selenium网站操作模块,Keys是键盘操作
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
# ----------------------------------------------------------------------------------------------------------------------

# start_city = input("输入出发城市：")
# end_city = input("输入目的城市：")
# data = input("输入出发时间<如2024-01-18>：")
num = int(input("请输入你要购买的车次序号："))
op = input("是否选择硬座YES/NO：")
is_really = input("是否真的购票YES/NO：")
num = (num+1)*2-1
# 初始化账号密码
print("请输入12306的账号密码")
account = input("请输入账号（手机号）：")
password = input("请输入12306密码：")
idcard4 = input("请输入身份证后四位：")

# 0.设置不自动关闭浏览器
options = webdriver.ChromeOptions()
options.add_experimental_option('detach', True)
# 1.打开/创建浏览器并设置等待
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(4)
# 2.输入网址
driver.get("https://kyfw.12306.cn/otn/resources/login.html")

# ----------------------------------------------------------------------------------------------------------------------
# 3.输入账号密码,身份证后四位，获取验证码，然后点击登录

# user_name = input("请输入名字：")
# idcard4 = input("请输入身份证号全部：")
driver.find_element(By.CSS_SELECTOR, "#J-userName").send_keys(account)      # 输入账号
driver.find_element(By.CSS_SELECTOR, "#J-password").send_keys(password)     # 输入密码
driver.find_element(By.CSS_SELECTOR, "#J-login").click()                    # 点击登录
driver.find_element(By.CSS_SELECTOR, "#id_card").send_keys(idcard4)          # 输入身份证后四位
driver.find_element(By.CSS_SELECTOR, "#verification_code").click()          # 点击获取验证码
code = input("请输入手机短信验证码：")
driver.find_element(By.CSS_SELECTOR, "#code").send_keys(code)               # 输入验证码
driver.find_element(By.CSS_SELECTOR, "#sureClick").click()                  # 点击确定
driver.find_element(By.CSS_SELECTOR, "#J-login").click()                    # 点击登录

# 4.查询购票
driver.find_element(By.CSS_SELECTOR, "#link_for_ticket").click()            # 点击预定购票
driver.find_element(By.CSS_SELECTOR, "#train_date").clear()
driver.find_element(By.CSS_SELECTOR, "#train_date").send_keys(data)         # 输入日期
driver.find_element(By.CSS_SELECTOR, "#fromStationText").click()            # 点击
driver.find_element(By.CSS_SELECTOR, "#fromStationText").send_keys(start_city)  # 输入出发地
driver.find_element(By.CSS_SELECTOR, "#fromStationText").send_keys(Keys.ENTER)  # 点击回车
driver.find_element(By.CSS_SELECTOR, "#toStationText").click()              # 点击
driver.find_element(By.CSS_SELECTOR, "#toStationText").send_keys(end_city)  # 输入目的地
driver.find_element(By.CSS_SELECTOR, "#toStationText").send_keys(Keys.ENTER)  # 点击回车
driver.find_element(By.CSS_SELECTOR, "#query_ticket").click()               # 点击查询

# 5.是否买硬座
driver.find_element(By.CSS_SELECTOR, "#cc_seat_type_1_check").click()

# 5购票/html/body/div[2]/div[7]/div[12]/table/tbody/tr[19]/td[13]/a
try:
    # 点击预约
    driver.find_element(By.XPATH, f"/html/body/div[2]/div[7]/div[12]/table/tbody/tr[{num}]/td[13]/a").click()
    driver.find_element(By.CSS_SELECTOR, "#normalPassenger_0").click()               # 使用默认信息购票
    try:
        driver.find_element(By.CSS_SELECTOR, "#dialog_xsertcj_cancel").click()             # 取消学生票
    except:
        print("")
    # driver.find_element(By.CSS_SELECTOR, "#passenger_name_1").send_keys(user_name)                   # 输入名字
    # driver.find_element(By.CSS_SELECTOR, "#passenger_id_no_1").send_keys(idcard)                  # 输入证件号码
except :
    print("没票了，购票失败")
else :
    print("选票成功")
if op == "YES":
    try:
        driver.find_element(By.CSS_SELECTOR, "#seatType_1").click()                         # 点击席别
        driver.find_element(By.CSS_SELECTOR, "#seatType_1 > option:nth-child(2)").click()   # 选择硬座
    except :
        print("没有硬座了")
    else:
        print("选择硬座成功")

driver.find_element(By.CSS_SELECTOR, "#submitOrder_id").click()             # 提交订单
if is_really == "YES":
    driver.find_element(By.CSS_SELECTOR, "#qr_submit_id").click()  # 最后确认
else:
    print(driver.find_element(By.CSS_SELECTOR, "#qr_submit_id"))             # 购票
# driver.find_element(By.CSS_SELECTOR, "#qr_submit_id").click()           # 最后确认
# ----------------------------------------------------------------------------------------------------------------------
