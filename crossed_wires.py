#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from random import choice
import sys
from math import floor

class Light:
	def __init__(self):
		self.on = False

	def turn_on(self):
		self.on = True

	def turn_off(self):
		self.on = False

	def toggle(self):
		self.on = not self.on

	def next(self):
		pass

	def __repr__(self):
		return "💡" if self.on else "🌑"

class Switch:
	def __init__(self):
		self.on = False
		self.toggled = False

	def toggle(self):
		self.on = not self.on
		self.toggled = True

	def next(self):
		self.toggled = False

	def __repr__(self):
		return "✓" if self.on else "✗"

class WiringRule:
	def __init__(self, rule='switch_on'):
		self.rule = rule
		self.revealed = False
		self.rules = {
			"corresponding_switch_on": (self.switch, 'corresponding', 'on'),
			"corresponding_switch_off": (self.switch, 'corresponding', 'off'),
			"corresponding_switch_toggled": (self.switch, 'corresponding', 'toggled'),
			"left_neighbour_switch_on": (self.switch, 'left', 'on'),
			"right_neighbour_switch_on": (self.switch, 'right', 'on'),
			"both_neighbouring_switches_on": (self.switch, 'both', 'on'),
			"either_neighbouring_switch_on": (self.switch, 'either', 'on'),
			"left_neighbour_switch_off": (self.switch, 'left', 'off'),
			"right_neighbour_switch_off": (self.switch, 'right', 'off'),
			"both_neighbouring_switches_off": (self.switch, 'both', 'off'),
			"either_neighbouring_switch_off": (self.switch, 'either', 'off'),
			"left_neighbour_switch_toggled": (self.switch, 'left', 'toggled'),
			"right_neighbour_switch_toggled": (self.switch, 'right', 'toggled'),
			"both_neighbouring_switches_toggled": (self.switch, 'both', 'toggled'),
			"either_neighbouring_switch_toggled": (self.switch, 'either', 'toggled'),
			"this_light_toggles_itself": (self.light, 'toggle_self'),
			"this_light_is_always_on": (self.light, 'always_on'),
			"left_neighbour_light_on": (self.light, 'left'),
			"right_neighbour_light_on": (self.light, 'right'),
			"both_neighbouring_light_on": (self.light, 'both'),
			"either_neighbouring_light_on": (self.light, 'either'),
		}
		if self.rule == 'random':
			self.rule = choice(list(self.rules.keys()))

	def reveal(self):
		self.revealed = True

	def __repr__(self):
		return "?" if not self.revealed else "🂠"

	def apply(self, board, row):
		"""
		Applies this rule to the board, for the given row.
		"""
		light = board.rows[row][0]
		switch = board.rows[row][1]
		lr = row-1 if row-1>=0 else board.num_rows-1
		rr = row+1 if row+1<board.num_rows else 0
		left_light = board.rows[lr][0]
		left_switch = board.rows[lr][1]
		right_light = board.rows[rr][0]
		right_switch = board.rows[rr][1]

		rule = self.rules[self.rule]
		rule[0](light, switch, left_light, left_switch, right_light, right_switch, *rule[1:])

		return board

	def light(self, light, switch, left_light, left_switch, right_light, right_switch, what):
		if what in ('left', 'right'):
			what_light = left_light if what == 'left' else right_light
			what_true = True if what_light.on else False
		elif what == 'both':
			what_true = True if left_light.on and right_light.on else False
		elif what == 'either':
			what_true = True if left_light.on or right_light.on else False
		elif what == 'toggle_self':
			what_true = True if not light.on else False
		elif what == 'always_on':
			what_true = True
		else:	
			raise RuntimeError("Invalid 'what' operand in WiringRule.light")
		light.turn_on() if what_true else light.turn_off()

	def switch(self, light, switch, left_light, left_switch, right_light, right_switch, which, how):
		if which in ('corresponding', 'left', 'right'):
			which_switch = switch if which=='corresponding' else left_switch if which=='left' else right_switch
			how_true = True if (
				how=='on' and which_switch.on or
				how=='off' and not which_switch.on or
				how=='toggled' and which_switch.toggled
			) else False
		elif which == 'both':
			how_true = True if (
				how=='on' and (left_switch.on and right_switch.on) or
				how=='off' and (not left_switch.on and not right_switch.on) or
				how=='toggled' and (left_switch.toggled and right_switch.toggled)
			) else False
		elif which == 'either':
			how_true = True if (
				how=='on' and (left_switch.on or right_switch.on) or
				how=='off' and (not left_switch.on or not right_switch.on) or
				how=='toggled' and (left_switch.toggled or right_switch.toggled)
			) else False
		else:
			raise RuntimeError("Invalid 'which' operand in WiringRule.switch")
		light.turn_on() if how_true else light.turn_off()

class Board:
	def __init__(self, num_rows=4):
		self.rows = {}
		self.num_rows = num_rows
		if self.num_rows<3:
			raise RuntimeError("Cannot play with fewer than three rows of lights.")
		self.rules = []
		for i in range(self.num_rows):
			self.rules.append(WiringRule('random'))
			self.rows[i] = [Light(), Switch()]

		# Ensure the wiring rules do not result in more than half the lights on to start with.
		while True:
			self.next()
			if self.num_lights_on() <= floor(self.num_rows/2):
				break
			for i in range(self.num_rows):
				self.rules[i] = WiringRule('random')


		self.is_impossible = self.test()

	def num_lights_on(self):
		return sum([1 if r[0].on else 0 for r in self.rows.values()])

	def test(self):
		"""
		Checks whether this board is possible or not, by applying some heuristics.
		"""
		for row in range(self.num_rows):
			lr = row-1 if row-1>=0 else self.num_rows-1
			rr = row+1 if row+1<self.num_rows else 0
			if self.rules[row].rule == 'corresponding_switch_off' and (
				self.rules[lr].rule == 'right_neighbour_switch_on' or 
				self.rules[rr].rule == 'left_neighbour_switch_on' or 
				self.rules[lr].rule == 'both_neighbouring_switches_on' or
				self.rules[rr].rule == 'both_neighbouring_switches_on'):
				return True
			if self.rules[row].rule == 'corresponding_switch_on' and (
				self.rules[lr].rule == 'right_neighbour_switch_off' or 
				self.rules[rr].rule == 'left_neighbour_switch_off' or 
				self.rules[lr].rule == 'both_neighbouring_switches_off' or
				self.rules[rr].rule == 'both_neighbouring_switches_off'):
				return True
		return False

	def toggle(self, row):
		"""
		Toggles the switch on the given row.
		"""
		try:
			self.rows[row][1].toggle()
		except KeyError:
			raise

	def next(self):
		changed = 1
		while(changed > 0 and changed < 10):  # While rule application is still changing the board, re-apply the rules left to right.
			board_prior = "%r" % (self, )
			for i in range(self.num_rows):
				self.board = self.rules[i].apply(self, i)  # Apply this rule to the board.
			board_post = "%r" % (self, )
			changed = changed+1 if board_prior != board_post else 0
		for i in range(self.num_rows):  # Call next() on the lights and switches too.
			self.rows[i][0].next()
			self.rows[i][1].next()

	def solved(self):
		for row in self.rows.values():
			if not row[0].on:
				return False
		return True

	def __repr__(self):
		output = "Rules:\t\t"
		for i in range(self.num_rows):
			output += "%r\t" % (self.rules[i],)
		output += "\r\nLights:\t\t"
		for i in range(self.num_rows):
			output += "%r\t" % (self.rows[i][0],)
		output += "\r\nSwitches:\t"
		for i in range(self.num_rows):
			output += "%r\t" % (self.rows[i][1],)
		return output

	def show(self):
		print("%r" % (self,))

class Game():
	def __init__(self, num_rows=4):
		try:
			self.board = Board(num_rows=num_rows)
		except RuntimeError as e:
			print(e)
			sys.exit(0)
		self.cost_per_row = 500
		self.money = self.cost_per_row * self.board.num_rows
		self.cost_per_turn = 100
		self.revealed_rules = []

	def console_play(self):
		print("----------------------------------")
		print("Crossed-Wires, a game by Tom Allen")
		print("----------------------------------\r\n")
		print("A dodgy electrician has wired up each of your lights according to some strange logic, "
			"but you're in the dark about it. Turn all the lights on in as few turns as you can!")
		while not self.board.solved() and self.money > 0:
			print("\r\n")
			self.board.show()
			print("You have $%d." % (self.money,))
			if(self.revealed_rules):
				print("You have revealed %d rule%s:" % (len(self.revealed_rules),'s' if len(self.revealed_rules)>1 else ''))
				for revealed_row in self.revealed_rules:
					print("\tRow %d's wiring rule is '%s'" % (revealed_row, self.board.rules[revealed_row-1].rule,))
			switches = input("Type R to pay $500 to reveal a wiring rule,\r\n"
				"Type I to declare this wiring to be impossible, or\r\n"
				"Choose which switches should be toggled? (eg: '1,3,4'): ")
			if switches.lower() == 'r':
				if self.money < self.cost_per_row:
					print("You don't have enough money to reveal a wiring rule.")
					continue
				else:
					self.money -= self.cost_per_row
					available_reveals = list(set(range(1,self.board.num_rows+1))-set(self.revealed_rules))
					while True:
						revealed_row = input('Which row do you wish to reveal? (%s): ' % (','.join('%s' % i for i in available_reveals)))
						try:
							revealed_row = int(revealed_row)
						except (ValueError, TypeError):
							continue
						if revealed_row in self.revealed_rules or revealed_row < 1 or revealed_row > self.board.num_rows:
							continue
						print("Row %d's wiring rule is '%s'" % (revealed_row, self.board.rules[revealed_row-1].rule,))
						self.revealed_rules.append(revealed_row)
						self.revealed_rules.sort()
						self.board.rules[revealed_row-1].reveal()
						break
					continue
			elif switches.lower() == 'i':
				while True:
					yn = input("Are you sure? You will immediately lose the game if you are incorrect, but win if correct! (Y/N): ")
					if yn.lower() == 'y':
						if self.board.is_impossible:
							print("You win! This wiring setup is indeed impossible!")
						else:
							print("Unfortunately, no one ever programmed this console with the ability to comprehensively "
								"work out whether it is possible or not. It passes the obvious tests, so it *probably* is "
								"possible. Here are the rules; work it out for yourself, and if you're right - you win!")
						for i, rule in enumerate(self.board.rules):
							print("%d: %s" % (i+1, rule.rule,))
						sys.exit(1)
					elif yn.lower() == 'n':
						break
					else:
						continue
				continue
			try:
				switches = switches.split(',')
				switches = list(map(int, switches))
				if any(i>self.board.num_rows for i in switches):
					print("Invalid row number. The maximum is %d." % (self.board.num_rows, ))	
					continue
			except TypeError:
				print("Invalid format. Please list the rows whose switches should be toggled, separated by commas. (eg: '1,3,4')")
				continue
			except ValueError:  # Ignore empty input - it means zero were toggled.
				switches = []
			self.money -= self.cost_per_turn
			for switch in switches:
				self.board.toggle(switch-1)
			self.board.next()

		# Out of main loop, so game is over.
		self.board.show()
		if self.money > 0:
			print("All lights are on, and you still have $%d! The rules were:" % (self.money, ))
		else:
			print("The dodgy electrician has taken all your money, and you're still in the dark... The rules were:")
		for i, rule in enumerate(self.board.rules):
			print("\t%d: %s" % (i+1, rule.rule,))
		if self.board.is_impossible:
			print("But you were duped - this wiring setup is IMPOSSIBLE to solve!")


if __name__ == "__main__":
	num_rows = 4
	if len(sys.argv) > 1:
		try:
			num_rows = int(sys.argv[1])
		except ValueError:
			pass
	game = Game(num_rows)
	game.console_play()
