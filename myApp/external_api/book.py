import requests
import http.client
import json
class BookAPI:
    def __init__(self):
        self.headers = {
            "x-rapidapi-key": "763ac69eb6msh793e9d528a2bddbp1f4d8ajsn8dac6a73a4d7",  # ✅ 你的 API 密钥
            "x-rapidapi-host": "booking-com15.p.rapidapi.com"
        }
        self.conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com")

    def search_destination(self, query):
        self.conn.request("GET", f"/api/v1/flights/searchDestination?query={query}", headers=self.headers)

        res = self.conn.getresponse()
        data = res.read()
        if res.status != 200:
            print(f"搜索请求失败: {res.status} {res.reason}")
            print(data.decode("utf-8"))
            return None
        search_results = json.loads(data.decode("utf-8"))
        # print("地点搜索成功!")

        return search_results

        # data = api.search_flights(origin, destination, trip_type, date, return_date, flight_class, airline, sort)





    def extract_flight_info(self, search_results):
        """
        从搜索结果中提取航班关键信息
        返回一个包含所有航班信息的列表,每个航班包含以下字段:
        - date: 起飞日期
        - time: 起飞和到达时间
        - route: 起飞-到达城市
        - airline: 航空公司
        - aircraft: 机型 
        - price: 总价格
        """
        flights = []
        
        # 检查搜索结果是否有效
        if not search_results or 'data' not in search_results:
            return flights
            
        segments = search_results['data'].get('segments', [])
        total_price = search_results['data']['priceBreakdown']['total']
        
        for segment in segments:
            flight = {}
            
            # 提取日期和时间
            departure_datetime = segment['departureTime']
            arrival_datetime = segment['arrivalTime']
            flight['date'] = departure_datetime.split('T')[0]
            flight['time'] = {
                'departure': departure_datetime.split('T')[1],
                'arrival': arrival_datetime.split('T')[1]
            }
            
            # 提取航线信息
            origin = segment['departureAirport']['cityName']
            destination = segment['arrivalAirport']['cityName']
            flight['route'] = f"{origin}-{destination}"
            
            # 提取航空公司信息
            if 'legs' in segment and len(segment['legs']) > 0:
                carriers = segment['legs'][0].get('carriersData', [])
                if carriers:
                    flight['airline'] = carriers[0].get('name', 'Unknown')
                    flight['aircraft'] = segment['legs'][0].get('flightInfo', {}).get('planeType', 'Unknown')
            
            # 提取价格信息
            flight['price'] = {
                'amount': total_price.get('units', 0),
                'currency': total_price.get('currencyCode', 'USD')
            }
            
            flights.append(flight)
            
        return flights

    def get_flight_info(self,token):

        conn = self.conn

        conn.request("GET", f"/api/v1/flights/getFlightDetails?token={token}&currency_code=GBP", headers=self.headers)
        # conn.request("GET", f"/api/v1/flights/getFlightDetails?token={token}", headers=self.headers)

        res = conn.getresponse()
        data = res.read()

        # print(data.decode("utf-8"))
        if res.status != 200:
            print(f"搜索请求失败: {res.status} {res.reason}")
            print(data.decode("utf-8"))
            return None
        search_results = json.loads(data.decode("utf-8"))


        return self.extract_flight_info(search_results)
        

    # def get_all_companies(self,flight_results):
    #     """
    #     获取所有航空公司
    #     """
    #     companies = []
    #     for flight in flight_results:
    #         if flight['airline'] not in companies:
    #             companies.append(flight['airline'])
    #     return companies
    # def filetr_by_company(self,flight_results,company):
    #     """
    #     根据航空公司过滤航班
    #     """
    #     return [flight for flight in flight_results if flight['airline'] == company]

    def search_flights(self, origin, destination, trip_type, date, return_date, flight_class, airline, sort):
        """
        处理航班搜索请求

        """
        #根据输入获取所有可选起点
        ori_results = self.search_destination(origin)
        #根据输入获取所有可选终点
        dest_results = self.search_destination(destination)
        #默认选择第一个
        if len(ori_results['data']) == 0 or len(dest_results) == 0:
            print("未找到相关机场")
            return None
        
        fromId = ori_results['data'][0]['id']
        toId = dest_results['data'][0]['id']        #根据输入获取所有可选起点
        flight_class = flight_class.upper()

        params = {
        "fromId": fromId,
        "toId": toId,
        "sort": sort,
        "cabinClass": flight_class,
        "departDate": date,
        "returnDate": return_date,
        "pageNo": 1,
        "adults": 1,
        "children": "0",
        "currency_code": "USD"
        }
    
        # 构建查询字符串
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        self.conn.request("GET", f"/api/v1/flights/searchFlights?{query_string}", headers=self.headers)

        #将flight_class转换为大写字母，以符合API要求
        
        # self.conn.request("GET", "/api/v1/flights/searchFlights?fromId=BOM.AIRPORT&toId=DEL.AIRPORT&pageNo=1&adults=1&children=0%2C17&sort=BEST&cabinClass=ECONOMY&currency_code=AED", headers=headers)


        # self.conn.request("GET", f"/api/v1/flights/searchFlights?fromId={fromId}&toId={toId}&sort={sort}&cabinClass={flight_class}&departDate={date}&returnDate={return_date}", headers=self.headers)
        res = self.conn.getresponse()
        data = res.read()
        if res.status != 200:
            print(f"搜索请求失败: {res.status} {res.reason}")
            print(data.decode("utf-8"))
            return None
        search_results = json.loads(data.decode("utf-8"))

        # 处理航班信息
        flight_list = []
        for offer in search_results['data']['flightOffers']:
            token = offer['token']
            info = self.get_flight_info(token)
            flight_list.append(info)
            print(info)


        
        #返回json的list
        return flight_list



# ✅ 你可以这样测试：
if __name__ == "__main__":
    api = BookAPI()
    #城市输入不能够有空格，如new york应该输入为newyork
    print(api.search_flights(
        "beijing", 
        "shanghai", 
        "oneway", 
        "2025-04-01", 
        "2025-04-15",  # 修改为合理的返回日期
        "economy", 
        "UA", 
        "BEST"
    ))