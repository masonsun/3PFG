import os
import math
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def read():
	path = './data/'
	# all filenames in data directory
	filenames = os.listdir(path)
	# open each file 
	result = {}
	for fn in filenames:
		curr = path + fn
		result[fn.split('.')[0]] = pd.read_csv(curr)
	# returns dict in which (key, val) -> (team, data)
	return result

def xaxis(sea):
	# redefines format of the seasons column
	# to be used as x-axis of plots
	return [int(s.split('-')[0]) + 1 for s in sea]

def redesign(data, cols):
	# convert to a single data frame with desired entries
	# row = seasons, col = teams
	final = pd.DataFrame()
	# insert seasons first to ensure row count is correct
	# since some teams are formed >1980
	s = xaxis(data['LAL']['Season'].tolist())
	final.insert(0, 'Season', s)
	# insert desired columns
	for key, val in data.items():
		final.insert(1, key, val[cols], allow_duplicates=False)
	return final

def edit(df):
	# set seasons as row labels
	df.set_index('Season', inplace=True)
	# reverse to make rows appear in chronological order
	df = df.iloc[::-1]
	# remove current season as still in progress
	df = df[df.index != 2016]
	# update team abbreviations
	df.rename(columns={'NJN': 'BKN', 'NOH': 'NOP'}, inplace=True)
	# sort columns in alphabetical order
	df.sort_index(axis=1, inplace=True)
	# replace missing values with the identifier 'X'
	# final.fillna('X', inplace=True)
	return df

def calcPct(data):
	# calculates the % of FGAs that are 3PAs
	# insert these values into new col called 'PCT'
	for key, df in data.items():
		p = (df['3PA'] / df['FGA'] * 100).round(1)
		df.insert(len(df.columns), 'PCT', p)
	return data

def plot(df, ylab, name):
	# override default style
	sns.set_style(
		{'axes.edgecolor': '#939393',
		'axes.linewidth': 1.0}
	)
	# plot
	plt.figure(figsize=(16,7))
	# left subplot (league wide)
	ax1 = plt.subplot(121)
	for c in df:
		plt.plot(
			df.index.values, # x-val
			df[c], # y-val
			label=c, # legend label
			alpha=0.7 # opacity
		)
	# edit legend
	plt.legend(loc=2, ncol=2)
	# axes labels
	plt.xlabel('Season', fontsize=15, labelpad=10)
	plt.ylabel(ylab, fontsize=15, labelpad=10)
	# title
	plt.title('Per Team', fontsize=18, y=1.02)
	# axes limits
	xl = [min(df.index.values), max(df.index.values)]
	yl = [0, math.ceil(max(df.max(axis=1)))+2]
	plt.xlim(xl)
	plt.ylim(yl)

	# right subplot (league avg)
	ax2 = plt.subplot(122) 
	for c in df:
		plt.scatter(
			df.index.values, # x-val
			df[c], # y-val
			color='#D3D3D3',
			alpha=0.95,
			clip_on=False, # prevents edge points being cut
		)
	# plot mean
	mean = df.mean(axis=1)
	plt.plot(df.index.values, mean)
	# plot lines that indicate changes in 3pt over seasons
	ch = {
		1994: '3-point line shortened to 22 ft',
		1997: '3-point line returned to previous length'
	}
	# place lines in alternating positions 
	i = 1
	for c in ch:
		m = float(mean.tolist()[c-xl[0]])
		delta = yl[1]*0.015
		if i % 2 != 0:
			y = [m*0.25, m]
			ty = min(y)-delta*2
		else:
			y = [m, yl[1]*0.9]
			ty = max(y)+delta
		# plot lines
		plt.plot(
			[c,c], # x-loc
			y, # y-loc
			color='#939393',
			linewidth=1)
		# plot text associated with lines
		plt.text(
			c, # x-loc
			ty, # y-loc
			ch[c], # text
			fontsize=10,
			wrap=True,
			ha='left' # alignment
		)
		i += 1 
	# sharex/sharey don't work properly
	# thus, manually declare axes labels and limits
	plt.xlabel('Season', fontsize=15, labelpad=10)
	plt.xlim(xl)
	plt.ylim(yl)
	# title
	plt.title('League average', fontsize=18, y=1.02)

	# save plots
	fp = './plots/' + name + '.pdf'
	plt.savefig(fp)

# start of script
if __name__ == '__main__':
	# retrieve all files in the data directory
	# columns required: Season, FGA, 3P, 3PA
	d = read()

	# plot 3PA of all teams + league avg
	tpa = edit(redesign(d, '3PA'))
	plot(tpa, '3-point field goals attempted per game', '3pa')

	# plot 3PM of all teams + league avg
	tpm = edit(redesign(d, '3P'))
	plot(tpm, '3-point field goals made per game', '3pm')

	# plot 3PA as a percentage of FGA of all teams + league avg
	per = edit(redesign(calcPct(d), 'PCT'))
	plot(per, 'Percentage of field goals that were 3-point shots', 'pct')

	# show plots
	plt.show()