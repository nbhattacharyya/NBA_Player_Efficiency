import pandas as pd 
import urllib.request
from html_table_parser import HTMLTableParser
from pprint import pprint
import time

# FIRST PART: Getting PER Data 
# Reads contents from webpage
def get_contents_url(url):
	req = urllib.request.Request(url=url)
	f = urllib.request.urlopen(req)
	return f.read()

#------------------- Get PER Table and append to DF --------------------------------------#
xhtml = get_contents_url('http://insider.espn.com/nba/hollinger/statistics/_/year/2020').decode('utf-8')
p = HTMLTableParser()
p.feed(xhtml)
df = pd.DataFrame(p.tables[0])
new_header = df.iloc[1]
df = df[2:]
df.columns = new_header
# ------------------------------------------------------------------------ #

# ------------------- Append Pages 2-8 in DF -------------------------------------- #
for i in range(2, 9):
	url = 'http://insider.espn.com/nba/hollinger/statistics/_/page/{}/year/2020'.format(i)
	xhtml_temp = get_contents_url(url).decode('utf-8')
	p_temp = HTMLTableParser()
	p_temp.feed(xhtml_temp)
	df_temp = pd.DataFrame(p_temp.tables[0])
	new_header_temp = df_temp.iloc[1]
	df_temp = df_temp[2:]
	df_temp.columns = new_header_temp

	df = df.append(df_temp, ignore_index=True)
# ---------------------------------------------------------------------------- #

# --------------- Cleaning ---------------- #
df_per = df[["PLAYER", "PER", "MPG"]]
df_per = df_per[df_per.PLAYER != "PLAYER"]
df_per = df_per[df_per.PER != "PER"]
df_per['PLAYER'] = df_per['PLAYER'].str.split(',').str[0]
# ----------------------------------------- #





#SECOND PART: Getting Salary data
#------------------- Get Salary Table and append to DF --------------------------------------#
xhtml = get_contents_url('http://www.espn.com/nba/salaries/_/year/2020').decode('utf-8')
p = HTMLTableParser()
p.feed(xhtml)
df_two = pd.DataFrame(p.tables[0])
new_header = df_two.iloc[0]
df_two = df_two[1:]
df_two.columns = new_header
# ------------------------------------------------------------------------ #

# ------------------- Append Pages 2-14 in DF -------------------------------------- #
for i in range(2, 15):
	url = 'http://www.espn.com/nba/salaries/_/year/2020/page/{}'.format(i)
	xhtml_temp = get_contents_url(url).decode('utf-8')
	p_temp = HTMLTableParser()
	p_temp.feed(xhtml_temp)
	df_temp = pd.DataFrame(p_temp.tables[0])
	new_header_temp = df_temp.iloc[0]
	df_temp = df_temp[1:]
	df_temp.columns = new_header_temp
	#print(df_temp.head(5))
	df_two = df_two.append(df_temp, ignore_index=True)
# ---------------------------------------------------------------------------- #

# --------------- Cleaning ---------------- #
df_salary = df_two[["NAME", "TEAM", "SALARY"]]
df_salary = df_salary.rename(columns={'NAME' : 'PLAYER'}) 
df_salary = df_salary[df_salary.PLAYER != "NAME"]
df_salary = df_salary[df_salary.TEAM != "TEAM"]
df_salary['PLAYER'] = df_salary['PLAYER'].str.split(',').str[0]
# ----------------------------------------- #


# ------------------ Merging Dataftames and Cleaning ------------------- #
df_final = pd.merge(df_per, df_salary, on=['PLAYER'])
df_final['SALARY'] = df_final['SALARY'].str.replace('$', '')
df_final['SALARY'] = df_final['SALARY'].str.replace(',', '')
cols = ['PER', 'SALARY', 'MPG']
df_final[cols] = df_final[cols].apply(pd.to_numeric, errors='coerce')
#print(df_final.head(10))
# -------------------------------------------------------------------- #


# -------------- Calculation --------------- #
df_final = df_final[df_final.MPG > 25]
df_final['PER_per_Dollar'] = (df_final['PER'] / df_final['SALARY']) * 1000000
print(df_final.nlargest(5, 'PER_per_Dollar'))
