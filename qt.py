#!/usr/bin/python

import time
import threading

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import pyqtSlot

import shared

class UserInterface():
	def run(self):
		
		# creating window
		self.a = QApplication(sys.argv)
		self.w = QWidget()

		# title
		self.w.setWindowTitle("Forex trade bot - EUR/USD")
		
		grid = QGridLayout()
		grid.setSpacing(10)
		# grid.addWidget(name, row, col)
		
		# financial data
		grid.addWidget(QLabel("<b>Financial data:</b>", self.w), 0, 0)
		self.sma5_text = QLabel("SMA(3): 0.0000", self.w)
		grid.addWidget(self.sma5_text, 1, 0)
		self.sma20_text = QLabel("SMA(50): 0.0000", self.w)
		grid.addWidget(self.sma20_text, 2, 0)
		self.prev_sma5_text = QLabel("Previous SMA(5): 0.0000", self.w)
		grid.addWidget(self.prev_sma5_text, 3, 0)
		self.prev_sma20_text = QLabel("Previous SMA(20): 0.0000", self.w)
		grid.addWidget(self.prev_sma20_text, 4, 0)
		
		# 1broker data
		grid.addWidget(QLabel("<b>1broker info:</b>", self.w), 0, 1)
		self.username_text = QLabel("Name:              ", self.w)
		grid.addWidget(self.username_text, 1, 1)
		self.balance_text = QLabel("Balance: 0.00000000", self.w)
		grid.addWidget(self.balance_text, 2, 1)
		self.locked_text = QLabel("Locked: 0.00000000", self.w)
		grid.addWidget(self.locked_text, 3, 1)
		self.total_balance_text = QLabel("Total: 0.00000000", self.w)
		grid.addWidget(self.total_balance_text, 4, 1)
		
		# position data
		grid.addWidget(QLabel("<b>Position:</b>", self.w), 0, 2)
		self.direction_text = QLabel("Direction: none ", self.w)
		grid.addWidget(self.direction_text, 1, 2)
		self.profit_loss_text = QLabel("P/L: 0000000000 Satoshi", self.w)
		grid.addWidget(self.profit_loss_text, 2, 2)
		
		# stats
		grid.addWidget(QLabel("<b>Stats:</b>", self.w), 0, 3)
		self.broker_fetch_count_text = QLabel("1Broker fetches: 00000", self.w)
		grid.addWidget(self.broker_fetch_count_text, 1, 3)
		self.profitloss_since_startup_text = QLabel("P/L since startup: 00000", self.w)
		grid.addWidget(self.profitloss_since_startup_text, 2, 3)
		
		# main box
		self.w.setLayout(grid)

		# run app
		self.w.show()
		
		# refresh thread
		th = threading.Thread(target=self.refresh_thread)
		th.start()
		
	def ui_exit(self):
		self.a.exec_()
		shared.running = False
		sys.exit()
		
	def refresh_thread(self):
		while shared.running == True:
			self.sma5_text.setText("SMA(5): "+str(shared.sma5))
			self.sma20_text.setText("SMA(20): "+str(shared.sma20))
			self.prev_sma5_text.setText("Previous SMA(5): "+str(shared.prev_sma5))
			self.prev_sma20_text.setText("Previous SMA(20): "+str(shared.prev_sma20))
			try:
				self.username_text.setText("Name: "+str(shared.overview['response']['username']))
				self.balance_text.setText("Balance: "+str(shared.overview['response']['balance_btc']))
				self.locked_text.setText("Locked: "+str(shared.overview['response']['positions_worth_btc']))
				self.total_balance_text.setText("Total: "+str(shared.overview['response']['net_worth_btc']))
			except:
				pass
			self.direction_text.setText("Direction: "+str(shared.position))
			self.profit_loss_text.setText("P/L: "+str(shared.profitloss)+" Satoshi")
			self.broker_fetch_count_text.setText("1Broker fetches: "+str(shared.broker_fetch_count))
			profitloss_since_startup = float(shared.balance)-float(shared.startup_balance)
			self.profitloss_since_startup_text.setText("P/L since startup: "+str(profitloss_since_startup))
				
			time.sleep(0.1)
