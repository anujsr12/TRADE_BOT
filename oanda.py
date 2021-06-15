import json
import v20
import threading
import time

class Oanda:

	def __init__(self):
		self.API = "api-fxpractice.oanda.com"	#rest api
		self.STREAM_API =  	"stream-fxpractice.oanda.com"	#stream api
		#
		#token and account id is used to access data and preform activity on certain person profile
		#
		self.ACCESS_TOKEN = "2cad9d0b4f90ab15761da499b43c26ad-06f113d3baaf47ba500924d8bc93e0fa"
		self.ACCOUNT_ID = "101-001-18827664-001" 
		
		self.api = v20.Context(hostname = self.API, token = self.ACCESS_TOKEN, port = 443)
		self.stream_api = v20.Context(hostname = self.STREAM_API, token = self.ACCESS_TOKEN, port = 443)
	#
	#log_dump use to record log of  whenever a sell or buy markert order is placed
	#
	def log_dump(self, response, order_type, instruments):
		with open("sell_and_buy_log.txt", "a+") as text:
			text.writelines("market_order_type : "+ order_type +"\n")
			text.writelines("instruments : "+ instruments+ "\n")
			for key, val in json.loads(response.body["orderCreateTransaction"].json()).items():
				if str(key) == "id" or str(key) == "time" or str(key) == "requestID" or str(key) =="units" or str(key) =="userID":
					text.writelines(str(key)+" : "+str(val) +"\n")
			at_price = json.loads(response.body["orderFillTransaction"].json())["price"]
			text.writelines("at_price_per_unit : "+ str(at_price)+ "\n")
			text.writelines("--------------------------------------------------\n\n\n")
	#
	#sell get called when price range get bellow then orb range
	#
	def sell(self, instruments):
		response = self.api.order.market(accountID = self.ACCOUNT_ID, instrument = instruments , units= -10)
		self.log_dump(response, "sell", instruments)
	#
	#buy get called when price get higher then orb range	
	#
	def buy(self, instruments):
		response = self.api.order.market(accountID = self.ACCOUNT_ID, instrument = instruments , units= 10)
		self.log_dump(response, "buy", instruments)
	#
	#orb is used to set orb range of "EUR_USD"/"AUD_USD"/"GBP_USD"
	#
	def orb(self, instruments):
		# t refer to time it function is decided to run for 15 min and return orb range
		t = 900
		print(instruments)
		response = self.api.pricing.get(accountID = self.ACCOUNT_ID, instruments = instruments)
		
		closeoutAsk = json.loads(response.body["prices"][0].json())["closeoutAsk"]
		orb_range=[closeoutAsk,closeoutAsk]
		while t:
			response = self.api.pricing.get(accountID = self.ACCOUNT_ID, instruments = instruments)
			closeoutAsk = json.loads(response.body["prices"][0].json())["closeoutAsk"]
			if closeoutAsk > orb_range[1]:
				orb_range[1] = closeoutAsk
			if closeoutAsk < orb_range[0]:
				orb_range[0] = closeoutAsk
			time.sleep(1)
			t-= 1
		return orb_range
	#
	#monitor is consist of an infinite loop at every 30sec it checks the pricing of instruments and send signal to buy or sell as per orb market strategy
	#
	def monitor(self, instruments, orb_range):
		while True:
			response = self.api.pricing.get(accountID = self.ACCOUNT_ID, instruments = instruments)
			closeoutAsk = json.loads(response.body["prices"][0].json())["closeoutAsk"]
			if closeoutAsk >= int(orb_range[1]):
				self.buy(instruments)	
			elif closeoutAsk <= int(orb_range[0]):
				self.sell(instruments)
			time.sleep(30)



	def run(self):
		orb_range = []
		instruments = ["EUR_USD", "AUD_USD", "GBP_USD"]
		# in after 15 min gap in each instruments there orb range will be set accordingly
		for ls in instruments:
			orb_range.append(self.orb(ls))

		try:
			if __name__ == "__main__":
			    # creating thread
				# t1 thread is for EUR_USD
				t1 = threading.Thread(target= self.monitor, args=(instruments[0],orb_range[0]))
				# t2 thread is for AUD_USD
				t2 = threading.Thread(target= self.monitor, args=(instruments[1],orb_range[1]))
				# t3 thread is for GBP_USD
				t3 = threading.Thread(target= self.monitor, args=(instruments[2],orb_range[2]))
				t1.start()
				t2.start()
				t3.start()
				t1.join()
				t2.join()
				t3.join()

		except KeyboardInterrupt:
			print("stoped")

# create object of class Oanda
run_oanda = Oanda()
# to run the main program
run_oanda.run()
