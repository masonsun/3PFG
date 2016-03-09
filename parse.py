from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

def getHeader(s):
	return [th.getText() for th in s.findAll('tr', limit=1)[0].findAll('th')]

def getRows(s):
	final = []
	for tr in s.findAll('tbody', limit=1)[0].findAll('tr'):
		row = []
		for td in tr.findAll('td'):
			row.append(td.getText())
		final.append(row)
	return final

def toDataFrame(h, r, inaug='1979-80'):
	df = pd.DataFrame(r, columns=h)
	# remove empty columns
	empty = [i for i in range(len(h)) if h[i] == '']
	df.drop(df.columns[empty], axis=1, inplace=True)
	# remove extra column headers that appear between rows
	df = df[df.Season.notnull()]
	# remove seasons before 3PT was introduced
	try:
		idx = df[df['Season'] == inaug].index[0]
		df = df[:idx]
	except IndexError as e:
		pass
	return df

def write(d, tm):
	fp = './data/' + tm + '.csv'
	d.to_csv(fp, sep=',', index=False)

# current NBA teams
teams = (
'ATL', 'BOS', 'NJN', 'CHA', 'CHI', 'CLE',
'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND',
'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN',
'NOH', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO',
'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'
)

# start of script
for t in teams:
	# url to scrape
	url = 'http://www.basketball-reference.com/teams/' + t + '/stats_per_game.html'
	soup = BeautifulSoup(urlopen(url), 'lxml')
	# corresponding data
	header = getHeader(soup)
	rows = getRows(soup)
	# convert to data frame
	df = toDataFrame(header, rows)
	# write to csv file
	write(df, t)